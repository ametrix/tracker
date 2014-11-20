#ifndef AHD_POSITIONING_H
#define AHD_POSITIONING_H

#include <QObject>

#include <QPointer>

#include <QGeoPositionInfoSource>
#include <QGeoPositionInfo>
#include <QNetworkAccessManager>
#include <QSettings>

#include "UserInterface.h"

namespace AHD {

class Positioning : public QObject
{
    Q_OBJECT

public:
    explicit Positioning(QObject *parent = 0);

    void setUserInterface(UserInterface *interface);
signals:

public slots:

private slots:
    void positionUpdated(const QGeoPositionInfo &info);
    void finished(QNetworkReply *reply);
    void settingsChanged(const QString &server);

private:
    bool mPosting;
    QByteArray mData;
    QPointer<QGeoPositionInfoSource> mSource;
    QPointer<UserInterface> mUserInterface;
    QNetworkAccessManager mNetworkAccessManager;
    QSettings mSettings;
    QUrl mServer;
};

}

#endif // POSITIONING_H
