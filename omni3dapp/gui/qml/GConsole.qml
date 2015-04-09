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
            mainwindow.sendCommand(textinput.text);
            appendToHistory(textinput.text);
            textinput.text = qsTr("");
            textinput.histindex = -1;
        } else if (event.key == Qt.Key_Up) {
            textinput.histindex = (textinput.histindex + 1) % textinput.history.length;
            textinput.text = textinput.history[textinput.histindex]
        } else if (event.key == Qt.Key_Down) {
            var len = textinput.history.length;
            var newindex = textinput.histindex > 0 ? textinput.histindex : 0;
            newindex = (textinput.histindex - 1) % len;
            if (newindex < 0) {
                newindex = (len + newindex) % len;
            }
            textinput.histindex = newindex;
            textinput.text = textinput.history[textinput.histindex]
        } else if (event.key == 0x60) {
            hideGConsole();
        }
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

            property variant history: []
            property int histindex: -1
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

    Flickable {
        id: flickable_area
        // contentWidth: logbox.width
        // contentHeight: logbox.height
        anchors.bottom: textline.top
        anchors.bottomMargin: 0
        anchors.left: parent.left
        anchors.leftMargin: 5
        width: parent.width
        height: parent.height - textline.height
        flickableDirection: Flickable.VerticalFlick
        clip: true

        Text {
            id: logbox
            objectName: "logbox"
            width: gconsole.width
            font.pixelSize: 12
            color: "#d1d1d2"
            font.family: lato_font.name
            wrapMode: Text.Wrap
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 0
        }
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
        graphicsscene.setConsoleOn();
        textinput.forceActiveFocus();
    }

    function hideGConsole() {
        gconsole.state = "";
        graphicsscene.setConsoleOff();
    }

    function appendToLogbox(log) {
        logbox.text += log;
    }

    function appendToHistory(text) {
        var newhistory = [text],
            elems = Math.min(textinput.history.length, 9);
        for (var i = 0; i < elems; i++) {
            newhistory.push(textinput.history[i]);
        }
        textinput.history = newhistory;
    }
}
