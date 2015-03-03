// import QtQuick 1.0 // to target S60 5th Edition or Maemo 5
import QtQuick 1.1
import QtQuick 1.0

Item {
    id: bars
    property int custom_height: 55
    property Rectangle last_active_tool: null
    property Rectangle last_active_bar: null
    width: parent.width
    height: custom_height

    signal scaled(string value, int axis, bool unified, bool is_mm)

    Rectangle {
        id: top_bar
        x: 0
        y: 0
        width: parent.width
        height: custom_height
        color: "#51545b"

        Image {
            id: logo
            source: "resources/logo_grey_small.png"
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            anchors.leftMargin: 20
        }

        Rectangle {
            id: load
            y: 0
            width: custom_height
            height: custom_height
            property bool isCurrentItem: false
            color: isCurrentItem ? orange_bar.color : (mouse_area_load.containsMouse ? "#5f646c" : "#00000000")
            anchors.left: parent.left
            anchors.leftMargin: 1.5*logo.width

            Image {
                id: image_load
                x: 0
                y: 0
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                source: "resources/icons/new.png"
            }

            MouseArea {
                id: mouse_area_load
                anchors.fill: parent
                hoverEnabled: true
                onClicked: {
                    load.isCurrentItem = !load.isCurrentItem;
                    setActive(load, null);
                    graphicsscene.showLoadModel();
                    unsetActive();
                }
            }
        }

        Rectangle {
            id: save
            y: 0
            width: custom_height
            height: custom_height
            property bool isCurrentItem: false
            color: isCurrentItem ? orange_bar.color : (mouse_area_save.containsMouse ? "#5f646c" : "#00000000")
            anchors.leftMargin: load.anchors.leftMargin + custom_height
            anchors.left: parent.left

            Image {
                id: image_save
                x: 0
                y: 0
                anchors.horizontalCenter: parent.horizontalCenter
                source: "resources/icons/save.png"
                anchors.verticalCenter: parent.verticalCenter
            }

            MouseArea {
                id: mouse_area_save
                width: custom_height
                height: custom_height
                hoverEnabled: true
                onClicked: {
                    save.isCurrentItem = !save.isCurrentItem;
                    setActive(save, save_bar);
                }
            }
        }

        Rectangle {
            id: reload
            y: 0
            width: custom_height
            height: custom_height
            property bool isCurrentItem: false
            color: isCurrentItem ? orange_bar.color : (mouse_area_reload.containsMouse ? "#5f646c" : "#00000000")
            anchors.leftMargin: save.anchors.leftMargin + custom_height
            anchors.left: parent.left

            Image {
                id: image_reload
                x: 0
                y: 0
                anchors.horizontalCenter: parent.horizontalCenter
                source: "resources/icons/restore.png"
                anchors.verticalCenter: parent.verticalCenter
            }

            MouseArea {
                id: mouse_area_reload
                width: custom_height
                height: custom_height
                hoverEnabled: true
                onClicked: {
                    reload.isCurrentItem = !reload.isCurrentItem;
                    setActive(reload, null);
                    graphicsscene.reloadScene();
                }
            }
        }

        Rectangle {
            id: deleteall
            y: 0
            width: custom_height
            height: custom_height
            property bool isCurrentItem: false
            color: isCurrentItem ? orange_bar.color : (mouse_area_deleteall.containsMouse ? "#5f646c" : "#00000000")
            Image {
                id: image_deleteall
                x: 0
                y: 0
                anchors.horizontalCenter: parent.horizontalCenter
                source: "resources/icons/erase.png"
                anchors.verticalCenter: parent.verticalCenter
            }

            MouseArea {
                id: mouse_area_deleteall
                width: custom_height
                height: custom_height
                hoverEnabled: true
                onClicked: {
                    deleteall.isCurrentItem = !deleteall.isCurrentItem;
                    setActive(deleteall, null);
                    graphicsscene.onDeleteAll();
                    unsetActive();
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
                source: "resources/icons/rotate.png"
                anchors.verticalCenter: parent.verticalCenter
            }

            MouseArea {
                id: mouse_area_rotate
                width: custom_height
                height: custom_height
                hoverEnabled: true
                enabled: false
                onClicked: {
                    rotate.isCurrentItem = !rotate.isCurrentItem;
                    setActive(rotate, rotate_bar);
                    graphicsscene.selectRotateTool();
                }
            }
            anchors.leftMargin: separator1.anchors.leftMargin + separator1.width + 5 
            anchors.left: parent.left

            function setOptionEnabled(enabled) {
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
            id: lay_flat
            y: 0
            width: custom_height
            height: custom_height
            property bool isCurrentItem: false
            color: isCurrentItem ? orange_bar.color : (mouse_area_lay_flat.containsMouse ? "#5f646c" : "#00000000")
            Image {
                id: image_lay_flat
                x: 0
                y: 0
                opacity: 0.2
                anchors.horizontalCenter: parent.horizontalCenter
                source: "resources/icons/laydown.png"
                anchors.verticalCenter: parent.verticalCenter
            }

            MouseArea {
                id: mouse_area_lay_flat
                width: custom_height
                height: custom_height
                hoverEnabled: true
                enabled: false
                onClicked: {
                    lay_flat.isCurrentItem = !lay_flat.isCurrentItem;
                    setActive(lay_flat, null);
                    graphicsscene.onLayFlat();
                    lay_flat.isCurrentItem = !lay_flat.isCurrentItem;
                }
            }
            anchors.leftMargin: rotate.anchors.leftMargin + custom_height
            anchors.left: parent.left

            function setOptionEnabled(enabled) {
                if (enabled == true) {
                    image_lay_flat.opacity = 1; 
                    mouse_area_lay_flat.enabled = true;
                } else {
                    image_lay_flat.opacity = 0.2;
                    mouse_area_lay_flat.enabled = false;
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
                source: "resources/icons/scale.png"
                anchors.verticalCenter: parent.verticalCenter
            }

            MouseArea {
                id: mouse_area_scale
                width: custom_height
                height: custom_height
                hoverEnabled: true
                enabled: false
                onClicked: {
                    scale.isCurrentItem = !scale.isCurrentItem;
                    setActive(scale, scale_bar);
                    graphicsscene.selectScaleTool();
                }
            }
            anchors.leftMargin: lay_flat.anchors.leftMargin + custom_height
            anchors.left: parent.left

            function setOptionEnabled(enabled) {
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
            id: to_max
            y: 0
            width: custom_height
            height: custom_height
            property bool isCurrentItem: false
            color: isCurrentItem ? orange_bar.color : (mouse_area_to_max.containsMouse ? "#5f646c" : "#00000000")
            Image {
                id: image_to_max
                x: 0
                y: 0
                opacity: 0.2
                anchors.horizontalCenter: parent.horizontalCenter
                source: "resources/icons/max.png"
                anchors.verticalCenter: parent.verticalCenter
            }

            MouseArea {
                id: mouse_area_to_max
                width: custom_height
                height: custom_height
                hoverEnabled: true
                enabled: false
                onClicked: {
                    to_max.isCurrentItem = !to_max.isCurrentItem;
                    setActive(to_max, null);
                    graphicsscene.onScaleMax();
                }
            }
            anchors.leftMargin: scale.anchors.leftMargin + custom_height
            anchors.left: parent.left

            function setOptionEnabled(enabled) {
                if (enabled == true) {
                    image_to_max.opacity = 1; 
                    mouse_area_to_max.enabled = true;
                } else {
                    image_to_max.opacity = 0.2;
                    mouse_area_to_max.enabled = false;
                }
            }
        }

        Rectangle {
            id: separator2
            y: 0
            width: 1.0
            height: custom_height
            color: options_bar.color
            anchors.leftMargin: to_max.anchors.leftMargin + custom_height
            anchors.left: parent.left
        }

        // Mirror on axes

        Rectangle {
            id: mirror_x
            y: 0
            width: custom_height
            height: custom_height
            property bool isCurrentItem: false
            color: mouse_area_mirror_x.containsMouse ? "#5f646c" : "#00000000"
            Image {
                id: image_mirror_x
                x: 0
                y: 0
                opacity: 0.2
                anchors.horizontalCenter: parent.horizontalCenter
                source: "resources/icons/flip_x.png"
                anchors.verticalCenter: parent.verticalCenter
            }

            MouseArea {
                id: mouse_area_mirror_x
                width: custom_height
                height: custom_height
                hoverEnabled: true
                enabled: false
                onClicked: {
                    mirror_x.isCurrentItem = !mirror_x.isCurrentItem;
                    setActive(mirror_x, null);
                    graphicsscene.onMirror(0);
                    mirror_x.isCurrentItem = !mirror_x.isCurrentItem;
                }
            }
            anchors.leftMargin: separator2.anchors.leftMargin + separator2.width + 5 
            anchors.left: parent.left

            function setOptionEnabled(enabled) {
                if (enabled == true) {
                    image_mirror_x.opacity = 1; 
                    mouse_area_mirror_x.enabled = true;
                } else {
                    image_mirror_x.opacity = 0.2;
                    mouse_area_mirror_x.enabled = false;
                }
            }
        }

        Rectangle {
            id: mirror_y
            y: 0
            width: custom_height
            height: custom_height
            property bool isCurrentItem: false
            color: mouse_area_mirror_y.containsMouse ? "#5f646c" : "#00000000"
            Image {
                id: image_mirror_y
                x: 0
                y: 0
                opacity: 0.2
                anchors.horizontalCenter: parent.horizontalCenter
                source: "resources/icons/flip_y.png"
                anchors.verticalCenter: parent.verticalCenter
            }

            MouseArea {
                id: mouse_area_mirror_y
                width: custom_height
                height: custom_height
                hoverEnabled: true
                enabled: false
                onClicked: {
                    mirror_y.isCurrentItem = !mirror_y.isCurrentItem;
                    setActive(mirror_y, null);
                    graphicsscene.onMirror(1);
                    mirror_y.isCurrentItem = !mirror_y.isCurrentItem;
                }
            }
            anchors.leftMargin: mirror_x.anchors.leftMargin + custom_height
            anchors.left: parent.left

            function setOptionEnabled(enabled) {
                if (enabled == true) {
                    image_mirror_y.opacity = 1; 
                    mouse_area_mirror_y.enabled = true;
                } else {
                    image_mirror_y.opacity = 0.2;
                    mouse_area_mirror_y.enabled = false;
                }
            }
        }

        Rectangle {
            id: mirror_z
            y: 0
            width: custom_height
            height: custom_height
            property bool isCurrentItem: false
            color: mouse_area_mirror_z.containsMouse ? "#5f646c" : "#00000000"
            Image {
                id: image_mirror_z
                x: 0
                y: 0
                opacity: 0.2
                anchors.horizontalCenter: parent.horizontalCenter
                source: "resources/icons/flip_z.png"
                anchors.verticalCenter: parent.verticalCenter
            }

            MouseArea {
                id: mouse_area_mirror_z
                width: custom_height
                height: custom_height
                hoverEnabled: true
                enabled: false
                onClicked: {
                    mirror_z.isCurrentItem = !mirror_z.isCurrentItem;
                    setActive(mirror_z, null);
                    graphicsscene.onMirror(2);
                    mirror_z.isCurrentItem = !mirror_z.isCurrentItem;
                }
            }
            anchors.leftMargin: mirror_y.anchors.leftMargin + custom_height
            anchors.left: parent.left

            function setOptionEnabled(enabled) {
                if (enabled == true) {
                    image_mirror_z.opacity = 1; 
                    mouse_area_mirror_z.enabled = true;
                } else {
                    image_mirror_z.opacity = 0.2;
                    mouse_area_mirror_z.enabled = false;
                }
            }
        }

        Rectangle {
            id: separator3
            y: 0
            width: 1.0
            height: custom_height
            color: options_bar.color
            anchors.leftMargin: mirror_z.anchors.leftMargin + custom_height
            anchors.left: parent.left
        }

        // View modes

        Rectangle {
            id: view_modes
            objectName: "view_modes"
            y: 0
            width: custom_height
            height: custom_height
            property bool isCurrentItem: false
            color: isCurrentItem ? orange_bar.color : (mouse_area_view_modes.containsMouse ? "#5f646c" : "#00000000")

            Image {
                id: image_view_modes
                x: 0
                y: 0
                opacity: 0.2
                anchors.horizontalCenter: parent.horizontalCenter
                source: "resources/icons/view.png"
                anchors.verticalCenter: parent.verticalCenter
            }

            MouseArea {
                id: mouse_area_view_modes
                width: custom_height
                height: custom_height
                hoverEnabled: true
                enabled: false
                onClicked: {
                    view_modes.isCurrentItem = !view_modes.isCurrentItem;
                    setActive(view_modes, view_modes_bar);
                }
            }
            anchors.leftMargin: separator3.anchors.leftMargin + separator3.width + 5 
            anchors.left: parent.left

            function setOptionEnabled(enabled) {
                if (enabled == true) {
                    image_view_modes.opacity = 1; 
                    mouse_area_view_modes.enabled = true;
                } else {
                    image_view_modes.opacity = 0.2;
                    mouse_area_view_modes.enabled = false;
                }
            }

            function showLayersButton() {
                layers_view.opacity = 1;
                mouse_area_layers_view.enabled = true;
            }

            function hideLayersButton() {
                layers_view.opacity = 0;
                mouse_area_layers_view.enabled = false;
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
        property TextInput current_input: null
        
        Rectangle {
            id: save_bar
            anchors.fill: parent
            color: "#00000000"
            opacity: 0

            Rectangle {
                id: option_name_save
                x: 0
                y: 0
                width: 85
                height: options_bar.height
                color: "#51545b"

                Text {
                    id: option_text_save
                    color: "#d1d1d2"
                    text: qsTr("Save")
                    font.bold: true
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                    anchors.fill: parent
                    font.pixelSize: 11
                    font.family: lato_font.name
                }
            }

            Rectangle {
                id: save_scene
                width: custom_height
                height: custom_height
                color: mouse_area_save_scene.containsMouse ? "#5f646c" : "#00000000"
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: option_name_save.width + options_bar.left_margin

                Image {
                    id: image_save_scene
                    source: "resources/icons/save_scene.png"
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                }

                MouseArea {
                    id: mouse_area_save_scene
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: {
                        graphicsscene.showSaveModel();
                    }
                }
            }

            Rectangle {
                id: save_gcode
                width: custom_height
                height: custom_height
                color: mouse_area_save_gcode.containsMouse ? "#5f646c" : "#00000000"
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: save_scene.anchors.leftMargin + save_scene.width + 30

                Image {
                    id: image_save_gcode
                    source: "resources/icons/save_g.png"
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                }

                MouseArea {
                    id: mouse_area_save_gcode
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: {
                        graphicsscene.showSaveGCode();
                    }
                }
            }

        }

        Rectangle {
            id: rotate_bar
            anchors.fill: parent
            color: "#00000000"
            opacity: 0

            Rectangle {
                id: option_name_rotate
                x: 0
                y: 0
                width: 85
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
        }

        Rectangle {
            id: scale_bar
            anchors.fill: parent
            color: "#00000000"
            opacity: 0

            property bool uniform: locked.isCurrentLock

            Rectangle {
                id: option_name_scale
                x: 0
                y: 0
                width: 85
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
                    color: "#d1d1d2"
                    font.family: "Lato"
                    font.pixelSize: 11
                    anchors.fill: parent
                    anchors.top: parent.top
                    anchors.topMargin: 3
                    horizontalAlignment: TextInput.AlignHCenter
                    validator: DoubleValidator{bottom: 0;}
                    readOnly: false
                    cursorVisible: options_bar.current_input == text_input_scaleX
                    Keys.onPressed: {
                        if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                            bars.scaled(text, 0, scale_bar.uniform, false)
                        }
                    }
                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            text_input_scaleX.forceActiveFocus();
                            options_bar.current_input = text_input_scaleX;
                        }
                    }
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
                    color: "#d1d1d2"
                    font.family: "Lato"
                    font.pixelSize: 11
                    anchors.fill: parent
                    anchors.top: parent.top
                    anchors.topMargin: 3
                    horizontalAlignment: TextInput.AlignHCenter
                    validator: DoubleValidator{bottom: 0;}
                    readOnly: false;
                    cursorVisible: options_bar.current_input == text_input_scaleY
                    Keys.onPressed: {
                        if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                            bars.scaled(text, 1, scale_bar.uniform, false)
                        }
                    }
                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            text_input_scaleY.forceActiveFocus();
                            options_bar.current_input = text_input_scaleY;
                        }
                    }
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
                    color: "#d1d1d2"
                    font.family: "Lato"
                    font.pixelSize: 11
                    anchors.fill: parent
                    anchors.top: parent.top
                    anchors.topMargin: 3
                    horizontalAlignment: TextInput.AlignHCenter
                    validator: DoubleValidator{bottom: 0;}
                    readOnly: false;
                    cursorVisible: options_bar.current_input == text_input_scaleZ
                    Keys.onPressed: {
                        if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                            bars.scaled(text, 2, scale_bar.uniform, false)
                        }
                    }
                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            text_input_scaleZ.forceActiveFocus();
                            options_bar.current_input = text_input_scaleZ;
                        }
                    }
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
                width: 60
                height: 20
                color: "#333333"
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: text_sizeX.anchors.leftMargin + text_sizeX.width + 10

                TextInput {
                    id: text_input_sizeX
                    objectName: "text_input_sizeX"
                    text: qsTr("1.0")
                    color: "#d1d1d2"
                    font.family: "Lato"
                    font.pixelSize: 11
                    height: parent.height
                    width: 33
                    anchors.top: parent.top
                    anchors.topMargin: 3
                    anchors.left: parent.left
                    anchors.leftMargin: 3
                    horizontalAlignment: TextInput.AlignHCenter
                    validator: IntValidator{bottom: 0;}
                    readOnly: false;
                    cursorVisible: options_bar.current_input == text_input_sizeX
                    Keys.onPressed: {
                        if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                            bars.scaled(text, 0, scale_bar.uniform, true)
                        }
                    }
                }

                Text {
                    id: text_mm_sizeX
                    height: parent.height
                    width: 22
                    text: qsTr("mm")
                    color: "#d1d1d2"
                    anchors.left: text_input_sizeX.right
                    anchors.leftMargin: 3
                    anchors.right: parent.right
                    anchors.rightMargin: 3
                    anchors.top: parent.top
                    anchors.topMargin: 3
                    horizontalAlignment: Text.AlignHCenter
                    font.pixelSize: 11
                    font.family: "Lato"
                }

                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        text_input_sizeX.forceActiveFocus();
                        options_bar.current_input = text_input_sizeX;
                    }
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
                width: 60
                height: 20
                color: "#333333"
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: text_sizeY.anchors.leftMargin + text_sizeY.width + 10

                TextInput {
                    id: text_input_sizeY
                    objectName: "text_input_sizeY"
                    text: qsTr("1.0")
                    color: "#d1d1d2"
                    font.family: "Lato"
                    font.pixelSize: 11
                    height: parent.height
                    width: 33
                    anchors.top: parent.top
                    anchors.topMargin: 3
                    anchors.left: parent.left
                    anchors.leftMargin: 3
                    horizontalAlignment: TextInput.AlignHCenter
                    validator: IntValidator{bottom: 0;}
                    readOnly: false;
                    cursorVisible: options_bar.current_input == text_input_sizeY
                    Keys.onPressed: {
                        if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                            bars.scaled(text, 1, scale_bar.uniform, true)
                        }
                    }
                }

                Text {
                    id: text_mm_sizeY
                    height: parent.height
                    width: 22 
                    text: qsTr("mm")
                    color: "#d1d1d2"
                    anchors.left: text_input_sizeY.right
                    anchors.leftMargin: 3
                    anchors.right: parent.right
                    anchors.rightMargin: 3
                    anchors.top: parent.top
                    anchors.topMargin: 3
                    horizontalAlignment: Text.AlignHCenter
                    font.pixelSize: 11
                    font.family: "Lato"
                }

                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        text_input_sizeY.forceActiveFocus();
                        options_bar.current_input = text_input_sizeY;
                    }
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
                width: 60
                height: 20
                color: "#333333"
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: text_sizeZ.anchors.leftMargin + text_sizeZ.width + 10

                TextInput {
                    id: text_input_sizeZ
                    objectName: "text_input_sizeZ"
                    text: qsTr("1.0")
                    color: "#d1d1d2"
                    font.family: "Lato"
                    font.pixelSize: 11
                    height: parent.height
                    width: 33
                    anchors.top: parent.top
                    anchors.topMargin: 3
                    anchors.left: parent.left
                    anchors.leftMargin: 3
                    horizontalAlignment: TextInput.AlignHCenter
                    validator: IntValidator{bottom: 0;}
                    readOnly: false;
                    cursorVisible: options_bar.current_input == text_input_sizeZ
                    Keys.onPressed: {
                        if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                            bars.scaled(text, 2, scale_bar.uniform, true)
                        }
                    }
                }

                Text {
                    id: text_mm_sizeZ
                    height: parent.height
                    width: 22
                    text: qsTr("mm")
                    color: "#d1d1d2"
                    anchors.left: text_input_sizeZ.right
                    anchors.leftMargin: 3
                    anchors.right: parent.right
                    anchors.rightMargin: 3
                    anchors.top: parent.top
                    anchors.topMargin: 3
                    horizontalAlignment: Text.AlignHCenter
                    font.pixelSize: 11
                    font.family: "Lato"
                }

                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        text_input_sizeZ.forceActiveFocus();
                        options_bar.current_input = text_input_sizeZ;
                    }
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
                    source: "resources/icons/lock_closed.png"
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    property bool isCurrentLock: true
                    opacity: isCurrentLock ? 1 : 0
                }

                Image {
                    id: unlocked
                    source: "resources/icons/lock_opened.png"
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
            id: view_modes_bar
            anchors.fill: parent
            color: "#00000000"
            opacity: 0

            property Rectangle currentView: normal_view

            Rectangle {
                id: option_name_view_modes
                x: 0
                y: 0
                width: 85
                height: options_bar.height
                color: "#51545b"

                Text {
                    id: option_text_view_modes
                    color: "#d1d1d2"
                    text: qsTr("View mode")
                    font.bold: true
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                    anchors.fill: parent
                    font.pixelSize: 11
                    font.family: lato_font.name
                }
            }

            Rectangle {
                id: normal_view
                width: custom_height
                height: custom_height
                color: (view_modes_bar.currentView == normal_view || mouse_area_normal_view.containsMouse) ? "#5f646c" : "#00000000"
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: option_name_view_modes.width + options_bar.left_margin

                Image {
                    id: image_normal_view
                    source: "resources/icons/normal.png"
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                }

                MouseArea {
                    id: mouse_area_normal_view
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: {
                        view_modes_bar.currentView = normal_view;
                        graphicsscene.setViewMode('normal');
                    }
                }
            }

            Rectangle {
                id: overhang_view
                width: custom_height
                height: custom_height
                color: (view_modes_bar.currentView == overhang_view || mouse_area_overhang_view.containsMouse) ? "#5f646c" : "#00000000"
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: normal_view.anchors.leftMargin + normal_view.width + 30

                Image {
                    id: image_overhang_view
                    source: "resources/icons/overhang.png"
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                }

                MouseArea {
                    id: mouse_area_overhang_view
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: {
                        view_modes_bar.currentView = overhang_view;
                        graphicsscene.setViewMode('overhang');
                    }
                }
            }

            Rectangle {
                id: xray_view
                width: custom_height
                height: custom_height
                color: (view_modes_bar.currentView == xray_view || mouse_area_xray_view.containsMouse) ? "#5f646c" : "#00000000"
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: overhang_view.anchors.leftMargin + overhang_view.width + 30

                Image {
                    id: image_xray_view
                    source: "resources/icons/xray.png"
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                }

                MouseArea {
                    id: mouse_area_xray_view
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: {
                        view_modes_bar.currentView = xray_view;
                        graphicsscene.setViewMode('xray');
                    }
                }
            }

            Rectangle {
                id: transparent_view
                width: custom_height
                height: custom_height
                color: (view_modes_bar.currentView == transparent_view || mouse_area_transparent_view.containsMouse) ? "#5f646c" : "#00000000"
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: xray_view.anchors.leftMargin + xray_view.width + 30

                Image {
                    id: image_transparent_view
                    source: "resources/icons/transparent.png"
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                }

                MouseArea {
                    id: mouse_area_transparent_view
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: {
                        view_modes_bar.currentView = transparent_view;
                        graphicsscene.setViewMode('transparent');
                    }
                }
            }

            Rectangle {
                id: layers_view
                width: custom_height
                height: custom_height
                color: (view_modes_bar.currentView == layers_view || mouse_area_layers_view.containsMouse) ? "#5f646c" : "#00000000"
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: transparent_view.anchors.leftMargin + transparent_view.width + 30
                opacity: 0

                Image {
                    id: image_layers_view
                    source: "resources/icons/layers.png"
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                }

                MouseArea {
                    id: mouse_area_layers_view
                    anchors.fill: parent
                    enabled: false
                    hoverEnabled: true
                    onClicked: {
                        view_modes_bar.currentView = layers_view;
                        graphicsscene.setViewMode('gcode');
                    }
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

    transitions: [
        Transition {
            to: "*"
            /*
            NumberAnimation {
                target: options_bar
                property: "anchors.topMargin"
                duration: 350
                easing.type: Easing.InOutQuad
            }
            */
            NumberAnimation {
                target: options_bar
                property: "opacity"
                duration: 400
                easing.type: Easing.InOutQuad
            }
        }
    ]


    function enableObjectTools(enabled) {
        rotate.setOptionEnabled(enabled)
        lay_flat.setOptionEnabled(enabled)
        scale.setOptionEnabled(enabled)
        to_max.setOptionEnabled(enabled)
        mirror_x.setOptionEnabled(enabled)
        mirror_y.setOptionEnabled(enabled)
        mirror_z.setOptionEnabled(enabled)

        options_bar.opacity = 0;
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

    function setActive(rect_tool, rect_bar) {
        graphicsscene.selectMirrorTool();
        if (rect_tool == bars.last_active_tool) {
            if (bars.last_active_bar) {
                bars.last_active_bar.opacity = 0
            }
            if (rect_bar) {
                rect_bar.opacity = 0;
            }
            options_bar.opacity = 0;
            bars.last_active_tool = null;
            bars.last_active_bar = null;
        } else if (bars.last_active_tool) {
            bars.last_active_tool.isCurrentItem = !bars.last_active_tool.isCurrentItem;
            if (bars.last_active_bar) {
                bars.last_active_bar.opacity = 0;
            }
            options_bar.opacity = 0
        }
        if (rect_tool.isCurrentItem) {
            bars.last_active_tool = rect_tool;
            bars.last_active_bar = rect_bar;
            if (rect_bar) {
                rect_bar.opacity = 1;
                options_bar.opacity = 1;
            }
        }

    }

    function unsetActive() {
        if (bars.last_active_tool) {
            bars.last_active_tool.isCurrentItem = false;
        }
        bars.last_active_tool = null;
        bars.last_active_bar = null;
    }

    function setScales(scaleX, scaleY, scaleZ, sizeX, sizeY, sizeZ) {
        text_input_scaleX.text = scaleX;
        text_input_scaleY.text = scaleY;
        text_input_scaleZ.text = scaleZ;

        text_input_sizeX.text = sizeX;
        text_input_sizeY.text = sizeY;
        text_input_sizeZ.text = sizeZ;
    }

}
