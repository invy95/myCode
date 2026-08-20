# 哼唱转简谱 `hum2jianpu`

把突然哼出来的旋律录音，自动翻译成 1234 简谱，并顺带导出 MIDI。

不装国内那些容易被标成「垃圾程序」的客户端，只依赖 Python +（可选）ffmpeg。

## 准备

```bash
pip install -r requirements.txt
```

- 纯 `wav` 可直接用
- `mp3` / `m4a` / `aac` 需要系统已安装 [ffmpeg](https://ffmpeg.org/)

## 用法

```bash
# 单个录音 → 同目录生成 .jianpu.txt 和 .mid
python hum2jianpu.py idea.wav

# 指定调号和速度（更稳）
python hum2jianpu.py idea.m4a --key C --bpm 96

# 整个文件夹批量转
python hum2jianpu.py ./recordings

# 监视文件夹：手机传到这个目录就自动出谱
python hum2jianpu.py --watch ./inbox

# 自检
python hum2jianpu.py --self-test
```

输出示例：

```
1=C  4/4  ♩=90
1 2 3 4 | 5 6 7 1' |
```

- `'` 表示高八度，`,` 表示低八度
- `/` 表示八分音符，`1 -` 表示二分音符
- `0` 是休止符
- `.mid` 可拖进 MuseScore 继续改谱

## 录音建议

- 用「啦 / 嘟」清唱，不要用「嗯」
- 尽量对着麦克风、环境安静、一次 8～16 小节
- 有节拍器再哼，节奏会规整很多

识别不会百分百准，把输出当草稿，不对的音在文本或 MuseScore 里改一下即可。
