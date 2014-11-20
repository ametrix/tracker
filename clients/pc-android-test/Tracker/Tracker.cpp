#include "Tracker.h"

namespace AHD {

Tracker::Tracker(QObject *parent) :
    QObject(parent)
{
    mPositioning.setUserInterface(&mUserInterface);
}

}
