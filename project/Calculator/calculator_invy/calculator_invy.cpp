#include "calculator_invy.h"
#include "ui_calculator_invy.h"
#include<string.h>
calculator_invy::calculator_invy(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::calculator_invy)
{
    ui->setupUi(this);

}

calculator_invy::~calculator_invy()
{
    delete ui;
}

float temp1=-1;
int pos=0;

void calculator_invy ::addNum(int num)
{
    QString Result=ui->lineEdit->text();

    QString num_str = QString::number(num, 10);
    Result=Result+num_str;
    ui->lineEdit->setText(Result);
}

void calculator_invy::on_pushButton_clicked()
{
  QString Result="";
  ui->lineEdit->setText(Result);
  pos=0;
  temp1=0;
}


void calculator_invy::on_pushButton_2_clicked()
{
    addNum(7);
}


void calculator_invy::on_pushButton_3_clicked()
{
    addNum(8);
}

void calculator_invy::on_pushButton_4_clicked()
{
    addNum(9);
}


void calculator_invy::on_pushButton_5_clicked()
{
    addNum(4);
}

void calculator_invy::on_pushButton_6_clicked()
{
    addNum(5);
}

void calculator_invy::on_pushButton_7_clicked()
{
    addNum(6);
}


void calculator_invy::on_pushButton_8_clicked()
{
    addNum(1);
}

void calculator_invy::on_pushButton_9_clicked()
{
    addNum(2);
}


void calculator_invy::on_pushButton_10_clicked()
{
    addNum(3);
}


void calculator_invy::on_pushButton_12_clicked()
{
    addNum(0);
}

void calculator_invy::on_pushButton_11_clicked()
{
    QString Result=ui->lineEdit->text();
    Result=Result+".";
    ui->lineEdit->setText(Result);
}

void calculator_invy::on_pushButton_14_clicked()
{
    pos=1;
    QString Result=ui->lineEdit->text();
    temp1=Result.toDouble();
    Result="";
    ui->lineEdit->setText(Result);
}


void calculator_invy::on_pushButton_15_clicked()
{
    pos=2;
    QString Result=ui->lineEdit->text();
    temp1=Result.toDouble();
    Result="";
    ui->lineEdit->setText(Result);
}

void calculator_invy::on_pushButton_16_clicked()
{
    pos=3;
    QString Result=ui->lineEdit->text();
    temp1=Result.toDouble();
    Result="";
    ui->lineEdit->setText(Result);
}

void calculator_invy::on_pushButton_17_clicked()
{
    pos=4;
    QString Result=ui->lineEdit->text();
    temp1=Result.toDouble();
    Result="";
    ui->lineEdit->setText(Result);
}


void calculator_invy::on_pushButton_13_clicked()
{
    QString Result=ui->lineEdit->text();
    float temp2=Result.toDouble();
    float zz;
    switch(pos)
    {
    case 1:
        zz=temp1+temp2;
        Result=QString("%1").arg(zz);
        ui->lineEdit->setText(Result);
        break;
    case 2:
        zz=temp1-temp2;
        Result=QString("%1").arg(zz);
        ui->lineEdit->setText(Result);
        break;
    case 3:
        zz=temp1*temp2;
        Result=QString("%1").arg(zz);
        ui->lineEdit->setText(Result);
        break;
    case 4:
        zz=temp1/temp2;
        Result=QString("%1").arg(zz);
        ui->lineEdit->setText(Result);
        break;
    }
}


