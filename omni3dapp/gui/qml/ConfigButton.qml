// import QtQuick 1.0 // to target S60 5th Edition or Maemo 5
import QtQuick 1.1
import QtQuick 1.0

Rectangle {
    id: config_button
    width: 330
    height: 432
    color: parent.color
    state: "CONFIG_FOLDED"

    Image {
        id: icon_config
        y: 454
        anchors.left: parent.left
        anchors.leftMargin: 0
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 0
        source: "resources/icons/cog-4x.png"
    }

    Rectangle {
        id: rect_config
        width: 32
        height: 32
        color: "#00000000"
        anchors.left: parent.left
        anchors.leftMargin: 0
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 0

        MouseArea {
            id: mousearea_config
            anchors.fill: parent
            onClicked: {
                if (config_button.state == "CONFIG_FOLDED") {
                    config_button.state = "CONFIG_EXPANDED"
                } else if (config_button.state == "CONFIG_EXPANDED") {
                    config_button.state = "CONFIG_FOLDED"
                }
            }
        }
    }

    Grid {
        id: grid_config
        x: 0
        y: 52
        width: 330
        height: 345
        flow: Grid.LeftToRight
        rows: 0
        columns: 3
        spacing: 10
        opacity: 0

        Rectangle {
            id: rectangle1
            x: 31
            y: 319
            width: 100
            height: 90
            color: "#ffffff"
        }

        Rectangle {
            id: rectangle2
            x: 29
            y: 313
            width: 100
            height: 90
            color: "#ffffff"
        }

        Rectangle {
            id: rectangle3
            x: 39
            y: 309
            width: 100
            height: 90
            color: "#ffffff"
        }

        Rectangle {
            id: rectangle4
            x: 39
            y: 312
            width: 100
            height: 90
            color: "#ffffff"
            radius: 1
        }

        Rectangle {
            id: rectangle5
            x: 36
            y: 324
            width: 100
            height: 90
            color: "#ffffff"
        }

        Rectangle {
            id: rectangle6
            x: 32
            y: 314
            width: 100
            height: 90
            color: "#ffffff"
        }

        Rectangle {
            id: rectangle7
            x: 36
            y: 315
            width: 100
            height: 90
            color: "#ffffff"
        }

        Rectangle {
            id: rectangle8
            x: 23
            y: 322
            width: 100
            height: 90
            color: "#ffffff"
        }

        Rectangle {
            id: rectangle9
            x: 23
            y: 328
            width: 100
            height: 90
            color: "#ffffff"
        }

        Rectangle {
            id: rectangle10
            x: 22
            y: 319
            width: 100
            height: 90
            color: "#ffffff"
        }

        Rectangle {
            id: rectangle11
            x: 34
            y: 328
            width: 100
            height: 90
            color: "#ffffff"
        }

        Rectangle {
            id: rectangle12
            x: 32
            y: 316
            width: 100
            height: 90
            color: "#ffffff"
        }
    }
    states: [
        State {
            name: "CONFIG_EXPANDED"
            PropertyChanges {
                target: grid_config
                opacity: 1
            }
            PropertyChanges {
                target: grid_config
                y: 0
            }
        },
        State {
            name: "CONFIG_FOLDED"
            PropertyChanges {
                target: grid_config
                opacity: 0
            }
            PropertyChanges {
                target: grid_config
                y: 52
            }
        }
    ]

    transitions: [
        Transition {
            to: "*"
            ParallelAnimation {
                NumberAnimation {
                    target: grid_config
                    property: "y"
                    duration: 350
                    easing.type: Easing.Linear
                }
                NumberAnimation {
                    target: grid_config
                    property: "opacity"
                    duration: 700
                    easing.type: Easing.Linear
                }
            }
        }
    ]
}
