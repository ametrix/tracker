#ifndef AHD_TRACKER_H
#define AHD_TRACKER_H

#include <QObject>

#include "UserInterface.h"
#include "Positioning.h"

namespace AHD {

class Tracker : public QObject
{
    Q_OBJECT

public:
    Tracker(QObject *parent = 0);

private:
    UserInterface mUserInterface;
    Positioning mPositioning;
};

}

#endif // AHD_TRACKER_H
