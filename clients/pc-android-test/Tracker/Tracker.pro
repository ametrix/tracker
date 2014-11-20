QT += core gui widgets positioning qml quick
TARGET = Tracker
TEMPLATE = app

SOURCES += main.cpp\
           Tracker.cpp \
           Positioning.cpp \
           UserInterface.cpp

HEADERS  += Tracker.h \
            Positioning.h \
            UserInterface.h

CONFIG += mobility

RESOURCES += Resources.qrc

OTHER_FILES += qml/Tracker.qml \
               android/AndroidManifest.xml

ANDROID_PACKAGE_SOURCE_DIR = $$PWD/android

