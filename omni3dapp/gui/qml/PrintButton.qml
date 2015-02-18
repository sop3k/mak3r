// import QtQuick 1.0 // to target S60 5th Edition or Maemo 5
import QtQuick 1.1

Rectangle {
    id: print_button
    width: 225 + cancel_print.width
    height: 32
    color: "#00000000"
    state: "IDLE"

    Rectangle {
        id: button
        width: 100
        height: 32
        color: "#ff5724"
        anchors.right: cancel_print.left
        anchors.rightMargin: 5

        Text {
            id: button_text
            color: "#ffffff"
            text: qsTr("Print")
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
                if (print_button.state == "IDLE") {
                    options_layer.showLayer();
                } else if (print_button.state == "SLICING") {
                    graphicsscene.onStopEngine();
                    print_button.state = "IDLE";
                } else if (print_button.state == "SLICED") {
                    // start printing
                    graphicsscene.onPrintButton();
                    print_button.state = "PRINTING";
                } else if (print_button.state == "PRINTING") {
                    // pause printing
                    mainwindow.pausePrinting();
                    print_button.state = "PAUSED";
                } else if (print_button.state == "PAUSED") {
                    // resume printing
                    print_button.state = "PRINTING";
                }
            }
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
        font.family: lato_font.name
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
        font.family: lato_font.name
    }

    Rectangle {
        id: cancel_print
        width: 0
        height: 0
        color: "#51545b"
        anchors.right: parent.right
        anchors.rightMargin: 0
        opacity: 0
        enabled: false

        Image {
            id: img_cancel
            source: "resources/icons/close.png"
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
        }


        MouseArea {
            id: mouse_area_cancel_print
            anchors.fill: parent
            onClicked: {
                // cancel printing
                mainwindow.turnOffPrinter()
                print_button.state = "SLICED"
            }
        }
    }

    states: [
        State {
            name: "IDLE"

            PropertyChanges {
                target: button_text
                text: qsTr("Slice")
            }
        },
        State {
            name: "SLICING"

            PropertyChanges {
                target: button_text
                text: qsTr("Stop")
            }
        },
        State {
            name: "SLICED"

            PropertyChanges {
                target: button_text
                text: qsTr("Print")
            }
        },
        State {
            name: "PRINTING"

            PropertyChanges {
                target: button_text
                text: qsTr("Pause")
            }

            PropertyChanges {
                target: cancel_print
                opacity: 1
                enabled: true
                width: 32
                height: 32
            }
        },
        State {
            name: "PAUSED"

            PropertyChanges {
                target: button_text
                text: qsTr("Resume")
            }

            PropertyChanges {
                target: cancel_print
                opacity: 1
                enabled: true
                width: 32
                height: 32
            }
        }
    ]

    function setPrintTime(text) {
        print_time.text = qsTr(text);
    }

    function setPrintParams(text) {
        print_params.text = qsTr(text);
    }

    function getState() {
        return print_button.state;
    }

    function setState(state) {
        print_button.state = state;
    }

    function disable() {
        print_button.enabled = false;
        button.color = "#b8b8b8";
    }

    function enable() {
        print_button.enabled = true;
        button.color = "#ff5724";
    }

}
