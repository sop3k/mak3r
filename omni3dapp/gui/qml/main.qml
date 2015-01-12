// import QtQuick 1.0 // to target S60 5th Edition or Maemo 5
import QtQuick 1.1
import QtQuick 1.0

Rectangle {
    id: page
    color: "transparent"

    LoadButton {
        id: load_button
        anchors.left: parent.left
        anchors.leftMargin: 25
        anchors.top: parent.top
        anchors.topMargin: 25
    }

    ConfigButton {
        id: config_button
        anchors.left: parent.left
        anchors.leftMargin: 25
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 25
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
        width: 200
        height: 12
        opacity: 0
        anchors.top: parent.top
        anchors.topMargin: 64
        anchors.horizontalCenter: parent.horizontalCenter
    }

    function showLayersSlider() {
        layers_slider.opacity = 1
    }

    function hideLayersSlider() {
        layers_slider.opacity = 0
    }
}
