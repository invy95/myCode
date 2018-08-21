#ifndef CALCULATOR_INVY_H
#define CALCULATOR_INVY_H

#include <QMainWindow>

namespace Ui {
class calculator_invy;
}

class calculator_invy : public QMainWindow
{
    Q_OBJECT


public:
    explicit calculator_invy(QWidget *parent = 0);
    ~calculator_invy();
    void addNum(int num);
    QString Result;
    int pos;
    float temp1;
    float temp2;
private slots:

    void on_pushButton_clicked();

    void on_pushButton_2_clicked();

    void on_pushButton_3_clicked();

    void on_pushButton_4_clicked();



    void on_pushButton_5_clicked();

    void on_pushButton_6_clicked();

    void on_pushButton_7_clicked();

    void on_pushButton_8_clicked();

    void on_pushButton_9_clicked();

    void on_pushButton_10_clicked();

    void on_pushButton_12_clicked();

    void on_pushButton_14_clicked();

    void on_pushButton_15_clicked();

    void on_pushButton_16_clicked();

    void on_pushButton_17_clicked();

    void on_pushButton_13_clicked();

    void on_pushButton_11_clicked();

private:
    Ui::calculator_invy *ui;

};

#endif // CALCULATOR_INVY_H
