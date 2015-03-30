import QtQuick 1.1

Rectangle {
    id: gconsole
    x: 0
    y: 0
    width: parent.width
    height: 0
    color: "#3f4245"

    Keys.onPressed: {
        if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
            mainwindow.sendCommand(textinput.text)
        }
    }

    Keys.onEscapePressed: {
        hideGConsole();
    }

    MouseArea {
        id: gconsole_mouse_area
        width: parent.width
        height: 3
        hoverEnabled: true
        onEntered: {
            if (gconsole.state == "DROPDOWN") {
                hideGConsole();
            } else {
                showGConsole();
            }
        }
    }

    Rectangle {
        id: textline
        width: parent.width
        height: 35
        color: "#3f4245"
        border.color: "#000000"
        anchors.left: parent.left
        anchors.leftMargin: 0
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 0

        TextInput {
            id: textinput
            width: parent.width - prompt.width
            color: "#d1d1d2"
            anchors.left: prompt.right
            anchors.leftMargin: 5
            anchors.verticalCenter: parent.verticalCenter
            cursorVisible: true
            font.pixelSize: 12
            font.family: lato_font.name
            horizontalAlignment: TextInput.AlignLeft
        }

        Text {
            id: prompt
            y: 0
            text: qsTr(" $ ")
            font.bold: true
            anchors.left: parent.left
            anchors.leftMargin: 5
            verticalAlignment: Text.AlignVCenter
            font.pixelSize: 12
            height: parent.height
            color: "#d1d1d2"
        }
    }

    Text {
        id: logbox
        objectName: "logbox"
        width: parent.width
        text: qsTr("text")
        anchors.bottom: textline.top
        anchors.bottomMargin: 0
        anchors.left: parent.left
        anchors.leftMargin: 0
        font.pixelSize: 12
        color: "#d1d1d2"
        font.family: lato_font.name
    }

    states: [
        State {
            name: "DROPDOWN"

            PropertyChanges {
                target: gconsole
                height: parent.height/3
            }

            PropertyChanges {
                target: gconsole
                opacity: 0.9
            }
        }
    ]

    transitions: [
        Transition {
            NumberAnimation {
                target: gconsole
                property: "height"
                duration: 800
                easing.type: Easing.OutExpo
            }
        }
    ]

    function showGConsole() {
        gconsole.state = "DROPDOWN";
        graphicsscene.setLayerOn();
    }

    function hideGConsole() {
        gconsole.state = "";
        graphicsscene.setLayerOff();
    }

    function appendToLogbox(log) {
        // logbox
    }
}
