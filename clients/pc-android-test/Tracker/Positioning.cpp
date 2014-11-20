#include "Positioning.h"

#include <QQuickItem>

#include <QNetworkRequest>
#include <QNetworkReply>
#include <QJsonObject>
#include <QJsonArray>
#include <QJsonDocument>

namespace AHD {

Positioning::Positioning(QObject *parent) :
    QObject(parent),
    mPosting(false),
    mSettings("AHD", "Tracker")
{
    mNetworkAccessManager.setNetworkAccessible(QNetworkAccessManager::Accessible);
    connect(&mNetworkAccessManager, SIGNAL(finished(QNetworkReply*)), this, SLOT(finished(QNetworkReply*)));

    mSource = QGeoPositionInfoSource::createDefaultSource(this);
    if (mSource) {
        connect(&(*mSource), SIGNAL(positionUpdated(QGeoPositionInfo)),
                this, SLOT(positionUpdated(QGeoPositionInfo)));
        mSource->startUpdates();
    }

    mServer = QUrl(mSettings.value("server").toString());
}

void Positioning::positionUpdated(const QGeoPositionInfo &info)
{
    qDebug("Entering position update!");

    if (mUserInterface) {
        QObject *comm = mUserInterface->rootObject()->findChild<QObject *>("comm");
        if (comm) {
            qDebug("GOT COMM!");

            comm->setProperty("lattitude", QString::number(info.coordinate().latitude()));
            comm->setProperty("longtitude", QString::number(info.coordinate().longitude()));
            comm->setProperty("altitude", QString::number(info.coordinate().altitude()));
            comm->setProperty("speed", QString::number(info.attribute(QGeoPositionInfo::GroundSpeed)));

            if (!mPosting) {
                qDebug("Posting to server: %s!", qPrintable(mServer.toString()));
                mPosting = true;
                QJsonObject gpsinfo;
                gpsinfo["time"] = QDateTime::currentDateTime().toString(Qt::ISODate);
                gpsinfo["lat"] = info.coordinate().latitude();
                gpsinfo["lon"] = info.coordinate().longitude();
                gpsinfo["speed"] = info.attribute(QGeoPositionInfo::GroundSpeed);

                QJsonArray array;
                array.append(gpsinfo);

                QJsonObject container;
                container["gpcoord-data"] = gpsinfo;

                mData.clear();
                QJsonDocument doc(container);
                mData = doc.toJson();
                QNetworkRequest request(mServer);

                request.setRawHeader("User-Agent", "Tracker v1.0");
                request.setRawHeader("X-Custom-User-Agent", "Tracker v1.0");
                request.setRawHeader("Content-Type", "application/json");
                request.setRawHeader("Content-Length", QByteArray::number(mData.size()));

                mNetworkAccessManager.post(request, mData);
            }
        }
    }
}

void Positioning::finished(QNetworkReply *reply)
{
    qDebug("Posted!");
    mPosting = false;
    reply->deleteLater();
}

void Positioning::settingsChanged(const QString &server)
{
    qDebug("Server bchanged: %s", qPrintable(server));
    mSettings.setValue("server", server.trimmed());
    mServer = QUrl(server.trimmed());
}

void Positioning::setUserInterface(UserInterface *interface)
{
    mUserInterface = interface;
    if (mUserInterface) {
        QObject *comm = mUserInterface->rootObject()->findChild<QObject *>("comm");
        if (comm) {
            connect(comm, SIGNAL(settingsChanged(QString)), this, SLOT(settingsChanged(QString)));
            QMetaObject::invokeMethod(comm, "setServer", Q_ARG(QVariant, mServer.toString()));
        }
    }
}

}
