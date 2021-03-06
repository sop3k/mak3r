import QtQuick 1.1

Rectangle {
    id: page
    color: "transparent"

    FontLoader {
        id: lato_font
        source: "resources/fonts/Lato-Bold.ttf"
    }

    Bars {
        id: bars
        objectName: "bars"
        anchors.left: parent.left
        anchors.leftMargin: 0
        anchors.top: parent.top
        anchors.topMargin: 0
    }

    LayersSlider {
        id: layers_slider
        objectName: "layers_slider"
        width: 200
        height: 12
        opacity: 0
        anchors.top: bars.bottom
        anchors.topMargin: bars.height / 2 - 5
        anchors.horizontalCenter: parent.horizontalCenter
    }

    function setLayersSliderVisible(val) {
        layers_slider.opacity = val;
        bars.showOptionsBar();
        // bars.setLayersViewOnly();
    }

    PrintButton {
        id: print_button
        objectName: "print_button"
        opacity: 0
        anchors.right: parent.right
        anchors.rightMargin: 25
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 25
    }

    ConnectButton {
        id: connect_button
        objectName: "connect_button"
        opacity: 1
        anchors.right: parent.right
        anchors.rightMargin: 30
        anchors.bottom: print_button.opacity == 1 ? print_button.top : parent.bottom
        anchors.bottomMargin: 25
    }

    function setPrintButtonVisible(val) {
        print_button.opacity = val;
    }

    ProgressBar {
        id: loader
        objectName: "loader"
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 0
        anchors.left: parent.left
        anchors.leftMargin: 0
    }

    OptionsLayer {
        id: options_layer
        objectName: "options_layer"
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
    }

    Wizard {
        id: wizard
        objectName: "wizard"
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
    }

    Rectangle {
        id: printarea_icon
        objectName: "printarea_icon"
        height: 27
        width: 27
        color: "#00000000"
        opacity: printingEnabled ? 1 : 0.2
        anchors.right: parent.right
        anchors.rightMargin: 24
        anchors.top: bars.bottom
        anchors.topMargin: 24

        property bool printingEnabled: false

        state: "HIDDEN"

        Image {
            id: printarea_show_icon
            source: "resources/icons/printarea.png"
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
        }

        Image {
            id: printarea_hide_icon
            source: "resources/icons/cancel.png"
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
        }

        MouseArea {
            id: mouse_area_printarea_icon
            anchors.fill: parent
            enabled: printarea_icon.printingEnabled

            onClicked: {
                printarea_icon.state = printarea_icon.state == "HIDDEN" ? "SHOWN" : "HIDDEN"
            }
        }

        states: [
            State {
                name: "HIDDEN"

                PropertyChanges {
                    target: printarea_hide_icon
                    opacity: 0
                }

                PropertyChanges {
                    target: printarea_show_icon
                    opacity: 1
                }

                PropertyChanges {
                    target: printarea
                    width: 0
                }

                PropertyChanges {
                    target: printarea
                    enabled: false
                }

                PropertyChanges {
                    target: printarea
                    opacity: 0
                }
            },

            State {
                name: "SHOWN"

                PropertyChanges {
                    target: printarea_hide_icon
                    opacity: 1
                }

                PropertyChanges {
                    target: printarea_show_icon
                    opacity: 0
                }

                PropertyChanges {
                    target: printarea
                    width: 420
                }

                PropertyChanges {
                    target: printarea
                    enabled: true
                }

                PropertyChanges {
                    target: printarea
                    opacity: 1
                }
            }
        ]
    }

    Rectangle {
        id: printarea
        objectName: "printarea"
        width: 0
        height: 400
        color: "#00000000"
        anchors.right: parent.right
        anchors.rightMargin: 24
        anchors.top: printarea_icon.bottom
        anchors.topMargin: 24
        enabled: false

        Behavior on width {
            PropertyAnimation {
                easing.type: Easing.InOutQuad
                duration: 500
            }
        }
        Behavior on opacity {
            PropertyAnimation {
                easing.type: Easing.InOutQuad
                duration: 800
            }
         }

        TempGauges {
            id: tempgauges
            objectName: "tempgauges"
            anchors.top: parent.top
            anchors.topMargin: 0
            anchors.left: parent.left
            anchors.leftMargin: 0
        }

        AxesController {
            id: axescontroller
            anchors.top: tempgauges.bottom
            anchors.topMargin: 24
            anchors.left: parent.left
            anchors.leftMargin: 0
        }
    }

    GConsole {
        id: gconsole
        objectName: "gconsole"
        anchors.top: parent.top
        anchors.topMargin: 0
        anchors.left: parent.left
        anchors.leftMargin: 0
    }

    function disableOtherElements(activeElement) {
        for (var i = 0; i < page.children.length; i++) {
            var child = page.children[i];
            if (child.objectName && child.objectName != activeElement) {
                child.enabled = false;
            }
        }
    }

    function enableAllElements(enabled) {
        for (var i = 0; i < page.children.length; i++) {
            page.children[i].enabled = enabled; 
        }
    }
}
