/********************************************************************************
** Form generated from reading UI file 'calculator_invy.ui'
**
** Created by: Qt User Interface Compiler version 5.5.1
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_CALCULATOR_INVY_H
#define UI_CALCULATOR_INVY_H

#include <QtCore/QVariant>
#include <QtWidgets/QAction>
#include <QtWidgets/QApplication>
#include <QtWidgets/QButtonGroup>
#include <QtWidgets/QHeaderView>
#include <QtWidgets/QLineEdit>
#include <QtWidgets/QMainWindow>
#include <QtWidgets/QPushButton>
#include <QtWidgets/QStatusBar>
#include <QtWidgets/QToolBar>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_calculator_invy
{
public:
    QWidget *centralWidget;
    QLineEdit *lineEdit;
    QPushButton *pushButton;
    QPushButton *pushButton_2;
    QPushButton *pushButton_3;
    QPushButton *pushButton_4;
    QPushButton *pushButton_5;
    QPushButton *pushButton_6;
    QPushButton *pushButton_7;
    QPushButton *pushButton_8;
    QPushButton *pushButton_9;
    QPushButton *pushButton_10;
    QPushButton *pushButton_11;
    QPushButton *pushButton_12;
    QPushButton *pushButton_13;
    QPushButton *pushButton_14;
    QPushButton *pushButton_15;
    QPushButton *pushButton_16;
    QPushButton *pushButton_17;
    QToolBar *mainToolBar;
    QStatusBar *statusBar;

    void setupUi(QMainWindow *calculator_invy)
    {
        if (calculator_invy->objectName().isEmpty())
            calculator_invy->setObjectName(QStringLiteral("calculator_invy"));
        calculator_invy->resize(385, 272);
        centralWidget = new QWidget(calculator_invy);
        centralWidget->setObjectName(QStringLiteral("centralWidget"));
        lineEdit = new QLineEdit(centralWidget);
        lineEdit->setObjectName(QStringLiteral("lineEdit"));
        lineEdit->setGeometry(QRect(20, 20, 251, 21));
        pushButton = new QPushButton(centralWidget);
        pushButton->setObjectName(QStringLiteral("pushButton"));
        pushButton->setGeometry(QRect(290, 20, 75, 23));
        pushButton_2 = new QPushButton(centralWidget);
        pushButton_2->setObjectName(QStringLiteral("pushButton_2"));
        pushButton_2->setGeometry(QRect(20, 70, 75, 23));
        pushButton_3 = new QPushButton(centralWidget);
        pushButton_3->setObjectName(QStringLiteral("pushButton_3"));
        pushButton_3->setGeometry(QRect(110, 70, 75, 23));
        pushButton_4 = new QPushButton(centralWidget);
        pushButton_4->setObjectName(QStringLiteral("pushButton_4"));
        pushButton_4->setGeometry(QRect(200, 70, 75, 23));
        pushButton_5 = new QPushButton(centralWidget);
        pushButton_5->setObjectName(QStringLiteral("pushButton_5"));
        pushButton_5->setGeometry(QRect(20, 110, 75, 23));
        pushButton_6 = new QPushButton(centralWidget);
        pushButton_6->setObjectName(QStringLiteral("pushButton_6"));
        pushButton_6->setGeometry(QRect(110, 110, 75, 23));
        pushButton_7 = new QPushButton(centralWidget);
        pushButton_7->setObjectName(QStringLiteral("pushButton_7"));
        pushButton_7->setGeometry(QRect(200, 110, 75, 23));
        pushButton_8 = new QPushButton(centralWidget);
        pushButton_8->setObjectName(QStringLiteral("pushButton_8"));
        pushButton_8->setGeometry(QRect(20, 150, 75, 23));
        pushButton_9 = new QPushButton(centralWidget);
        pushButton_9->setObjectName(QStringLiteral("pushButton_9"));
        pushButton_9->setGeometry(QRect(110, 150, 75, 23));
        pushButton_10 = new QPushButton(centralWidget);
        pushButton_10->setObjectName(QStringLiteral("pushButton_10"));
        pushButton_10->setGeometry(QRect(200, 150, 75, 23));
        pushButton_11 = new QPushButton(centralWidget);
        pushButton_11->setObjectName(QStringLiteral("pushButton_11"));
        pushButton_11->setGeometry(QRect(20, 190, 75, 23));
        pushButton_12 = new QPushButton(centralWidget);
        pushButton_12->setObjectName(QStringLiteral("pushButton_12"));
        pushButton_12->setGeometry(QRect(110, 190, 75, 23));
        pushButton_13 = new QPushButton(centralWidget);
        pushButton_13->setObjectName(QStringLiteral("pushButton_13"));
        pushButton_13->setGeometry(QRect(200, 190, 75, 23));
        pushButton_14 = new QPushButton(centralWidget);
        pushButton_14->setObjectName(QStringLiteral("pushButton_14"));
        pushButton_14->setGeometry(QRect(290, 70, 75, 23));
        pushButton_15 = new QPushButton(centralWidget);
        pushButton_15->setObjectName(QStringLiteral("pushButton_15"));
        pushButton_15->setGeometry(QRect(290, 110, 75, 23));
        pushButton_16 = new QPushButton(centralWidget);
        pushButton_16->setObjectName(QStringLiteral("pushButton_16"));
        pushButton_16->setGeometry(QRect(290, 150, 75, 23));
        pushButton_17 = new QPushButton(centralWidget);
        pushButton_17->setObjectName(QStringLiteral("pushButton_17"));
        pushButton_17->setGeometry(QRect(290, 190, 75, 23));
        calculator_invy->setCentralWidget(centralWidget);
        mainToolBar = new QToolBar(calculator_invy);
        mainToolBar->setObjectName(QStringLiteral("mainToolBar"));
        calculator_invy->addToolBar(Qt::TopToolBarArea, mainToolBar);
        statusBar = new QStatusBar(calculator_invy);
        statusBar->setObjectName(QStringLiteral("statusBar"));
        calculator_invy->setStatusBar(statusBar);

        retranslateUi(calculator_invy);

        QMetaObject::connectSlotsByName(calculator_invy);
    } // setupUi

    void retranslateUi(QMainWindow *calculator_invy)
    {
        calculator_invy->setWindowTitle(QApplication::translate("calculator_invy", "\350\256\241\347\256\227\345\231\250", 0));
        pushButton->setText(QApplication::translate("calculator_invy", "AC", 0));
        pushButton_2->setText(QApplication::translate("calculator_invy", "7", 0));
        pushButton_3->setText(QApplication::translate("calculator_invy", "8", 0));
        pushButton_4->setText(QApplication::translate("calculator_invy", "9", 0));
        pushButton_5->setText(QApplication::translate("calculator_invy", "4", 0));
        pushButton_6->setText(QApplication::translate("calculator_invy", "5", 0));
        pushButton_7->setText(QApplication::translate("calculator_invy", "6", 0));
        pushButton_8->setText(QApplication::translate("calculator_invy", "1", 0));
        pushButton_9->setText(QApplication::translate("calculator_invy", "2", 0));
        pushButton_10->setText(QApplication::translate("calculator_invy", "3", 0));
        pushButton_11->setText(QApplication::translate("calculator_invy", ".", 0));
        pushButton_12->setText(QApplication::translate("calculator_invy", "0", 0));
        pushButton_13->setText(QApplication::translate("calculator_invy", "=", 0));
        pushButton_14->setText(QApplication::translate("calculator_invy", "+", 0));
        pushButton_15->setText(QApplication::translate("calculator_invy", "-", 0));
        pushButton_16->setText(QApplication::translate("calculator_invy", "\303\227", 0));
        pushButton_17->setText(QApplication::translate("calculator_invy", "\303\267", 0));
    } // retranslateUi

};

namespace Ui {
    class calculator_invy: public Ui_calculator_invy {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_CALCULATOR_INVY_H
