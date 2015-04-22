// import QtQuick 1.0 // to target S60 5th Edition or Maemo 5
import QtQuick 1.1

Rectangle {
    id: connect_button
    width: 100
    height: 32
    color: "#ff5724"

    state: "OFFLINE"

    Text {
        id: button_text
        color: "#ffffff"
        text: qsTr("Connect")
        font.bold: true
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        anchors.fill: parent
        font.pixelSize: 14
        font.family: lato_font.name
    }

    MouseArea {
        id: mouse_area_button
        anchors.fill: parent
        onClicked: {
            if (connect_button.state == "OFFLINE") {
                mainwindow.connectPrinter();
            } else if (connect_button.state == "ONLINE") {
                mainwindow.disconnectPrinter();
            }
        }
    }

    states: [
        State {
            name: "OFFLINE"

            PropertyChanges {
                target: button_text
                text: qsTr("Connect")
            }

            PropertyChanges {
                target: axescontroller
                opacity: 0
            }

            PropertyChanges {
                target: tempgauges
                opacity: 0
            }
        },
        State {
            name: "ONLINE"

            PropertyChanges {
                target: button_text
                text: qsTr("Disconnect")
            }

            PropertyChanges {
                target: axescontroller
                opacity: 1
            }

            PropertyChanges {
                target: tempgauges
                opacity: 1
            }
        }
    ]

    function getState() {
        return connect_button.state;
    }

    function setState(state) {
        connect_button.state = state;
    }

}
