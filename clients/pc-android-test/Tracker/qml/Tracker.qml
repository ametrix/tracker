import QtQuick 2.3
import QtQuick.Controls 1.2

Item { id: root;

    Rectangle { id: comm; objectName: "comm";

        property string lattitude;
        property string longtitude;
        property string altitude;
        property string speed;
        property alias settingsMode: settingsPanel.visible;

        signal settingsChanged(string server);

        anchors.fill: parent;
        color: "black";

        function setServer(server) {
            serverInput.text = server;
        }

        Column { id: column;

            anchors.fill: parent;
            anchors.topMargin: 10;
            spacing: 10;

            Repeater {

                model: 3;
                delegate: Rectangle {

                    x: (column.width - width) / 2;
                    width: column.width * 0.8;
                    height: column.height * 0.1;
                    color: "lightgray";
                    radius: Math.min(width, height) * 0.5;
                    smooth: true;
                    antialiasing: true;
                    border.width: 2;
                    border.color: "white";

                    Text {
                        text: getText();
                        font.pixelSize: parent.height * 0.6;
                        anchors.fill: parent;
                        horizontalAlignment: Text.AlignHCenter;
                        verticalAlignment: Text.AlignVCenter;

                        function getText()
                        {
                            switch (index) {
                            case 0:
                                return "LAT: " + comm.lattitude;

                            case 1:
                                return "LON: " + comm.longtitude;

                            case 2:
                                return "ALT: " + comm.altitude;
                            }
                        }
                    }
                }
            }
        }

        Rectangle {
            color: "Transparent";
            smooth: true;
            antialiasing: true;
            anchors.top: parent.verticalCenter;
            anchors.bottom: parent.bottom;
            anchors.left: parent.left;
            anchors.right: parent.right;
            anchors.margins: 10;
            radius: Math.min(width, height) * 0.5;
            border.width: 2;
            border.color: "white";

            Text {
                anchors.centerIn: parent;
                font.pixelSize: parent.height * 0.1;
                font.italic: true;
                font.bold: true;
                text: comm.speed + " m/s";
                color: "white";
            }

            MouseArea {
                anchors.fill: parent;
                onClicked:
                    settingsPanel.visible = true;
            }
        }
    }

    Rectangle { id: settingsPanel;

        anchors.fill: parent;
        color: "black"
        visible: false;

        MouseArea {
            anchors.fill: parent;

            onPressed:
                comm.focus = true;
        }

        Rectangle {

            anchors.left: parent.left;
            anchors.top: parent.top;
            width: parent.width;
            height: 50;

            Text { id: label;

                anchors.left: parent.left;
                anchors.top: parent.top;
                height: parent.height;
                text: "URL: "
                font.pixelSize: parent.height * 0.5
                verticalAlignment: Text.AlignVCenter;
            }


            TextInput { id: serverInput;

                anchors.left: label.right;
                anchors.top: parent.top;
                anchors.bottom: parent.bottom;
                anchors.right: parent.right;
                text: "http://"
                color: "black"
                font.pixelSize: label.font.pixelSize;
                verticalAlignment: Text.AlignVCenter;

            }
        }

        Button {

            width: parent.width / 2;
            height: width / 2;
            anchors.horizontalCenter: parent.horizontalCenter;
            anchors.bottom: parent.bottom;
            anchors.bottomMargin: 10;
            text: "save";

            onClicked: {
                comm.settingsChanged(serverInput.text);
                settingsPanel.visible = false;
            }
        }
    }
}
