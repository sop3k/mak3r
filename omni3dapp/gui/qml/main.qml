// import QtQuick 1.0 // to target S60 5th Edition or Maemo 5
import QtQuick 1.1
import QtQuick 1.0

Rectangle {
    id: page
    color: "transparent"

    Bars {
        id: bars
        anchors.left: parent.left
        anchors.leftMargin: 0
        anchors.top: parent.top
        anchors.topMargin: 0
    }

    ViewSelect {
        id: view_select
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: 25
        opacity: 0
    }

    function showViewSelect() {
        view_select.opacity = 1
    }

    function hideViewSelect() {
        view_select.opacity = 0
    }

    LayersSlider {
        id: layers_slider
        objectName: "layers_slider"
        width: 200
        height: 12
        opacity: 0
        anchors.top: parent.top
        anchors.topMargin: 64
        anchors.horizontalCenter: parent.horizontalCenter
    }

    function setLayersSliderVisible(val) {
        layers_slider.opacity = val;
    }

    PrintButton {
        id: print_button
        anchors.right: parent.right
        anchors.rightMargin: 25
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 25
    }

    Loader {
        id: loader
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 0
    }
}
