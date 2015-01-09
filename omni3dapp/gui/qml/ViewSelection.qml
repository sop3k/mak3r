// import QtQuick 1.0 // to target S60 5th Edition or Maemo 5
import QtQuick 1.1
import QtQuick 1.0

Rectangle {
    id: all_view_selections
    width: 32
    height: 158

    Image {
        id: image_normal
        x: 0
        anchors.top: parent.top
        anchors.topMargin: 0
        source: "resources/icons/collapse-down-4x.png"
    }

    Image {
        id: image_overhang
        x: 0
        anchors.top: parent.top
        anchors.topMargin: 42
        anchors.horizontalCenter: parent.horizontalCenter
        source: "resources/icons/collapse-left-4x.png"
    }

    Image {
        id: image_transparent
        x: 0
        y: 79
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 42
        anchors.horizontalCenter: parent.horizontalCenter
        source: "resources/icons/collapse-right-4x.png"
    }

    Image {
        id: image_layers
        x: 0
        y: 126
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 0
        source: "resources/icons/collapse-up-4x.png"
    }

    Rectangle {
        id: rect_normal
        x: 0
        width: 32
        height: 32
        color: "#00000000"
        anchors.top: parent.top
        anchors.topMargin: 0

        MouseArea {
            id: mouse_area_normal
            x: 0
            width: 32
            height: 32
            anchors.top: all_view_selections.bottom
            anchors.topMargin: -158
        }
    }

    Rectangle {
        id: rect_overhang
        x: 0
        width: 32
        height: 32
        color: "#00000000"
        anchors.top: parent.top
        anchors.topMargin: 42
        anchors.horizontalCenter: parent.horizontalCenter

        MouseArea {
            id: mouse_area_overhang
            x: 0
            y: 0
            width: 32
            height: 32
        }
    }

    Rectangle {
        id: rect_transparent
        x: 1
        y: 0
        width: 32
        height: 32
        color: "#00000000"
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 42
        anchors.horizontalCenter: parent.horizontalCenter

        MouseArea {
            id: mouse_area_transparent
            x: 0
            y: 0
            width: 32
            height: 32
        }
    }

    Rectangle {
        id: rect_layers
        x: 0
        y: 0
        width: 32
        height: 32
        color: "#00000000"
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 0

        MouseArea {
            id: mouse_area_layers
            x: 0
            y: 0
            width: 32
            height: 32
        }
    }
}
