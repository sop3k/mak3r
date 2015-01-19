// import QtQuick 1.0 // to target S60 5th Edition or Maemo 5
import QtQuick 1.1

Rectangle {
    id: loader
    width: parent.width
    height: 5
    color: "#000000"
    property real value: 0

    Rectangle {
        id: orange_bar
        x: 0
        y: 0
        width: value * parent.width
        height: 5
        color: "#ff5724"

         //Behavior on width {
         //    SmoothedAnimation {
         //        velocity: 1000;
         //        reversingMode: SmoothedAnimation.Sync
         //    }
         //}
    }

    function setValue(val) {
        value = val;
    }
}
