#include "UserInterface.h"

namespace AHD {

UserInterface::UserInterface(QWindow *parent) :
    QQuickView(parent)
{
    setResizeMode(QQuickView::SizeRootObjectToView);
    setSource(QUrl("qrc:/AHD/qml/Tracker.qml"));
    showFullScreen();
}

}
