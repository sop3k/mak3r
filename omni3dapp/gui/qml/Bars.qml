// import QtQuick 1.0 // to target S60 5th Edition or Maemo 5
import QtQuick 1.1
import QtQuick 1.0

Item {
    id: bars
    property int custom_height: 40
    property Rectangle last_active_tool: null
    property Rectangle last_active_bar: null
    width: parent.width
    height: custom_height

    Rectangle {
        id: top_bar
        x: 0
        y: 0
        width: parent.width
        height: custom_height
        color: "#51545b"

        Text {
            id: logo
            x: 0
            y: 0
            width: 100
            height: parent.height
            color: "#b8b8b8"
            text: qsTr("Mak3r Logo")
            font.bold: true
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
            font.pixelSize: 13
        }

        Rectangle {
            id: load
            y: 0
            width: custom_height
            height: custom_height
            color: mouse_area_load.containsMouse ? "#5f646c" : "#00000000"
            anchors.left: parent.left
            anchors.leftMargin: 1.5*logo.width

            Image {
                id: image_load
                x: 0
                y: 0
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                source: "resources/icons/plus-2x.png"
            }

            MouseArea {
                id: mouse_area_load
                anchors.fill: parent
                hoverEnabled: true
                onClicked: {
                    graphicsscene.showLoadModel();
                }
            }
        }

        Rectangle {
            id: save
            y: 0
            width: custom_height
            height: custom_height
            color: mouse_area_save.containsMouse ? "#5f646c" : "#00000000"
            anchors.leftMargin: load.anchors.leftMargin + custom_height
            anchors.left: parent.left

            Image {
                id: image_save
                x: 0
                y: 0
                anchors.horizontalCenter: parent.horizontalCenter
                source: "resources/icons/browser-2x.png"
                anchors.verticalCenter: parent.verticalCenter
            }

            MouseArea {
                id: mouse_area_save
                width: custom_height
                height: custom_height
                hoverEnabled: true
                onClicked: {
                    // graphicsscene.showSaveModel();
                    graphicsscene.showSaveGCode();
                }
            }
        }

        Rectangle {
            id: reload
            y: 0
            width: custom_height
            height: custom_height
            color: mouse_area_reload.containsMouse ? "#5f646c" : "#00000000"
            anchors.leftMargin: save.anchors.leftMargin + custom_height
            anchors.left: parent.left

            Image {
                id: image_reload
                x: 0
                y: 0
                anchors.horizontalCenter: parent.horizontalCenter
                source: "resources/icons/reload-2x.png"
                anchors.verticalCenter: parent.verticalCenter
            }

            MouseArea {
                id: mouse_area_reload
                width: custom_height
                height: custom_height
                hoverEnabled: true
                onClicked: {
                    graphicsscene.reloadScene();
                }
            }
        }

        Rectangle {
            id: deleteall
            y: 0
            width: custom_height
            height: custom_height
            color: mouse_area_deleteall.containsMouse ? "#5f646c" : "#00000000"
            Image {
                id: image_deleteall
                x: 0
                y: 0
                anchors.horizontalCenter: parent.horizontalCenter
                source: "resources/icons/trash-2x.png"
                anchors.verticalCenter: parent.verticalCenter
            }

            MouseArea {
                id: mouse_area_deleteall
                width: custom_height
                height: custom_height
                hoverEnabled: true
                onClicked: {
                    graphicsscene.onDeleteAll();
                }
            }
            anchors.leftMargin: reload.anchors.leftMargin + custom_height
            anchors.left: parent.left
        }

        Rectangle {
            id: separator1
            y: 0
            width: 1.0
            height: custom_height
            color: options_bar.color
            anchors.leftMargin: deleteall.anchors.leftMargin + custom_height
            anchors.left: parent.left
        }

        // Object manipulators

        Rectangle {
            id: rotate
            y: 0
            width: custom_height
            height: custom_height
            property bool isCurrentItem: false
            color: isCurrentItem ? orange_bar.color : (mouse_area_rotate.containsMouse ? "#5f646c" : "#00000000")
            Image {
                id: image_rotate
                x: 0
                y: 0
                opacity: 0.2
                anchors.horizontalCenter: parent.horizontalCenter
                source: "resources/icons/action-redo-2x.png"
                anchors.verticalCenter: parent.verticalCenter
            }

            MouseArea {
                id: mouse_area_rotate
                width: custom_height
                height: custom_height
                hoverEnabled: true
                enabled: false
                onClicked: {
                    graphicsscene.selectRotateTool();
                    rotate.isCurrentItem = !rotate.isCurrentItem;
                    set_active(rotate, rotate_bar);
                }
            }
            anchors.leftMargin: separator1.anchors.leftMargin + separator1.width
            anchors.left: parent.left

            function setEnabled(enabled) {
                if (enabled == true) {
                    image_rotate.opacity = 1; 
                    mouse_area_rotate.enabled = true;
                } else {
                    image_rotate.opacity = 0.2;
                    mouse_area_rotate.enabled = false;
                }
            }
        }

        Rectangle {
            id: scale
            y: 0
            width: custom_height
            height: custom_height
            property bool isCurrentItem: false
            color: isCurrentItem ? orange_bar.color : (mouse_area_scale.containsMouse ? "#5f646c" : "#00000000")
            Image {
                id: image_scale
                x: 0
                y: 0
                opacity: 0.2
                anchors.horizontalCenter: parent.horizontalCenter
                source: "resources/icons/resize-both-2x.png"
                anchors.verticalCenter: parent.verticalCenter
            }

            MouseArea {
                id: mouse_area_scale
                width: custom_height
                height: custom_height
                hoverEnabled: true
                enabled: false
                onClicked: {
                    graphicsscene.selectScaleTool();
                    scale.isCurrentItem = !scale.isCurrentItem;
                    set_active(scale, scale_bar);
                }
            }
            anchors.leftMargin: rotate.anchors.leftMargin + custom_height
            anchors.left: parent.left

            function setEnabled(enabled) {
                if (enabled == true) {
                    image_scale.opacity = 1; 
                    mouse_area_scale.enabled = true;
                } else {
                    image_scale.opacity = 0.2;
                    mouse_area_scale.enabled = false;
                }
            }
        }

        Rectangle {
            id: mirror
            y: 0
            width: custom_height
            height: custom_height
            property bool isCurrentItem: false
            color: isCurrentItem ? orange_bar.color : (mouse_area_mirror.containsMouse ? "#5f646c" : "#00000000")
            Image {
                id: image_mirror
                x: 0
                y: 0
                opacity: 0.2
                anchors.horizontalCenter: parent.horizontalCenter
                source: "resources/icons/resize-width-2x.png"
                anchors.verticalCenter: parent.verticalCenter
            }

            MouseArea {
                id: mouse_area_mirror
                width: custom_height
                height: custom_height
                hoverEnabled: true
                enabled: false
                onClicked: {
                    graphicsscene.selectMirrorTool();
                    mirror.isCurrentItem = !mirror.isCurrentItem;
                    set_active(mirror, mirror_bar);
                }
            }
            anchors.leftMargin: scale.anchors.leftMargin + custom_height
            anchors.left: parent.left

            function setEnabled(enabled) {
                if (enabled == true) {
                    image_mirror.opacity = 1; 
                    mouse_area_mirror.enabled = true;
                } else {
                    image_mirror.opacity = 0.2;
                    mouse_area_mirror.enabled = false;
                }
            }
        }
    }

    Rectangle {
        id: options_bar
        x: 0
        width: parent.width
        height: custom_height + orange_bar.height
        color: "#3f4245"
        border.color: "#313335"
        anchors.top: parent.top
        anchors.topMargin: custom_height 
        opacity: 0
        property int left_margin: 50

        Rectangle {
            id: rotate_bar
            anchors.fill: parent
            color: "#00000000"
            opacity: 0

            Rectangle {
                id: option_name_rotate
                x: 0
                y: 0
                width: 65
                height: options_bar.height
                color: "#51545b"

                Text {
                    id: option_text_rotate
                    color: "#d1d1d2"
                    text: qsTr("Rotate")
                    font.bold: true
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                    anchors.fill: parent
                    font.pixelSize: 11
                    font.family: lato_font.name
                }
            }

            Rectangle {
                id: reset
                width: 55
                height: 20
                color: "#333333"
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: option_name_rotate.width + options_bar.left_margin

                Text {
                    id: text_reset
                    color: "#d1d1d2"
                    text: qsTr("Reset")
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                    anchors.fill: parent
                    font.pixelSize: 11
                    font.family: lato_font.name
                }

                MouseArea {
                    id: mouse_area_reset
                    anchors.fill: parent
                    onClicked: {
                        graphicsscene.onRotateReset();
                    }
                }
            }

            Rectangle {
                id: lay_flat
                width: 55
                height: 20
                color: "#333333"
                anchors.verticalCenterOffset: 0
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: reset.anchors.leftMargin + reset.width + 30

                Text {
                    id: text_lay_flat
                    color: "#d1d1d2"
                    text: qsTr("Lay Flat")
                    font.pixelSize: 11
                    anchors.fill: parent
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    font.family: lato_font.name
                }

                MouseArea {
                    id: mouse_area_lay_flat
                    anchors.fill: parent
                    onClicked: {
                        graphicsscene.onLayFlat();
                    }
                }
            }
        }

        Rectangle {
            id: scale_bar
            anchors.fill: parent
            color: "#00000000"
            opacity: 0

            Rectangle {
                id: option_name_scale
                x: 0
                y: 0
                width: 65
                height: options_bar.height
                color: "#51545b"

                Text {
                    id: option_text_scale
                    color: "#d1d1d2"
                    text: qsTr("Scale")
                    font.bold: true
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                    anchors.fill: parent
                    font.pixelSize: 11
                    font.family: lato_font.name
                }
            }

            Text {
                id: text_scaleX
                color: "#d1d1d2"
                text: qsTr("Scale X")
                font.pixelSize: 11
                font.family: lato_font.name
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: option_name_scale.width + options_bar.left_margin
            }

            Rectangle {
                id: scaleX
                width: 55
                height: 20
                color: "#333333"
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: text_scaleX.anchors.leftMargin + text_scaleX.width + 10

                TextInput {
                    id: text_input_scaleX
                    objectName: "text_input_scaleX"
                    text: qsTr("1.0")
                    font.family: "Lato"
                    font.pixelSize: 11
                    anchors.fill: parent
                    anchors.top: parent.top
                    anchors.topMargin: 3
                    horizontalAlignment: TextInput.AlignHCenter
                    validator: DoubleValidator{bottom: 0;}
                    readOnly: false;
                }
            }

            Text {
                id: text_scaleY
                color: "#d1d1d2"
                text: qsTr("Scale Y")
                font.pixelSize: 11
                font.family: lato_font.name
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: scaleX.anchors.leftMargin + scaleX.width + 20
            }

            Rectangle {
                id: scaleY
                width: 55
                height: 20
                color: "#333333"
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: text_scaleY.anchors.leftMargin + text_scaleY.width + 10

                TextInput {
                    id: text_input_scaleY
                    objectName: "text_input_scaleY"
                    text: qsTr("1.0")
                    font.family: "Lato"
                    font.pixelSize: 11
                    anchors.fill: parent
                    anchors.top: parent.top
                    anchors.topMargin: 3
                    horizontalAlignment: TextInput.AlignHCenter
                    validator: DoubleValidator{bottom: 0;}
                    readOnly: false;
                }
            }

            Text {
                id: text_scaleZ
                color: "#d1d1d2"
                text: qsTr("Scale Z")
                font.pixelSize: 11
                font.family: lato_font.name
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: scaleY.anchors.leftMargin + scaleY.width + 20
            }

            Rectangle {
                id: scaleZ
                width: 55
                height: 20
                color: "#333333"
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: text_scaleZ.anchors.leftMargin + text_scaleZ.width + 10

                TextInput {
                    id: text_input_scaleZ
                    objectName: "text_input_scaleZ"
                    text: qsTr("1.0")
                    font.family: "Lato"
                    font.pixelSize: 11
                    anchors.fill: parent
                    anchors.top: parent.top
                    anchors.topMargin: 3
                    horizontalAlignment: TextInput.AlignHCenter
                    validator: DoubleValidator{bottom: 0;}
                    readOnly: false;
                }
            }

            Text {
                id: text_sizeX
                color: "#d1d1d2"
                text: qsTr("Size X")
                font.pixelSize: 11
                font.family: lato_font.name
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: scaleZ.anchors.leftMargin + scaleZ.width + options_bar.left_margin
            }

            Rectangle {
                id: sizeX
                width: 55
                height: 20
                color: "#333333"
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: text_sizeX.anchors.leftMargin + text_sizeX.width + 10

                TextInput {
                    id: text_input_sizeX
                    objectName: "text_input_sizeX"
                    text: qsTr("123")
                    font.family: "Lato"
                    font.pixelSize: 11
                    height: parent.height
                    width: parent.width - text_mm_sizeX.width
                    anchors.top: parent.top
                    anchors.topMargin: 3
                    anchors.left: parent.left
                    anchors.leftMargin: 0
                    horizontalAlignment: TextInput.AlignRight
                    validator: IntValidator{bottom: 0;}
                    readOnly: false;
                }

                Text {
                    id: text_mm_sizeX
                    height: parent.height
                    width: 25 
                    text: qsTr("mm")
                    anchors.right: parent.right
                    anchors.rightMargin: 0
                    anchors.top: parent.top
                    anchors.topMargin: 3
                    horizontalAlignment: Text.AlignHCenter
                    font.pixelSize: 11
                    font.family: "Lato"
                }
            }

            Text {
                id: text_sizeY
                color: "#d1d1d2"
                text: qsTr("Size Y")
                font.pixelSize: 11
                font.family: lato_font.name
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: sizeX.anchors.leftMargin + sizeX.width + 20
            }

            Rectangle {
                id: sizeY
                width: 55
                height: 20
                color: "#333333"
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: text_sizeY.anchors.leftMargin + text_sizeY.width + 10

                TextInput {
                    id: text_input_sizeY
                    objectName: "text_input_sizeY"
                    text: qsTr("123")
                    font.family: "Lato"
                    font.pixelSize: 11
                    height: parent.height
                    width: parent.width - text_mm_sizeY.width
                    anchors.top: parent.top
                    anchors.topMargin: 3
                    anchors.left: parent.left
                    anchors.leftMargin: 0
                    horizontalAlignment: TextInput.AlignRight
                    validator: IntValidator{bottom: 0;}
                    readOnly: false;
                }

                Text {
                    id: text_mm_sizeY
                    height: parent.height
                    width: 25 
                    text: qsTr("mm")
                    anchors.right: parent.right
                    anchors.rightMargin: 0
                    anchors.top: parent.top
                    anchors.topMargin: 3
                    horizontalAlignment: Text.AlignHCenter
                    font.pixelSize: 11
                    font.family: "Lato"
                }
            }

            Text {
                id: text_sizeZ
                color: "#d1d1d2"
                text: qsTr("Size Z")
                font.pixelSize: 11
                font.family: lato_font.name
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: sizeY.anchors.leftMargin + sizeY.width + 20
            }

            Rectangle {
                id: sizeZ
                width: 55
                height: 20
                color: "#333333"
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: text_sizeZ.anchors.leftMargin + text_sizeZ.width + 10

                TextInput {
                    id: text_input_sizeZ
                    objectName: "text_input_sizeZ"
                    text: qsTr("123")
                    font.family: "Lato"
                    font.pixelSize: 11
                    height: parent.height
                    width: parent.width - text_mm_sizeZ.width
                    anchors.top: parent.top
                    anchors.topMargin: 3
                    anchors.left: parent.left
                    anchors.leftMargin: 0
                    horizontalAlignment: TextInput.AlignRight
                    validator: IntValidator{bottom: 0;}
                    readOnly: false;
                }

                Text {
                    id: text_mm_sizeZ
                    height: parent.height
                    width: 25 
                    text: qsTr("mm")
                    anchors.right: parent.right
                    anchors.rightMargin: 0
                    anchors.top: parent.top
                    anchors.topMargin: 3
                    horizontalAlignment: Text.AlignHCenter
                    font.pixelSize: 11
                    font.family: "Lato"
                }
            }

            Rectangle {
                height: bars.custom_height
                width: bars.custom_height
                color: mouse_area_lock.containsMouse ? "#5f646c" : "#00000000"
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: sizeZ.anchors.leftMargin + sizeZ.width + 20

                Image {
                    id: locked
                    source: "resources/icons/link-intact-2x.png"
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    property bool isCurrentLock: true
                    opacity: isCurrentLock ? 1 : 0
                }

                Image {
                    id: unlocked
                    source: "resources/icons/link-broken-2x.png"
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    property bool isCurrentLock: false
                    opacity: isCurrentLock ? 1 : 0
                }

                MouseArea {
                    id: mouse_area_lock
                    anchors.fill: parent
                    hoverEnabled: true

                    onClicked: {
                        locked.isCurrentLock = !locked.isCurrentLock;
                        unlocked.isCurrentLock = !unlocked.isCurrentLock;
                    }
                }
            }
        }

        Rectangle {
            id: mirror_bar
            anchors.fill: parent
            color: "#00000000"
            opacity: 0

            Rectangle {
                id: option_name_mirror
                x: 0
                y: 0
                width: 65
                height: options_bar.height
                color: "#51545b"

                Text {
                    id: option_text_mirror
                    color: "#d1d1d2"
                    text: qsTr("Mirror")
                    font.bold: true
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                    anchors.fill: parent
                    font.pixelSize: 11
                    font.family: lato_font.name
                }
            }
        }

    }

    Rectangle {
        id: orange_bar
        x: 0
        width: parent.width
        height: 2
        color: "#ff5724"
        anchors.top: parent.top
        anchors.topMargin: custom_height 
    }

    function enableObjectTools(enabled) {
        rotate.setEnabled(enabled)
        scale.setEnabled(enabled)
        mirror.setEnabled(enabled)
        if (!enabled) {
            options_bar.opacity = 0;
        }
        if (bars.last_active_tool) {
            bars.last_active_tool.isCurrentItem = false;
        }
        if (bars.last_active_bar) {
            bars.last_active_bar.opacity = 0;
        }
        bars.last_active_tool = null;
        bars.last_active_bar = null;
    }

    function getDimensions() {
        return {
            'width': parent.width,
            'height': top_bar.height + options_bar.height
            }
    }

    function set_active(rect_tool, rect_bar) {
        if (rect_tool == bars.last_active_tool) {
            bars.last_active_tool = null;
            bars.last_active_bar = null;
            rect_bar.opacity = 0;
            options_bar.opacity = 0;
        } else if (bars.last_active_tool) {
            bars.last_active_tool.isCurrentItem = !bars.last_active_tool.isCurrentItem;
            bars.last_active_bar.opacity = 0;
            bars.last_active_bar.opacity = 0
        }
        if (rect_tool.isCurrentItem) {
            bars.last_active_tool = rect_tool;
            bars.last_active_bar = rect_bar;
            options_bar.opacity = 1;
            rect_bar.opacity = 1;
        }

    }
}
