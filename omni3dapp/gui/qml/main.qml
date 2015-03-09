// import QtQuick 1.0 // to target S60 5th Edition or Maemo 5
import QtQuick 1.1
import QtQuick 1.0

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

    // PrintArea {
    //     id: print_area
    //     objectName: "print_area"
    //     anchors.right: parent.right
    //     anchors.rightMargin: 20
    //     anchors.top: bars.bottom
    //     anchors.topMargin: 55
    // }
}
