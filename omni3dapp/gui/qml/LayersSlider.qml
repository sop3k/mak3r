import QtQuick 1.1

Item {
    id: slider;
    width: 400;
    height: 16
    objectName: "layers_slider_item";

    // value is read/write
    property real value: 1;
    onValueChanged: updatePos();
    property real minimum: 1;
    property real maximum: 1;
    property int xMax: width - handle.width - 4;
    onXMaxChanged: updatePos();
    onMinimumChanged: updatePos();

    function setRange(min, max) {
        minimum = min;
        maximum = max;
    }

    function getValue() {
        return value;
    }

    function getMaxValue() {
        return maximum;
    }

    function setValue(val) {
        value = val;
    }

    function updatePos() {
        if (maximum > minimum) {
            var pos = 2 + (value - minimum) * slider.xMax / (maximum - minimum);
            pos = Math.min(pos, width - handle.width - 2);
            pos = Math.max(pos, 2);
            handle.x = pos;
        } else {
            handle.x = 2;
        }

    }

    Rectangle {
        anchors.fill: parent;
        color: "#333333"
        border.color: "#333333";
        border.width: 1;
        radius: 1;
    }

    Rectangle {
        id: handle;
        smooth: true;
        y: 2; width: 30; height: slider.height-4; color: "#94948f"; radius: 2

        MouseArea {
            id: mouse
            anchors.fill: parent;
            drag.target: parent;
            drag.axis: Drag.XAxis;
            drag.minimumX: 2;
            drag.maximumX: slider.xMax+2;
            onPositionChanged: {
                value = (maximum - minimum) * (handle.x-2) / slider.xMax + minimum;
            }
        }
    }
}
