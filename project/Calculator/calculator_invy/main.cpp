#include "calculator_invy.h"
#include <QApplication>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    calculator_invy w;
    w.show();

    return a.exec();
}
