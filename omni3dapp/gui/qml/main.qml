// import QtQuick 1.0 // to target S60 5th Edition or Maemo 5
import QtQuick 1.1
import QtQuick 1.0
//import Sample 1.0

Rectangle {
    id: page
    width: 1024
    height: 786
    color: "transparent";

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

    /*
    SampleGLView {
        id: sample_view
        anchors.rightMargin: 100
        anchors.leftMargin: 100
        anchors.bottomMargin: 100
        anchors.topMargin: 100
        anchors.fill: parent
    }
    */
}
