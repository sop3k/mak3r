// import QtQuick 1.0 // to target S60 5th Edition or Maemo 5
import QtQuick 1.1
import QtQuick 1.0

Item {
    id: bars
    property int custom_height: 40
    width: parent.width
    height: custom_height

    Rectangle {
        id: top_bar
        x: 0
        y: 0
        width: parent.width
        height: custom_height
        color: "#51545b"

        Text {
            id: logo
            x: 0
            y: 0
            width: 100
            height: parent.height
            color: "#b8b8b8"
            text: qsTr("Mak3r Logo")
            font.bold: true
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
            font.pixelSize: 13
        }

        Rectangle {
            id: load
            y: 0
            width: custom_height
            height: custom_height
            color: mouse_area_load.containsMouse ? "#5f646c" : "#00000000"
            anchors.left: parent.left
            anchors.leftMargin: 1.5*logo.width

            Image {
                id: image_load
                x: 0
                y: 0
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                source: "resources/icons/plus-2x.png"
            }

            MouseArea {
                id: mouse_area_load
                anchors.fill: parent
                hoverEnabled: true
                onClicked: {
                    graphicsscene.showLoadModel();
                }
            }
        }

        Rectangle {
            id: save
            y: 0
            width: custom_height
            height: custom_height
            color: mouse_area_save.containsMouse ? "#5f646c" : "#00000000"
            anchors.leftMargin: load.anchors.leftMargin + custom_height
            anchors.left: parent.left

            Image {
                id: image_save
                x: 0
                y: 0
                anchors.horizontalCenter: parent.horizontalCenter
                source: "resources/icons/browser-2x.png"
                anchors.verticalCenter: parent.verticalCenter
            }

            MouseArea {
                id: mouse_area_save
                width: custom_height
                height: custom_height
                hoverEnabled: true
                onClicked: {
                    // graphicsscene.showSaveModel();
                    graphicsscene.showSaveGCode();
                }
            }
        }

        Rectangle {
            id: reload
            y: 0
            width: custom_height
            height: custom_height
            color: mouse_area_reload.containsMouse ? "#5f646c" : "#00000000"
            anchors.leftMargin: save.anchors.leftMargin + custom_height
            anchors.left: parent.left

            Image {
                id: image_reload
                x: 0
                y: 0
                anchors.horizontalCenter: parent.horizontalCenter
                source: "resources/icons/reload-2x.png"
                anchors.verticalCenter: parent.verticalCenter
            }

            MouseArea {
                id: mouse_area_reload
                width: custom_height
                height: custom_height
                hoverEnabled: true
                onClicked: {
                    graphicsscene.reloadScene();
                }
            }
        }

        Rectangle {
            id: deleteall
            y: 0
            width: custom_height
            height: custom_height
            color: mouse_area_deleteall.containsMouse ? "#5f646c" : "#00000000"
            Image {
                id: image_deleteall
                x: 0
                y: 0
                anchors.horizontalCenter: parent.horizontalCenter
                source: "resources/icons/trash-2x.png"
                anchors.verticalCenter: parent.verticalCenter
            }

            MouseArea {
                id: mouse_area_deleteall
                width: custom_height
                height: custom_height
                hoverEnabled: true
                onClicked: {
                    graphicsscene.onDeleteAll();
                }
            }
            anchors.leftMargin: reload.anchors.leftMargin + custom_height
            anchors.left: parent.left
        }
    }

    Rectangle {
        id: options_bar
        x: 0
        width: parent.width
        height: custom_height + orange_bar.height
        color: "#3f4245"
        border.color: "#313335"
        anchors.top: parent.top
        anchors.topMargin: custom_height 
    }

    Rectangle {
        id: orange_bar
        x: 0
        width: parent.width
        height: 1
        color: "#ff5724"
        anchors.top: parent.top
        anchors.topMargin: custom_height 
    }
}
