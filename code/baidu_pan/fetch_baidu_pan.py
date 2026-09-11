#!/usr/bin/env python3
# 功能：在云服务器上反复从百度网盘开放平台取数。
# 一次浏览器授权拿到 refresh_token 后，由本脚本按需刷新 access_token、
# 仅同步 /apps/{应用名}（网盘里显示为 /我的应用数据/{应用名}），并做增量下载。
# 更新时间：2026-09-11：首次提交。支持授权码换 token、refresh_token 一次性轮换、
# 应用目录列表与增量同步；密钥写入独立 token.json，不入库。

"""云服务器百度网盘反复取数。

必须使用授权码模式（response_type=code），不要用网页里直接吐 access_token 的简化模式。
简化模式过期后无法刷新，云上无法长期跑。

一次性（本机浏览器）：
  python3 fetch_baidu_pan.py init-config
  # 编辑 config.json，填 AppId / AppKey / SecretKey / 应用名
  python3 fetch_baidu_pan.py auth-url
  # 浏览器打开打印的链接，同意授权，把页面上的 code 复制回来
  python3 fetch_baidu_pan.py exchange --code 粘贴的CODE

日常（云服务器 cron，每天一次即可）：
  python3 fetch_baidu_pan.py sync --local /data/baidu_pan

官方限制：新应用只能读写 /apps/{应用名}。请把要取的文件先拷到
「我的应用数据/{应用名}」。refresh_token 用一次就作废，脚本会立刻写回新值。
同一时刻不要跑两个实例，否则会把对方的 refresh_token 作废。
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

UA = "pan.baidu.com"
AUTHORIZE_URL = "https://openapi.baidu.com/oauth/2.0/authorize"
TOKEN_URL = "https://openapi.baidu.com/oauth/2.0/token"
FILE_API = "https://pan.baidu.com/rest/2.0/xpan/file"
MULTIMEDIA_API = "https://pan.baidu.com/rest/2.0/xpan/multimedia"
UINFO_API = "https://pan.baidu.com/rest/2.0/xpan/nas"
REFRESH_SKEW_SEC = 24 * 3600
HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG = HERE / "config.json"
DEFAULT_TOKEN = HERE / "token.json"


class PanError(RuntimeError):
    """百度网盘接口或本地配置错误。"""


def _http_get(url: str, params: dict[str, Any] | None = None, timeout: int = 60) -> tuple[int, bytes, str]:
    if params:
        url = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read(), resp.headers.get("Content-Type", "")
    except urllib.error.HTTPError as exc:
        body = exc.read()
        raise PanError(f"HTTP {exc.code}: {body[:500]!r}") from exc


def _http_get_json(url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    _status, body, _ctype = _http_get(url, params)
    try:
        data = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise PanError(f"接口返回不是 JSON: {body[:300]!r}") from exc
    return data


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise PanError(f"找不到文件: {path}")
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def dump_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    os.replace(tmp, path)
    os.chmod(path, 0o600)


def app_root(app_name: str) -> str:
    name = app_name.strip().strip("/")
    if not name:
        raise PanError("config.app_name 不能为空，必须与开放平台应用名称一致")
    return f"/apps/{name}"


def assert_under_app(path: str, app_name: str) -> str:
    root = app_root(app_name)
    normalized = "/" + path.strip().strip("/")
    if normalized != root and not normalized.startswith(root + "/"):
        raise PanError(
            f"官方接口只能访问 {root}（网盘显示为 /我的应用数据/{app_name}），"
            f"收到路径: {path}"
        )
    return normalized


def build_auth_url(app_key: str, redirect_uri: str = "oob") -> str:
    query = urllib.parse.urlencode(
        {
            "response_type": "code",
            "client_id": app_key,
            "redirect_uri": redirect_uri,
            "scope": "basic,netdisk",
            "display": "page",
        }
    )
    return f"{AUTHORIZE_URL}?{query}"


def cmd_init_config(config_path: Path) -> None:
    if config_path.exists():
        raise PanError(f"已存在 {config_path}，避免覆盖。若要重建请先自行删除。")
    example = HERE / "config.example.json"
    dump_json(config_path, load_json(example))
    os.chmod(config_path, 0o600)
    print(f"已写入 {config_path}，请填入 AppId / AppKey / SecretKey / 应用名。")


def cmd_auth_url(config: dict[str, Any]) -> None:
    app_key = config.get("app_key") or ""
    if not app_key or "替换" in str(app_key):
        raise PanError("请先在 config.json 填入真实 AppKey")
    url = build_auth_url(app_key, config.get("redirect_uri") or "oob")
    print("用浏览器打开下面链接，登录百度并点同意：")
    print(url)
    print()
    print("授权后页面会给出 code（或 URL 参数 ?code=）。10 分钟内执行：")
    print("  python3 fetch_baidu_pan.py exchange --code 你的CODE")


def save_token_response(
    token_path: Path,
    config: dict[str, Any],
    data: dict[str, Any],
) -> dict[str, Any]:
    if "access_token" not in data or "refresh_token" not in data:
        raise PanError(f"换票失败: {data}")
    record = {
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "expires_at": int(time.time()) + int(data.get("expires_in") or 2592000),
        "scope": data.get("scope", ""),
        "app_id": config.get("app_id", ""),
        "app_key": config["app_key"],
        "secret_key": config["secret_key"],
        "app_name": config["app_name"],
        "redirect_uri": config.get("redirect_uri") or "oob",
        "updated_at": int(time.time()),
    }
    dump_json(token_path, record)
    return record


def cmd_exchange(config: dict[str, Any], token_path: Path, code: str) -> None:
    data = _http_get_json(
        TOKEN_URL,
        {
            "grant_type": "authorization_code",
            "code": code.strip(),
            "client_id": config["app_key"],
            "client_secret": config["secret_key"],
            "redirect_uri": config.get("redirect_uri") or "oob",
        },
    )
    save_token_response(token_path, config, data)
    print(f"授权成功，token 已写入 {token_path}（chmod 600）。")
    print("把 config.json 和 token.json 拷到云服务器同一目录，之后只需跑 sync。")


def refresh_access_token(token: dict[str, Any], token_path: Path) -> dict[str, Any]:
    data = _http_get_json(
        TOKEN_URL,
        {
            "grant_type": "refresh_token",
            "refresh_token": token["refresh_token"],
            "client_id": token["app_key"],
            "client_secret": token["secret_key"],
        },
    )
    if "error" in data or "access_token" not in data:
        raise PanError(
            "刷新失败，旧 refresh_token 可能已作废，需要重新 auth-url + exchange。"
            f" 原始返回: {data}"
        )
    merged = save_token_response(token_path, token, data)
    print("已刷新 access_token，并写回新的 refresh_token。")
    return merged


def ensure_access_token(token_path: Path, force: bool = False) -> dict[str, Any]:
    token = load_json(token_path)
    expires_at = int(token.get("expires_at") or 0)
    if force or expires_at - time.time() < REFRESH_SKEW_SEC:
        token = refresh_access_token(token, token_path)
    return token


def with_lock(lock_path: Path):
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fh = lock_path.open("a+", encoding="utf-8")
    try:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        fh.close()
        raise PanError("已有取数进程在跑。不要并行刷新 refresh_token。") from exc
    return fh


def cmd_whoami(token_path: Path) -> None:
    token = ensure_access_token(token_path)
    data = _http_get_json(UINFO_API, {"method": "uinfo", "access_token": token["access_token"]})
    print(json.dumps(data, ensure_ascii=False, indent=2))


def list_all_files(access_token: str, path: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    start = 0
    limit = 1000
    while True:
        data = _http_get_json(
            MULTIMEDIA_API,
            {
                "method": "listall",
                "access_token": access_token,
                "path": path,
                "recursion": 1,
                "start": start,
                "limit": limit,
                "web": 1,
            },
        )
        errno = data.get("errno", 0)
        if errno not in (0, None):
            raise PanError(f"listall 失败 errno={errno}: {data}")
        batch = data.get("list") or []
        items.extend(batch)
        if not data.get("has_more"):
            break
        start = int(data.get("cursor") or (start + len(batch)))
        if not batch:
            break
    return items


def filemetas(access_token: str, fsids: list[int]) -> list[dict[str, Any]]:
    if not fsids:
        return []
    out: list[dict[str, Any]] = []
    for i in range(0, len(fsids), 100):
        chunk = fsids[i : i + 100]
        data = _http_get_json(
            MULTIMEDIA_API,
            {
                "method": "filemetas",
                "access_token": access_token,
                "fsids": json.dumps(chunk),
                "dlink": 1,
            },
        )
        errno = data.get("errno", 0)
        if errno not in (0, None):
            raise PanError(f"filemetas 失败 errno={errno}: {data}")
        out.extend(data.get("list") or [])
    return out


def download_dlink(dlink: str, access_token: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    url = dlink
    sep = "&" if "?" in url else "?"
    url = f"{url}{sep}access_token={urllib.parse.quote(access_token)}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler())
    with opener.open(req, timeout=300) as resp, tmp.open("wb") as fh:
        while True:
            chunk = resp.read(1024 * 1024)
            if not chunk:
                break
            fh.write(chunk)
    os.replace(tmp, dest)


def cmd_list(token_path: Path, remote: str | None) -> None:
    token = ensure_access_token(token_path)
    path = assert_under_app(remote or app_root(token["app_name"]), token["app_name"])
    items = list_all_files(token["access_token"], path)
    files = [x for x in items if not x.get("isdir")]
    print(f"{path} 共 {len(files)} 个文件：")
    for item in files:
        print(f"{item.get('size', 0):>12}  {item.get('path')}")


def cmd_sync(token_path: Path, local_dir: Path, remote: str | None) -> None:
    token = ensure_access_token(token_path)
    path = assert_under_app(remote or app_root(token["app_name"]), token["app_name"])
    root = app_root(token["app_name"])
    items = list_all_files(token["access_token"], path)
    files = [x for x in items if not int(x.get("isdir") or 0)]
    if not files:
        print(f"{path} 下没有文件。请先把数据拷到网盘「我的应用数据/{token['app_name']}」。")
        return

    fsids = [int(x["fs_id"]) for x in files if x.get("fs_id")]
    metas = {int(m["fs_id"]): m for m in filemetas(token["access_token"], fsids)}
    downloaded = 0
    skipped = 0
    for item in files:
        remote_path = str(item.get("path") or "")
        rel = remote_path[len(root) :].lstrip("/") if remote_path.startswith(root) else Path(remote_path).name
        dest = local_dir / rel
        size = int(item.get("size") or 0)
        if dest.exists() and dest.stat().st_size == size:
            skipped += 1
            continue
        meta = metas.get(int(item["fs_id"]))
        dlink = (meta or {}).get("dlink")
        if not dlink:
            raise PanError(f"没有下载地址: {remote_path}")
        print(f"下载 {remote_path} -> {dest}")
        download_dlink(dlink, token["access_token"], dest)
        downloaded += 1
    print(f"完成：新增/更新 {downloaded} 个，跳过未变化 {skipped} 个。输出目录 {local_dir}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="百度网盘云服务器反复取数")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="配置文件，默认 ./config.json")
    parser.add_argument("--token", default=str(DEFAULT_TOKEN), help="token 文件，默认 ./token.json")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init-config", help="生成 config.json 模板")
    sub.add_parser("auth-url", help="打印授权链接")
    p_ex = sub.add_parser("exchange", help="用浏览器拿到的 code 换长期 token")
    p_ex.add_argument("--code", required=True)
    sub.add_parser("refresh", help="强制刷新 access_token")
    sub.add_parser("whoami", help="验证 token 是否有效")
    p_list = sub.add_parser("list", help="列出应用目录文件")
    p_list.add_argument("--remote", help="远程目录，默认 /apps/{应用名}")
    p_sync = sub.add_parser("sync", help="增量同步到本地目录")
    p_sync.add_argument("--local", default="./data", help="本机/云服务器保存目录")
    p_sync.add_argument("--remote", help="远程目录，默认 /apps/{应用名}")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config_path = Path(args.config)
    token_path = Path(args.token)
    lock_fh = None
    try:
        if args.cmd in {"refresh", "whoami", "list", "sync", "exchange"}:
            lock_fh = with_lock(token_path.with_suffix(".lock"))
        if args.cmd == "init-config":
            cmd_init_config(config_path)
        elif args.cmd == "auth-url":
            cmd_auth_url(load_json(config_path))
        elif args.cmd == "exchange":
            cmd_exchange(load_json(config_path), token_path, args.code)
        elif args.cmd == "refresh":
            ensure_access_token(token_path, force=True)
        elif args.cmd == "whoami":
            cmd_whoami(token_path)
        elif args.cmd == "list":
            cmd_list(token_path, args.remote)
        elif args.cmd == "sync":
            cmd_sync(token_path, Path(args.local), args.remote)
        return 0
    except PanError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1
    finally:
        if lock_fh is not None:
            fcntl.flock(lock_fh.fileno(), fcntl.LOCK_UN)
            lock_fh.close()


if __name__ == "__main__":
    sys.exit(main())
