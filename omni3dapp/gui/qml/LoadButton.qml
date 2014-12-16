// import QtQuick 1.0 // to target S60 5th Edition or Maemo 5
import QtQuick 1.1
import QtQuick 1.0


Rectangle {
    id: load_button
    width: 146
    height: 32
    color: parent.color
    state: "LOAD_FOLDED"

    Image {
        id: icon_load
        anchors.left: parent.left
        anchors.leftMargin: 0
        anchors.top: parent.top
        anchors.topMargin: 0
        source: "resources/icons/plus-4x.png"
    }

    Rectangle {
        id: rect_load
        width: 32
        height: 32
        color: "#00000000"
        opacity: 1
        anchors.left: parent.left
        anchors.leftMargin: 0
        anchors.top: parent.top
        anchors.topMargin: 0

        MouseArea {
            id: mousearea_load
            anchors.fill: parent
            onClicked: {
                if (load_button.state == "LOAD_FOLDED") {
                    load_button.state = "LOAD_EXPANDED"
                } else if (load_button.state == "LOAD_EXPANDED") {
                    load_button.state = "LOAD_FOLDED"
                }
            }
        }
    }

    Image {
        id: icon_folder
        anchors.left: parent.left
        anchors.leftMargin: 0
        anchors.top: parent.top
        anchors.topMargin: 0
        opacity: 0
        source: "resources/icons/folder-4x.png"
    }

    Rectangle {
        id: rect_folder
        width: 32
        height: 32
        color: "#00000000"
        opacity: 1
        anchors.left: parent.left
        anchors.leftMargin: 0
        anchors.top: parent.top
        anchors.topMargin: 0

        MouseArea {
            id: mousearea_load_folder
            anchors.fill: parent
            onClicked: { scene.showLoadModel() }
        }
    }

    Image {
        id: icon_file
        anchors.left: parent.left
        anchors.leftMargin: 0
        anchors.top: parent.top
        anchors.topMargin: 0
        opacity: 0
        source: "resources/icons/file-4x.png"
    }

    Rectangle {
        id: rect_file
        width: 32
        height: 32
        color: "#00000000"
        opacity: 1
        anchors.left: parent.left
        anchors.leftMargin: 0
        anchors.top: parent.top
        anchors.topMargin: 0

        MouseArea {
            id: mousearea_load_file
            anchors.fill: parent
            onClicked: {
                if (load_button.state == "LOAD_FOLDED") {
                    load_button.state = "LOAD_EXPANDED"
                } else if (load_button.state == "LOAD_EXPANDED") {
                    load_button.state = "LOAD_FOLDED"
                }
            }
        }
    }

    states: [
        State {
            name: "LOAD_EXPANDED"

            PropertyChanges {
                target: icon_folder
                anchors.leftMargin: 57
            }
            PropertyChanges {
                target: icon_folder
                opacity: 1
            }
            PropertyChanges {
                target: rect_folder
                anchors.leftMargin: 57
            }
            PropertyChanges {
                target: icon_file
                anchors.leftMargin: 114
            }
            PropertyChanges {
                target: icon_file
                opacity: 1
            }
            PropertyChanges {
                target: rect_file
                anchors.leftMargin: 114
            }
        },
        State {
            name: "LOAD_FOLDED"

            PropertyChanges {
                target: icon_folder
                anchors.leftMargin: 25
            }
            PropertyChanges {
                target: icon_folder
                opacity: 0
            }
            PropertyChanges {
                target: icon_file
                anchors.leftMargin: 25
            }
            PropertyChanges {
                target: icon_file
                opacity: 0
            }
        }
    ]

    transitions: [
        Transition {
            to: "*"
            NumberAnimation {
                target: icon_folder
                property: "anchors.leftMargin"
                duration: 350
                easing.type: Easing.InOutQuad
            }
            NumberAnimation {
                target: icon_folder
                property: "opacity"
                duration: 400
                easing.type: Easing.InOutQuad
            }
            NumberAnimation {
                target: icon_file
                property: "anchors.leftMargin"
                duration: 500
                easing.type: Easing.InOutQuad
            }
            NumberAnimation {
                target: icon_file
                property: "opacity"
                duration: 550
                easing.type: Easing.InOutQuad
            }
        }
    ]
}
