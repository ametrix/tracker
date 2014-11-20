#ifndef AHD_USERINTERFACE_H
#define AHD_USERINTERFACE_H

#include <QQuickView>

namespace AHD {

class UserInterface : public QQuickView
{
    Q_OBJECT

public:
    UserInterface(QWindow *parent = 0);
};

}

#endif // AHD_USERINTERFACE_H
