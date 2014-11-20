#include "Tracker.h"
#include <QApplication>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    AHD::Tracker w;

    return a.exec();
}
