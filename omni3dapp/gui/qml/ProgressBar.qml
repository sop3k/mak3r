// import QtQuick 1.0 // to target S60 5th Edition or Maemo 5
import QtQuick 1.1

Rectangle {
    id: loader
    width: parent.width
    height: 30
    color: "#00000000"

    Rectangle {
        id: black_bar
        width: parent.width
        height: 5
        color: "#000000"
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 0
        property real value: 0

            Rectangle {
                id: orange_bar
                x: 0
                y: 0
                width: black_bar.value * parent.width
                height: 5
                color: "#ff5724"
            }
    }

    Text {
        id: info
        x: 0
        y: 0
        width: parent.width
        height: loader.height - black_bar.height
        text: qsTr("")
        color: "#ff5724"
        font.pixelSize: 12
        //verticalAlignment: Text.AlignVTop
        horizontalAlignment: Text.AlignLeft
        anchors.left: parent.left
        anchors.leftMargin: 15
        font.family: lato_font.name
    }

    function setValue(val) {
        black_bar.value = val;
    }

    function setInfoText(text) {
        info.text = qsTr(text);
    }

}
