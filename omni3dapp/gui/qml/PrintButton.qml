// import QtQuick 1.0 // to target S60 5th Edition or Maemo 5
import QtQuick 1.1

Rectangle {
    id: print_button
    width: 220
    height: 32
    color: "#00000000"

    Rectangle {
        id: button
        width: 100
        height: 32
        color: "#ff5724"
        anchors.right: parent.right
        anchors.rightMargin: 0

        Text {
            id: text
            color: "#ffffff"
            text: qsTr("Print")
            font.family: "Arial"
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            anchors.fill: parent
            font.pixelSize: 14
        }
    }

    Text {
        id: print_time
        width: 100
        height: 16
        color: "#b8b8b8"
        text: qsTr("")
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignRight
        font.pixelSize: 12
    }

    Text {
        id: print_params
        width: 100
        height: 16
        color: "#b8b8b8"
        text: qsTr("")
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignRight
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 0
        font.pixelSize: 12
    }

    function setPrintTime(text) {
        print_time.text = qsTr(text)
    }

    function setPrintParams(text) {
        print_params.text = qsTr(text)
    }

}
