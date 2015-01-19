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
            color: "#00000000"
            anchors.left: parent.left
            anchors.leftMargin: 1.5*logo.width

            Image {
                id: image_load
                x: 0
                y: 0
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                source: "resources/icons/plus2-4x.png"
            }

            MouseArea {
                id: mouse_area_load
                anchors.fill: parent
                onClicked: {
                    graphicsscene.showLoadModel();
                }
            }
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
