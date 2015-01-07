// import QtQuick 1.0 // to target S60 5th Edition or Maemo 5
import QtQuick 1.1
import QtQuick 1.0

Rectangle {
    id: all_view_selections
    width: 158
    height: 32

    Image {
        id: image_normal
        anchors.left: parent.left
        anchors.leftMargin: 0
        source: "resources/icons/collapse-down-4x.png"
    }

    Image {
        id: image_overhang
        anchors.left: parent.left
        anchors.leftMargin: 42
        anchors.verticalCenter: parent.verticalCenter
        source: "resources/icons/collapse-left-4x.png"
    }

    Image {
        id: image_transparent
        x: 0
        y: 79
        anchors.right: parent.right
        anchors.rightMargin: 42
        anchors.verticalCenter: parent.verticalCenter
        source: "resources/icons/collapse-right-4x.png"
    }

    Image {
        id: image_layers
        x: 0
        y: 0
        anchors.right: parent.right
        anchors.rightMargin: 0
        source: "resources/icons/collapse-up-4x.png"
    }

    Rectangle {
        id: rect_normal
        width: 32
        height: 32
        color: "#00000000"
        anchors.left: parent.left
        anchors.leftMargin: 0

        MouseArea {
            id: mouse_area_normal
            x: 0
            y: 0
            width: 32
            height: 32
        }
    }

    Rectangle {
        id: rect_overhang
        width: 32
        height: 32
        color: "#00000000"
        anchors.left: parent.left
        anchors.leftMargin: 42
        anchors.verticalCenter: parent.verticalCenter

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
        anchors.right: parent.right
        anchors.rightMargin: 42
        anchors.verticalCenter: parent.verticalCenter

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
        anchors.right: parent.right
        anchors.rightMargin: 0

        MouseArea {
            id: mouse_area_layers
            x: 0
            y: 0
            width: 32
            height: 32
        }
    }
}
