import QtQuick 1.0

Rectangle {
    id: options_layer
    width: 700
    height: 0.8*parent.height
    color: "#51545b"
    enabled: false
    opacity: 0

    property int line_width: 230
    property int line_height: 25
    property int input_width: 70
    property int row_spacing: 3

    Rectangle {
        id: header
        x: 0
        y: 0
        width: parent.width
        height: 34
        color: "#00000000"

        Text {
            id: title
            color: "#ffffff"
            text: qsTr("Slicing options")
            verticalAlignment: Text.AlignVCenter
            anchors.fill: parent
            horizontalAlignment: Text.AlignHCenter
            font.pixelSize: 15
            font.family: lato_font.name
        }
    }

    Rectangle {
        id: close
        width: 30
        height: 24
        color: "#333333"
        anchors.top: parent.top
        anchors.topMargin: 0
        anchors.right: parent.right
        anchors.rightMargin: 10

        MouseArea {
            id: mouse_area_close
            anchors.fill: parent
            onClicked: {
                options_layer.hideLayer();
            }

            Image {
                id: image_close
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                source: "resources/icons/close.png"
            }
        }
    }

    Rectangle {
        id: grid1
        x: 0
        width: parent.width
        height: parent.height - header.height
        anchors.top: parent.top
        anchors.topMargin: header.height
        color: "#00000000"

        // Enable scrolling
        Flickable {
            id: view
            anchors.fill: parent
            contentWidth: 700
            contentHeight: 880
            clip: true

            Rectangle {
                id: row_tabs
                color: "#00000000"
                width: parent.width
                height: 30
                anchors.left: parent.left
                anchors.leftMargin: row_options.padding

                Rectangle {
                    id: tab_options
                    x: 0
                    y: 0
                    width: 133
                    height: parent.height
                    color: active ? "#5d6169" : "#3f4245"

                    property bool active: true

                    Text {
                        id: text2
                        color: "#ffffff"
                        text: qsTr("Options")
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.pixelSize: 13
                        anchors.fill: parent
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            tab_options.active = true;
                            tab_gcodes.active = false;
                        }
                    }
                }

                Rectangle {
                    id: tab_gcodes
                    width: 133
                    height: parent.height
                    color: active ? "#5d6169" : "#3f4245"
                    anchors.left: tab_options.right
                    anchors.leftMargin: 0

                    property bool active: false

                    Text {
                        id: text3
                        color: "#ffffff"
                        text: qsTr("Start/End gcode")
                        height: parent.height
                        font.pixelSize: 13
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        anchors.fill: parent
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            tab_gcodes.active = true;
                            tab_options.active = false;
                        }
                    }
                }
            }

            Rectangle {
                id: row_options
                objectName: "row_options"
                color: "#5d6169"
                width: parent.width
                height: parent.height - row_tabs.height
                anchors.top: row_tabs.bottom
                anchors.topMargin: 0
                anchors.left: parent.left
                anchors.leftMargin: row_options.padding/2
                anchors.right: parent.right
                anchors.rightMargin: row_options.padding/2
                opacity: tab_options.active ? 1 : 0

                property int padding: 50
                property Item current_input: null

                Rectangle {
                    id: column_left
                    color: "#00000000"
                    width: (parent.width - 2*row_options.padding) / 2
                    height: parent.height
                    anchors.left: parent.left
                    anchors.leftMargin: row_options.padding
                    anchors.top: parent.top
                    anchors.topMargin: 10

                    Text {
                        id: title_layer
                        color: "#ffffff"
                        text: qsTr("Layer")
                        anchors.left: parent.left
                        anchors.leftMargin: 0
                        anchors.top: parent.top
                        anchors.topMargin: row_spacing
                        font.pixelSize: 13
                        font.bold: true
                        font.family: lato_font.name
                    }

                    Rectangle {
                        id: rect_layer_height
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: title_layer.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_layer_height
                            color: "#a8a8a8"
                            text: qsTr("Layer height")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: layer_height
                            width: options_layer.input_width
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter

                            TextInput {
                                id: text_input_layer_height
                                objectName: "layer_height"
                                height: parent.height
                                anchors.top: parent.top
                                anchors.topMargin: 3
                                anchors.right: text_mm_layer_height.left
                                anchors.rightMargin: 3
                                anchors.left: parent.left
                                anchors.leftMargin: 4
                                color: "#d1d1d2"
                                font.family: "Lato"
                                font.pixelSize: 11
                                horizontalAlignment: TextInput.AlignHCenter
                                validator: DoubleValidator{bottom: 0;}
                                readOnly: false
                                cursorVisible: row_options.current_input == text_input_layer_height
                                Keys.onPressed: {
                                    if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                                        mainwindow.onFloatSettingChange(text_input_layer_height.objectName, text)
                                    }
                                }
                            }

                            Text {
                                id: text_mm_layer_height
                                height: parent.height
                                width: 22
                                text: qsTr("mm")
                                color: "#d1d1d2"
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
                                    text_input_layer_height.forceActiveFocus();
                                    row_options.current_input = text_input_layer_height;
                                }
                            }
                        }
                    }

                    Text {
                        id: title_shell
                        color: "#ffffff"
                        text: qsTr("Shell")
                        anchors.left: parent.left
                        anchors.leftMargin: 0
                        anchors.top: rect_layer_height.bottom
                        anchors.topMargin: row_spacing * 4
                        font.pixelSize: 13
                        font.bold: true
                        font.family: lato_font.name
                    }

                    Rectangle {
                        id: rect_wall_thickness
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: title_shell.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_wall_thickness
                            color: "#a8a8a8"
                            text: qsTr("Shell thickness")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: wall_thickness
                            width: options_layer.input_width
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter

                            TextInput {
                                id: text_input_wall_thickness
                                objectName: "wall_thickness"
                                height: parent.height
                                anchors.top: parent.top
                                anchors.topMargin: 3
                                anchors.right: text_mm_wall_thickness.left
                                anchors.rightMargin: 3
                                anchors.left: parent.left
                                anchors.leftMargin: 4
                                color: "#d1d1d2"
                                font.family: "Lato"
                                font.pixelSize: 11
                                horizontalAlignment: TextInput.AlignHCenter
                                validator: DoubleValidator{bottom: 0;}
                                readOnly: false
                                cursorVisible: row_options.current_input == text_input_wall_thickness
                                Keys.onPressed: {
                                    if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                                        mainwindow.onFloatSettingChange(text_input_wall_thickness.objectName, text)
                                    }
                                }
                            }

                            Text {
                                id: text_mm_wall_thickness
                                height: parent.height
                                width: 22
                                text: qsTr("mm")
                                color: "#d1d1d2"
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
                                    text_input_wall_thickness.forceActiveFocus();
                                    row_options.current_input = text_input_wall_thickness;
                                }
                            }
                        }
                    }

                    Rectangle {
                        id: rect_solid_layer_thickness
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: rect_wall_thickness.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_solid_layer_thickness
                            color: "#a8a8a8"
                            text: qsTr("Bottom/Top thickness")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: solid_layer_thickness
                            width: options_layer.input_width
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter

                            TextInput {
                                id: text_input_solid_layer_thickness
                                objectName: "solid_layer_thickness"
                                height: parent.height
                                anchors.top: parent.top
                                anchors.topMargin: 3
                                anchors.right: text_mm_solid_layer_thickness.left
                                anchors.rightMargin: 3
                                anchors.left: parent.left
                                anchors.leftMargin: 4
                                color: "#d1d1d2"
                                font.family: "Lato"
                                font.pixelSize: 11
                                horizontalAlignment: TextInput.AlignHCenter
                                validator: DoubleValidator{bottom: 0;}
                                readOnly: false
                                cursorVisible: row_options.current_input == text_input_solid_layer_thickness
                                Keys.onPressed: {
                                    if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                                        mainwindow.onFloatSettingChange(text_input_solid_layer_thickness.objectName, text)
                                    }
                                }
                            }

                            Text {
                                id: text_mm_solid_layer_thickness
                                height: parent.height
                                width: 22
                                text: qsTr("mm")
                                color: "#d1d1d2"
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
                                    text_input_solid_layer_thickness.forceActiveFocus();
                                    row_options.current_input = text_input_solid_layer_thickness;
                                }
                            }
                        }
                    }

                    Rectangle {
                        id: rect_bottom_thickness
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: rect_solid_layer_thickness.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_bottom_thickness
                            color: "#a8a8a8"
                            text: qsTr("Initial layer thickness")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: bottom_thickness
                            width: options_layer.input_width
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter

                            TextInput {
                                id: text_input_bottom_thickness
                                objectName: "bottom_thickness"
                                height: parent.height
                                anchors.top: parent.top
                                anchors.topMargin: 3
                                anchors.right: text_mm_bottom_thickness.left
                                anchors.rightMargin: 3
                                anchors.left: parent.left
                                anchors.leftMargin: 4
                                color: "#d1d1d2"
                                font.family: "Lato"
                                font.pixelSize: 11
                                horizontalAlignment: TextInput.AlignHCenter
                                validator: DoubleValidator{bottom: 0;}
                                readOnly: false
                                cursorVisible: row_options.current_input == text_input_bottom_thickness
                                Keys.onPressed: {
                                    if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                                        mainwindow.onFloatSettingChange(text_input_bottom_thickness.objectName, text)
                                    }
                                }
                            }

                            Text {
                                id: text_mm_bottom_thickness
                                height: parent.height
                                width: 22
                                text: qsTr("mm")
                                color: "#d1d1d2"
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
                                    text_input_bottom_thickness.forceActiveFocus();
                                    row_options.current_input = text_input_bottom_thickness;
                                }
                            }
                        }
                    }

                    Rectangle {
                        id: rect_layer0_width_factor
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: rect_bottom_thickness.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_layer0_width_factor
                            color: "#a8a8a8"
                            text: qsTr("Initial layer line with")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: layer0_width_factor
                            width: options_layer.input_width
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter

                            TextInput {
                                id: text_input_layer0_width_factor
                                objectName: "layer0_width_factor"
                                height: parent.height
                                anchors.top: parent.top
                                anchors.topMargin: 3
                                anchors.right: text_mm_layer0_width_factor.left
                                anchors.rightMargin: 3
                                anchors.left: parent.left
                                anchors.leftMargin: 4
                                color: "#d1d1d2"
                                font.family: "Lato"
                                font.pixelSize: 11
                                horizontalAlignment: TextInput.AlignHCenter
                                validator: DoubleValidator{bottom: 0;}
                                readOnly: false
                                cursorVisible: row_options.current_input == text_input_layer0_width_factor
                                Keys.onPressed: {
                                    if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                                        mainwindow.onFloatSettingChange(text_input_layer0_width_factor.objectName, text)
                                    }
                                }
                            }

                            Text {
                                id: text_mm_layer0_width_factor
                                height: parent.height
                                width: 22
                                text: qsTr("%")
                                color: "#d1d1d2"
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
                                    text_input_layer0_width_factor.forceActiveFocus();
                                    row_options.current_input = text_input_layer0_width_factor;
                                }
                            }
                        }
                    }

                    Rectangle {
                        id: rect_simple_mode
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: rect_layer0_width_factor.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_simple_mode
                            color: "#a8a8a8"
                            text: qsTr("Only follow mesh surface")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: simple_mode
                            objectName: "simple_mode"
                            width: 20
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            property bool isActive: false

                            MouseArea {
                                id: mouse_area_simple_mode
                                anchors.fill: parent
                                onClicked: {
                                    simple_mode.isActive = !simple_mode.isActive
                                    mainwindow.onBoolSettingChange(simple_mode.objectName, simple_mode.isActive)
                                }

                                Image {
                                    id: image_simple_mode
                                    opacity: simple_mode.isActive ? 1 : 0
                                    anchors.horizontalCenter: parent.horizontalCenter
                                    anchors.verticalCenter: parent.verticalCenter
                                    source: "resources/icons/checked.png"
                                }
                            }

                        }
                    }

                    Rectangle {
                        id: rect_spiralize
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: rect_simple_mode.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_spiralize
                            color: "#a8a8a8"
                            text: qsTr("Spiralize the outer contour")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: spiralize
                            objectName: "spiralize"
                            width: 20
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            property bool isActive: false

                            MouseArea {
                                id: mouse_area_spiralize
                                anchors.fill: parent
                                onClicked: {
                                    spiralize.isActive = !spiralize.isActive
                                    mainwindow.onBoolSettingChange(spiralize.objectName, spiralize.isActive)
                                }

                                Image {
                                    id: image_spiralize
                                    opacity: spiralize.isActive ? 1 : 0
                                    anchors.horizontalCenter: parent.horizontalCenter
                                    anchors.verticalCenter: parent.verticalCenter
                                    source: "resources/icons/checked.png"
                                }
                            }

                        }
                    }

                    Text {
                        id: title_temperature
                        color: "#ffffff"
                        text: qsTr("Temperature")
                        anchors.left: parent.left
                        anchors.leftMargin: 0
                        anchors.top: rect_spiralize.bottom
                        anchors.topMargin: row_spacing * 4
                        font.pixelSize: 13
                        font.bold: true
                        font.family: lato_font.name
                    }

                    Rectangle {
                        id: rect_print_temperature
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: title_temperature.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_print_temperature
                            color: "#a8a8a8"
                            text: qsTr("Printing temperature")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: print_temperature
                            width: options_layer.input_width
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter

                            TextInput {
                                id: text_input_print_temperature
                                objectName: "print_temperature"
                                height: parent.height
                                anchors.top: parent.top
                                anchors.topMargin: 3
                                anchors.right: text_mm_print_temperature.left
                                anchors.rightMargin: 3
                                anchors.left: parent.left
                                anchors.leftMargin: 4
                                color: "#d1d1d2"
                                font.family: "Lato"
                                font.pixelSize: 11
                                horizontalAlignment: TextInput.AlignHCenter
                                validator: IntValidator{bottom: 0; top: 340;}
                                readOnly: false
                                cursorVisible: row_options.current_input == text_input_print_temperature
                                Keys.onPressed: {
                                    if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                                        mainwindow.onFloatSettingChange(text_input_print_temperature.objectName, text)
                                    }
                                }
                            }

                            Text {
                                id: text_mm_print_temperature
                                height: parent.height
                                width: 22
                                text: qsTr("C")
                                color: "#d1d1d2"
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
                                    text_input_print_temperature.forceActiveFocus();
                                    row_options.current_input = text_input_print_temperature;
                                }
                            }
                        }
                    }

                    Rectangle {
                        id: rect_print_temperature_2
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: rect_print_temperature.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_print_temperature_2
                            color: "#a8a8a8"
                            text: qsTr("2nd nozzle temperature")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: print_temperature_2
                            width: options_layer.input_width
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter

                            TextInput {
                                id: text_input_print_temperature_2
                                objectName: "print_temperature2"
                                height: parent.height
                                anchors.top: parent.top
                                anchors.topMargin: 3
                                anchors.right: text_mm_print_temperature_2.left
                                anchors.rightMargin: 3
                                anchors.left: parent.left
                                anchors.leftMargin: 4
                                color: "#d1d1d2"
                                font.family: "Lato"
                                font.pixelSize: 11
                                horizontalAlignment: TextInput.AlignHCenter
                                validator: IntValidator{bottom: 0; top: 340;}
                                readOnly: false
                                cursorVisible: row_options.current_input == text_input_print_temperature_2
                                Keys.onPressed: {
                                    if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                                        mainwindow.onFloatSettingChange(text_input_print_temperature_2.objectName, text)
                                    }
                                }
                            }

                            Text {
                                id: text_mm_print_temperature_2
                                height: parent.height
                                width: 22
                                text: qsTr("C")
                                color: "#d1d1d2"
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
                                    text_input_print_temperature_2.forceActiveFocus();
                                    row_options.current_input = text_input_print_temperature_2;
                                }
                            }
                        }
                    }

                    Rectangle {
                        id: rect_print_bed_temperature
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: rect_print_temperature_2.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_print_bed_temperature
                            color: "#a8a8a8"
                            text: qsTr("Bed temperature")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: print_bed_temperature
                            width: options_layer.input_width
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter

                            TextInput {
                                id: text_input_print_bed_temperature
                                objectName: "print_bed_temperature"
                                height: parent.height
                                anchors.top: parent.top
                                anchors.topMargin: 3
                                anchors.right: text_mm_print_bed_temperature.left
                                anchors.rightMargin: 3
                                anchors.left: parent.left
                                anchors.leftMargin: 4
                                color: "#d1d1d2"
                                font.family: "Lato"
                                font.pixelSize: 11
                                horizontalAlignment: TextInput.AlignHCenter
                                validator: IntValidator{bottom: 0; top: 340;}
                                readOnly: false
                                cursorVisible: row_options.current_input == text_input_print_bed_temperature
                                Keys.onPressed: {
                                    if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                                        mainwindow.onFloatSettingChange(text_input_print_bed_temperature.objectName, text)
                                    }
                                }
                            }

                            Text {
                                id: text_mm_print_bed_temperature
                                height: parent.height
                                width: 22
                                text: qsTr("C")
                                color: "#d1d1d2"
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
                                    text_input_print_bed_temperature.forceActiveFocus();
                                    row_options.current_input = text_input_print_bed_temperature;
                                }
                            }
                        }
                    }

                    Text {
                        id: title_fan
                        color: "#ffffff"
                        text: qsTr("Fan")
                        anchors.left: parent.left
                        anchors.leftMargin: 0
                        anchors.top: rect_print_bed_temperature.bottom
                        anchors.topMargin: row_spacing * 4
                        font.pixelSize: 13
                        font.bold: true
                        font.family: lato_font.name
                    }

                    Rectangle {
                        id: rect_fan_enabled
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: title_fan.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_fan_enabled
                            color: "#a8a8a8"
                            text: qsTr("Enable cooling fan")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: fan_enabled
                            objectName: "fan_enabled"
                            width: 20
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            property bool isActive: false

                            MouseArea {
                                id: mouse_area_fan_enabled
                                anchors.fill: parent
                                onClicked: {
                                    fan_enabled.isActive = !fan_enabled.isActive
                                    mainwindow.onBoolSettingChange(fan_enabled.objectName, fan_enabled.isActive)
                                }

                                Image {
                                    id: image_fan_enabled
                                    opacity: fan_enabled.isActive ? 1 : 0
                                    anchors.horizontalCenter: parent.horizontalCenter
                                    anchors.verticalCenter: parent.verticalCenter
                                    source: "resources/icons/checked.png"
                                }
                            }

                        }
                    }

                    Rectangle {
                        id: rect_cool_min_layer_time
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: rect_fan_enabled.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_cool_min_layer_time
                            color: "#a8a8a8"
                            text: qsTr("Minimal layer time")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: cool_min_layer_time
                            width: options_layer.input_width
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter

                            TextInput {
                                id: text_input_cool_min_layer_time
                                objectName: "cool_min_layer_time"
                                height: parent.height
                                anchors.top: parent.top
                                anchors.topMargin: 3
                                anchors.right: text_mm_cool_min_layer_time.left
                                anchors.rightMargin: 3
                                anchors.left: parent.left
                                anchors.leftMargin: 4
                                color: "#d1d1d2"
                                font.family: "Lato"
                                font.pixelSize: 11
                                horizontalAlignment: TextInput.AlignHCenter
                                validator: DoubleValidator{bottom: 0;}
                                readOnly: false
                                cursorVisible: row_options.current_input == text_input_cool_min_layer_time
                                Keys.onPressed: {
                                    if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                                        mainwindow.onFloatSettingChange(text_input_cool_min_layer_time.objectName, text)
                                    }
                                }
                            }

                            Text {
                                id: text_mm_cool_min_layer_time
                                height: parent.height
                                width: 22
                                text: qsTr("sec")
                                color: "#d1d1d2"
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
                                    text_input_cool_min_layer_time.forceActiveFocus();
                                    row_options.current_input = text_input_cool_min_layer_time;
                                }
                            }
                        }
                    }

                    Rectangle {
                        id: rect_fan_full_height
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: rect_cool_min_layer_time.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_fan_full_height
                            color: "#a8a8a8"
                            text: qsTr("Fan full on at height")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: fan_full_height
                            width: options_layer.input_width
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter

                            TextInput {
                                id: text_input_fan_full_height
                                objectName: "fan_full_height"
                                height: parent.height
                                anchors.top: parent.top
                                anchors.topMargin: 3
                                anchors.right: text_mm_fan_full_height.left
                                anchors.rightMargin: 3
                                anchors.left: parent.left
                                anchors.leftMargin: 4
                                color: "#d1d1d2"
                                font.family: "Lato"
                                font.pixelSize: 11
                                horizontalAlignment: TextInput.AlignHCenter
                                validator: DoubleValidator{bottom: 0;}
                                readOnly: false
                                cursorVisible: row_options.current_input == text_input_fan_full_height
                                Keys.onPressed: {
                                    if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                                        mainwindow.onFloatSettingChange(text_input_fan_full_height.objectName, text)
                                    }
                                }
                            }

                            Text {
                                id: text_mm_fan_full_height
                                height: parent.height
                                width: 22
                                text: qsTr("mm")
                                color: "#d1d1d2"
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
                                    text_input_fan_full_height.forceActiveFocus();
                                    row_options.current_input = text_input_fan_full_height;
                                }
                            }
                        }
                    }

                    Rectangle {
                        id: rect_fan_speed
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: rect_fan_full_height.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_fan_speed
                            color: "#a8a8a8"
                            text: qsTr("Fan speed min")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: fan_speed
                            width: options_layer.input_width
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter

                            TextInput {
                                id: text_input_fan_speed
                                objectName: "fan_speed"
                                height: parent.height
                                anchors.top: parent.top
                                anchors.topMargin: 3
                                anchors.right: text_mm_fan_speed.left
                                anchors.rightMargin: 3
                                anchors.left: parent.left
                                anchors.leftMargin: 4
                                color: "#d1d1d2"
                                font.family: "Lato"
                                font.pixelSize: 11
                                horizontalAlignment: TextInput.AlignHCenter
                                validator: IntValidator{bottom: 0; top: 100;}
                                readOnly: false
                                cursorVisible: row_options.current_input == text_input_fan_speed
                                Keys.onPressed: {
                                    if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                                        mainwindow.onFloatSettingChange(text_input_fan_speed.objectName, text)
                                    }
                                }
                            }

                            Text {
                                id: text_mm_fan_speed
                                height: parent.height
                                width: 22
                                text: qsTr("%")
                                color: "#d1d1d2"
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
                                    text_input_fan_speed.forceActiveFocus();
                                    row_options.current_input = text_input_fan_speed;
                                }
                            }
                        }
                    }

                    Rectangle {
                        id: rect_fan_speed_max
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: rect_fan_speed.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_fan_speed_max
                            color: "#a8a8a8"
                            text: qsTr("Fan speed max")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: fan_speed_max
                            width: options_layer.input_width
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter

                            TextInput {
                                id: text_input_fan_speed_max
                                objectName: "fan_speed_max"
                                height: parent.height
                                anchors.top: parent.top
                                anchors.topMargin: 3
                                anchors.right: text_mm_fan_speed_max.left
                                anchors.rightMargin: 3
                                anchors.left: parent.left
                                anchors.leftMargin: 4
                                color: "#d1d1d2"
                                font.family: "Lato"
                                font.pixelSize: 11
                                horizontalAlignment: TextInput.AlignHCenter
                                validator: IntValidator{bottom: 0; top: 100;}
                                readOnly: false
                                cursorVisible: row_options.current_input == text_input_fan_speed_max
                                Keys.onPressed: {
                                    if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                                        mainwindow.onFloatSettingChange(text_input_fan_speed_max.objectName, text)
                                    }
                                }
                            }

                            Text {
                                id: text_mm_fan_speed_max
                                height: parent.height
                                width: 22
                                text: qsTr("%")
                                color: "#d1d1d2"
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
                                    text_input_fan_speed_max.forceActiveFocus();
                                    row_options.current_input = text_input_fan_speed_max;
                                }
                            }
                        }
                    }

                    Rectangle {
                        id: rect_cool_min_feedrate
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: rect_fan_speed_max.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_cool_min_feedrate
                            color: "#a8a8a8"
                            text: qsTr("Minimum speed")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: cool_min_feedrate
                            width: options_layer.input_width
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter

                            TextInput {
                                id: text_input_cool_min_feedrate
                                objectName: "cool_min_feedrate"
                                height: parent.height
                                anchors.top: parent.top
                                anchors.topMargin: 3
                                anchors.right: text_mm_cool_min_feedrate.left
                                anchors.rightMargin: 3
                                anchors.left: parent.left
                                anchors.leftMargin: 4
                                color: "#d1d1d2"
                                font.family: "Lato"
                                font.pixelSize: 11
                                horizontalAlignment: TextInput.AlignHCenter
                                validator: DoubleValidator{bottom: 0;}
                                readOnly: false
                                cursorVisible: row_options.current_input == text_input_cool_min_feedrate
                                Keys.onPressed: {
                                    if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                                        mainwindow.onFloatSettingChange(text_input_cool_min_feedrate.objectName, text)
                                    }
                                }
                            }

                            Text {
                                id: text_mm_cool_min_feedrate
                                height: parent.height
                                width: 22
                                text: qsTr("mm/s")
                                color: "#d1d1d2"
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
                                    text_input_cool_min_feedrate.forceActiveFocus();
                                    row_options.current_input = text_input_cool_min_feedrate;
                                }
                            }
                        }
                    }

                    Rectangle {
                        id: rect_cool_head_lift
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: rect_cool_min_feedrate.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_cool_head_lift
                            color: "#a8a8a8"
                            text: qsTr("Cool head lift")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: cool_head_lift
                            objectName: "cool_head_lift"
                            width: 20
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            property bool isActive: false

                            MouseArea {
                                id: mouse_area_cool_head_lift
                                anchors.fill: parent
                                onClicked: {
                                    cool_head_lift.isActive = !cool_head_lift.isActive
                                    mainwindow.onBoolSettingChange(cool_head_lift.objectName, cool_head_lift.isActive)
                                }

                                Image {
                                    id: image_cool_head_lift
                                    opacity: cool_head_lift.isActive ? 1 : 0
                                    anchors.horizontalCenter: parent.horizontalCenter
                                    anchors.verticalCenter: parent.verticalCenter
                                    source: "resources/icons/checked.png"
                                }
                            }

                        }
                    }

                    Text {
                        id: title_misc
                        color: "#ffffff"
                        text: qsTr("Misc")
                        anchors.left: parent.left
                        anchors.leftMargin: 0
                        anchors.top: rect_cool_head_lift.bottom
                        anchors.topMargin: row_spacing * 4
                        font.pixelSize: 13
                        font.bold: true
                        font.family: lato_font.name
                    }

                    Rectangle {
                        id: rect_object_sink
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: title_misc.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_object_sink
                            color: "#a8a8a8"
                            text: qsTr("Cut off object bottom")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: object_sink
                            width: options_layer.input_width
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter

                            TextInput {
                                id: text_input_object_sink
                                objectName: "object_sink"
                                height: parent.height
                                anchors.top: parent.top
                                anchors.topMargin: 3
                                anchors.right: text_mm_object_sink.left
                                anchors.rightMargin: 3
                                anchors.left: parent.left
                                anchors.leftMargin: 4
                                color: "#d1d1d2"
                                font.family: "Lato"
                                font.pixelSize: 11
                                horizontalAlignment: TextInput.AlignHCenter
                                validator: DoubleValidator{bottom: 0;}
                                readOnly: false
                                cursorVisible: row_options.current_input == text_input_object_sink
                                Keys.onPressed: {
                                    if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                                        mainwindow.onFloatSettingChange(text_input_object_sink.objectName, text)
                                    }
                                }
                            }

                            Text {
                                id: text_mm_object_sink
                                height: parent.height
                                width: 22
                                text: qsTr("mm")
                                color: "#d1d1d2"
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
                                    text_input_object_sink.forceActiveFocus();
                                    row_options.current_input = text_input_object_sink;
                                }
                            }
                        }
                    }

                    Rectangle {
                        id: rect_filament_flow
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: rect_object_sink.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_filament_flow
                            color: "#a8a8a8"
                            text: qsTr("Flow")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: filament_flow
                            width: options_layer.input_width
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter

                            TextInput {
                                id: text_input_filament_flow
                                objectName: "filament_flow"
                                height: parent.height
                                anchors.top: parent.top
                                anchors.topMargin: 3
                                anchors.right: text_mm_filament_flow.left
                                anchors.rightMargin: 3
                                anchors.left: parent.left
                                anchors.leftMargin: 4
                                color: "#d1d1d2"
                                font.family: "Lato"
                                font.pixelSize: 11
                                horizontalAlignment: TextInput.AlignHCenter
                                validator: DoubleValidator{bottom: 5; top: 300;}
                                readOnly: false
                                cursorVisible: row_options.current_input == text_input_filament_flow
                                Keys.onPressed: {
                                    if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                                        mainwindow.onFloatSettingChange(text_input_filament_flow.objectName, text)
                                    }
                                }
                            }

                            Text {
                                id: text_mm_filament_flow
                                height: parent.height
                                width: 22
                                text: qsTr("%")
                                color: "#d1d1d2"
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
                                    text_input_filament_flow.forceActiveFocus();
                                    row_options.current_input = text_input_filament_flow;
                                }
                            }
                        }
                    }

                    Rectangle {
                        id: rect_fix_horrible_union_all_type_a
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: rect_filament_flow.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_fix_horrible_union_all_type_a
                            color: "#a8a8a8"
                            text: qsTr("Combine everything (Type-A)")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: fix_horrible_union_all_type_a
                            objectName: "fix_horrible_union_all_type_a"
                            width: 20
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            property bool isActive: false

                            MouseArea {
                                id: mouse_area_fix_horrible_union_all_type_a
                                anchors.fill: parent
                                onClicked: {
                                    fix_horrible_union_all_type_a.isActive = !fix_horrible_union_all_type_a.isActive
                                    mainwindow.onBoolSettingChange(fix_horrible_union_all_type_a.objectName, fix_horrible_union_all_type_a.isActive)
                                }

                                Image {
                                    id: image_fix_horrible_union_all_type_a
                                    opacity: fix_horrible_union_all_type_a.isActive ? 1 : 0
                                    anchors.horizontalCenter: parent.horizontalCenter
                                    anchors.verticalCenter: parent.verticalCenter
                                    source: "resources/icons/checked.png"
                                }
                            }

                        }
                    }

                    Rectangle {
                        id: rect_fix_horrible_union_all_type_b
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: rect_fix_horrible_union_all_type_a.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_fix_horrible_union_all_type_b
                            color: "#a8a8a8"
                            text: qsTr("Combine everything (Type-B)")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: fix_horrible_union_all_type_b
                            objectName: "fix_horrible_union_all_type_b"
                            width: 20
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            property bool isActive: false

                            MouseArea {
                                id: mouse_area_fix_horrible_union_all_type_b
                                anchors.fill: parent
                                onClicked: {
                                    fix_horrible_union_all_type_b.isActive = !fix_horrible_union_all_type_b.isActive
                                    mainwindow.onBoolSettingChange(fix_horrible_union_all_type_b.objectName, fix_horrible_union_all_type_b.isActive)
                                }

                                Image {
                                    id: image_fix_horrible_union_all_type_b
                                    opacity: fix_horrible_union_all_type_b.isActive ? 1 : 0
                                    anchors.horizontalCenter: parent.horizontalCenter
                                    anchors.verticalCenter: parent.verticalCenter
                                    source: "resources/icons/checked.png"
                                }
                            }

                        }
                    }

                    Rectangle {
                        id: rect_fix_horrible_use_open_bits
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: rect_fix_horrible_union_all_type_b.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_fix_horrible_use_open_bits
                            color: "#a8a8a8"
                            text: qsTr("Keep open faces")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: fix_horrible_use_open_bits
                            objectName: "fix_horrible_use_open_bits"
                            width: 20
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            property bool isActive: false

                            MouseArea {
                                id: mouse_area_fix_horrible_use_open_bits
                                anchors.fill: parent
                                onClicked: {
                                    fix_horrible_use_open_bits.isActive = !fix_horrible_use_open_bits.isActive
                                    mainwindow.onBoolSettingChange(fix_horrible_use_open_bits.objectName, fix_horrible_use_open_bits.isActive)
                                }

                                Image {
                                    id: image_fix_horrible_use_open_bits
                                    opacity: fix_horrible_use_open_bits.isActive ? 1 : 0
                                    anchors.horizontalCenter: parent.horizontalCenter
                                    anchors.verticalCenter: parent.verticalCenter
                                    source: "resources/icons/checked.png"
                                }
                            }

                        }
                    }

                    Rectangle {
                        id: rect_fix_horrible_extensive_stitching
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: rect_fix_horrible_use_open_bits.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_fix_horrible_extensive_stitching
                            color: "#a8a8a8"
                            text: qsTr("Extensive stitching")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: fix_horrible_extensive_stitching
                            objectName: "fix_horrible_extensive_stitching"
                            width: 20
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            property bool isActive: false

                            MouseArea {
                                id: mouse_area_fix_horrible_extensive_stitching
                                anchors.fill: parent
                                onClicked: {
                                    fix_horrible_extensive_stitching.isActive = !fix_horrible_extensive_stitching.isActive
                                    mainwindow.onBoolSettingChange(fix_horrible_extensive_stitching.objectName, fix_horrible_extensive_stitching.isActive)
                                }

                                Image {
                                    id: image_fix_horrible_extensive_stitching
                                    opacity: fix_horrible_extensive_stitching.isActive ? 1 : 0
                                    anchors.horizontalCenter: parent.horizontalCenter
                                    anchors.verticalCenter: parent.verticalCenter
                                    source: "resources/icons/checked.png"
                                }
                            }

                        }
                    }

                }

                Rectangle {
                    id: column_right
                    color: "#00000000"
                    width: (parent.width - 2*row_options.padding) / 2
                    height: parent.height
                    anchors.right: parent.right
                    anchors.rightMargin: row_options.padding
                    anchors.left: column_left.right
                    anchors.leftMargin: 40
                    anchors.top: parent.top
                    anchors.topMargin: 10

                    Text {
                        id: title_retract
                        color: "#ffffff"
                        text: qsTr("Retraction")
                        anchors.left: parent.left
                        anchors.leftMargin: 0
                        anchors.top: parent.top
                        anchors.topMargin: row_spacing
                        font.pixelSize: 13
                        font.bold: true
                        font.family: lato_font.name
                    }

                    Rectangle {
                        id: rect_retraction_enable
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: title_retract.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_retraction_enable
                            color: "#a8a8a8"
                            text: qsTr("Enable retraction")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: retraction_enable
                            objectName: "retraction_enable"
                            width: 20
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            property bool isActive: false

                            MouseArea {
                                id: mouse_area_retraction_enable
                                anchors.fill: parent
                                onClicked: {
                                    retraction_enable.isActive = !retraction_enable.isActive
                                    mainwindow.onBoolSettingChange(retraction_enable.objectName, retraction_enable.isActive)
                                }

                                Image {
                                    id: image_retraction_enable
                                    opacity: retraction_enable.isActive ? 1 : 0
                                    anchors.horizontalCenter: parent.horizontalCenter
                                    anchors.verticalCenter: parent.verticalCenter
                                    source: "resources/icons/checked.png"
                                }
                            }

                        }
                    }

                    Rectangle {
                        id: rect_retraction_speed
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: rect_retraction_enable.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_retraction_speed
                            color: "#a8a8a8"
                            text: qsTr("Speed")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: retraction_speed
                            width: options_layer.input_width
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter

                            TextInput {
                                id: text_input_retraction_speed
                                objectName: "retraction_speed"
                                height: parent.height
                                anchors.top: parent.top
                                anchors.topMargin: 3
                                anchors.right: text_mm_retraction_speed.left
                                anchors.rightMargin: 3
                                anchors.left: parent.left
                                anchors.leftMargin: 4
                                color: "#d1d1d2"
                                font.family: "Lato"
                                font.pixelSize: 11
                                horizontalAlignment: TextInput.AlignHCenter
                                validator: DoubleValidator{bottom: 0.1;}
                                readOnly: false
                                cursorVisible: row_options.current_input == text_input_retraction_speed
                                Keys.onPressed: {
                                    if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                                        mainwindow.onFloatSettingChange(text_input_retraction_speed.objectName, text)
                                    }
                                }
                            }

                            Text {
                                id: text_mm_retraction_speed
                                height: parent.height
                                width: 22
                                text: qsTr("mm/s")
                                color: "#d1d1d2"
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
                                    text_input_retraction_speed.forceActiveFocus();
                                    row_options.current_input = text_input_retraction_speed;
                                }
                            }
                        }
                    }

                    Rectangle {
                        id: rect_retraction_min_travel
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: rect_retraction_speed.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_retraction_min_travel
                            color: "#a8a8a8"
                            text: qsTr("Minimum travel")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: retraction_min_travel
                            width: options_layer.input_width
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter

                            TextInput {
                                id: text_input_retraction_min_travel
                                objectName: "retraction_min_travel"
                                height: parent.height
                                anchors.top: parent.top
                                anchors.topMargin: 3
                                anchors.right: text_mm_retraction_min_travel.left
                                anchors.rightMargin: 3
                                anchors.left: parent.left
                                anchors.leftMargin: 4
                                color: "#d1d1d2"
                                font.family: "Lato"
                                font.pixelSize: 11
                                horizontalAlignment: TextInput.AlignHCenter
                                validator: DoubleValidator{bottom: 0;}
                                readOnly: false
                                cursorVisible: row_options.current_input == text_input_retraction_min_travel
                                Keys.onPressed: {
                                    if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                                        mainwindow.onFloatSettingChange(text_input_retraction_min_travel.objectName, text)
                                    }
                                }
                            }

                            Text {
                                id: text_mm_retraction_min_travel
                                height: parent.height
                                width: 22
                                text: qsTr("mm")
                                color: "#d1d1d2"
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
                                    text_input_retraction_min_travel.forceActiveFocus();
                                    row_options.current_input = text_input_retraction_min_travel;
                                }
                            }
                        }
                    }

                    Rectangle {
                        id: rect_retraction_dual_amount
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: rect_retraction_min_travel.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_retraction_dual_amount
                            color: "#a8a8a8"
                            text: qsTr("Dual extrusion switch amount")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: retraction_dual_amount
                            width: options_layer.input_width
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter

                            TextInput {
                                id: text_input_retraction_dual_amount
                                objectName: "retraction_dual_amount"
                                height: parent.height
                                anchors.top: parent.top
                                anchors.topMargin: 3
                                anchors.right: text_mm_retraction_dual_amount.left
                                anchors.rightMargin: 3
                                anchors.left: parent.left
                                anchors.leftMargin: 4
                                color: "#d1d1d2"
                                font.family: "Lato"
                                font.pixelSize: 11
                                horizontalAlignment: TextInput.AlignHCenter
                                validator: DoubleValidator{bottom: 0;}
                                readOnly: false
                                cursorVisible: row_options.current_input == text_input_retraction_dual_amount
                                Keys.onPressed: {
                                    if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                                        mainwindow.onFloatSettingChange(text_input_retraction_dual_amount.objectName, text)
                                    }
                                }
                            }

                            Text {
                                id: text_mm_retraction_dual_amount
                                height: parent.height
                                width: 22
                                text: qsTr("mm")
                                color: "#d1d1d2"
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
                                    text_input_retraction_dual_amount.forceActiveFocus();
                                    row_options.current_input = text_input_retraction_dual_amount;
                                }
                            }
                        }
                    }

                    Text {
                        id: title_fill
                        color: "#ffffff"
                        text: qsTr("Fill")
                        anchors.left: parent.left
                        anchors.leftMargin: 0
                        anchors.top: rect_retraction_dual_amount.bottom
                        anchors.topMargin: row_spacing * 4
                        font.pixelSize: 13
                        font.bold: true
                        font.family: lato_font.name
                    }

                    Rectangle {
                        id: rect_fill_density
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: title_fill.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_fill_density
                            color: "#a8a8a8"
                            text: qsTr("Fill density")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: fill_density
                            width: options_layer.input_width
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter

                            TextInput {
                                id: text_input_fill_density
                                objectName: "fill_density"
                                height: parent.height
                                anchors.top: parent.top
                                anchors.topMargin: 3
                                anchors.right: text_mm_fill_density.left
                                anchors.rightMargin: 3
                                anchors.left: parent.left
                                anchors.leftMargin: 4
                                color: "#d1d1d2"
                                font.family: "Lato"
                                font.pixelSize: 11
                                horizontalAlignment: TextInput.AlignHCenter
                                validator: DoubleValidator{bottom: 0; top: 100;}
                                readOnly: false
                                cursorVisible: row_options.current_input == text_input_fill_density
                                Keys.onPressed: {
                                    if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                                        mainwindow.onFloatSettingChange(text_input_fill_density.objectName, text)
                                    }
                                }
                            }

                            Text {
                                id: text_mm_fill_density
                                height: parent.height
                                width: 22
                                text: qsTr("%")
                                color: "#d1d1d2"
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
                                    text_input_fill_density.forceActiveFocus();
                                    row_options.current_input = text_input_fill_density;
                                }
                            }
                        }
                    }

                    Rectangle {
                        id: rect_solid_bottom
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: rect_fill_density.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_solid_bottom
                            color: "#a8a8a8"
                            text: qsTr("Solid infill bottom")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: solid_bottom
                            objectName: "solid_bottom"
                            width: 20
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            property bool isActive: false

                            MouseArea {
                                id: mouse_area_solid_bottom
                                anchors.fill: parent
                                onClicked: {
                                    solid_bottom.isActive = !solid_bottom.isActive
                                    mainwindow.onBoolSettingChange(solid_bottom.objectName, solid_bottom.isActive)
                                }

                                Image {
                                    id: image_solid_bottom
                                    opacity: solid_bottom.isActive ? 1 : 0
                                    anchors.horizontalCenter: parent.horizontalCenter
                                    anchors.verticalCenter: parent.verticalCenter
                                    source: "resources/icons/checked.png"
                                }
                            }

                        }
                    }

                    Rectangle {
                        id: rect_solid_top
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: rect_solid_bottom.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_solid_top
                            color: "#a8a8a8"
                            text: qsTr("Solid infill top")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: solid_top
                            objectName: "solid_top"
                            width: 20
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            property bool isActive: false

                            MouseArea {
                                id: mouse_area_solid_top
                                anchors.fill: parent
                                onClicked: {
                                    solid_top.isActive = !solid_top.isActive
                                    mainwindow.onBoolSettingChange(solid_top.objectName, solid_top.isActive)
                                }

                                Image {
                                    id: image_solid_top
                                    opacity: solid_top.isActive ? 1 : 0
                                    anchors.horizontalCenter: parent.horizontalCenter
                                    anchors.verticalCenter: parent.verticalCenter
                                    source: "resources/icons/checked.png"
                                }
                            }

                        }
                    }

                    Text {
                        id: title_adhesion
                        color: "#ffffff"
                        text: qsTr("Adhesion")
                        anchors.left: parent.left
                        anchors.leftMargin: 0
                        anchors.top: rect_solid_top.bottom
                        anchors.topMargin: row_spacing * 4
                        font.pixelSize: 13
                        font.bold: true
                        font.family: lato_font.name
                    }

                    // Rectangle {
                    //     id: rect_platform_adhesion
                    //     width: options_layer.line_width
                    //     height: options_layer.line_height
                    //     color: "#00000000"
                    //     anchors.top: title_adhesion.bottom
                    //     anchors.topMargin: row_spacing

                    //     Text {
                    //         id: text_platform_adhesion
                    //         color: "#a8a8a8"
                    //         text: qsTr("Platform adhesion type")
                    //         anchors.left: parent.left
                    //         anchors.leftMargin: 0
                    //         anchors.verticalCenter: parent.verticalCenter
                    //         verticalAlignment: Text.AlignVCenter
                    //         font.pixelSize: 11
                    //         font.family: lato_font.name
                    //     }

                    //     Rectangle {
                    //         id: platform_adhesion
                    //         objectName: "platform_adhesion"
                    //         width: options_layer.line_width
                    //         height: 20
                    //         color: "#333333"
                    //         radius: 1
                    //         border.color: "#333333"
                    //         anchors.right: parent.right
                    //         anchors.rightMargin: 0
                    //         anchors.verticalCenter: parent.verticalCenter
                    //         property bool isActive: false

                    //         MouseArea {
                    //             id: mouse_area_platform_adhesion
                    //             anchors.fill: parent
                    //             onClicked: {
                    //                 platform_adhesion.isActive = !platform_adhesion.isActive
                    //                 mainwindow.onBoolSettingChange(platform_adhesion.objectName, platform_adhesion.isActive)
                    //             }

                    //             Image {
                    //                 id: image_platform_adhesion
                    //                 opacity: platform_adhesion.isActive ? 1 : 0
                    //                 anchors.horizontalCenter: parent.horizontalCenter
                    //                 anchors.verticalCenter: parent.verticalCenter
                    //                 source: "resources/icons/checked.png"
                    //             }
                    //         }

                    //     }
                    // }

                    Rectangle {
                        id: rect_raft_margin
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: title_adhesion.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_raft_margin
                            color: "#a8a8a8"
                            text: qsTr("Extra margin")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: raft_margin
                            width: options_layer.input_width
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter

                            TextInput {
                                id: text_input_raft_margin
                                objectName: "raft_margin"
                                height: parent.height
                                anchors.top: parent.top
                                anchors.topMargin: 3
                                anchors.right: text_mm_raft_margin.left
                                anchors.rightMargin: 3
                                anchors.left: parent.left
                                anchors.leftMargin: 4
                                color: "#d1d1d2"
                                font.family: "Lato"
                                font.pixelSize: 11
                                horizontalAlignment: TextInput.AlignHCenter
                                validator: DoubleValidator{bottom: 0;}
                                readOnly: false
                                cursorVisible: row_options.current_input == text_input_raft_margin
                                Keys.onPressed: {
                                    if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                                        mainwindow.onFloatSettingChange(text_input_raft_margin.objectName, text)
                                    }
                                }
                            }

                            Text {
                                id: text_mm_raft_margin
                                height: parent.height
                                width: 22
                                text: qsTr("mm")
                                color: "#d1d1d2"
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
                                    text_input_raft_margin.forceActiveFocus();
                                    row_options.current_input = text_input_raft_margin;
                                }
                            }
                        }
                    }

                    Rectangle {
                        id: rect_raft_line_spacing
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: rect_raft_margin.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_raft_line_spacing
                            color: "#a8a8a8"
                            text: qsTr("Line spacing")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: raft_line_spacing
                            width: options_layer.input_width
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter

                            TextInput {
                                id: text_input_raft_line_spacing
                                objectName: "raft_line_spacing"
                                height: parent.height
                                anchors.top: parent.top
                                anchors.topMargin: 3
                                anchors.right: text_mm_raft_line_spacing.left
                                anchors.rightMargin: 3
                                anchors.left: parent.left
                                anchors.leftMargin: 4
                                color: "#d1d1d2"
                                font.family: "Lato"
                                font.pixelSize: 11
                                horizontalAlignment: TextInput.AlignHCenter
                                validator: DoubleValidator{bottom: 0;}
                                readOnly: false
                                cursorVisible: row_options.current_input == text_input_raft_line_spacing
                                Keys.onPressed: {
                                    if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                                        mainwindow.onFloatSettingChange(text_input_raft_line_spacing.objectName, text)
                                    }
                                }
                            }

                            Text {
                                id: text_mm_raft_line_spacing
                                height: parent.height
                                width: 22
                                text: qsTr("mm")
                                color: "#d1d1d2"
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
                                    text_input_raft_line_spacing.forceActiveFocus();
                                    row_options.current_input = text_input_raft_line_spacing;
                                }
                            }
                        }
                    }

                    Rectangle {
                        id: rect_raft_base_thickness
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: rect_raft_line_spacing.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_raft_base_thickness
                            color: "#a8a8a8"
                            text: qsTr("Base thickness")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: raft_base_thickness
                            width: options_layer.input_width
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter

                            TextInput {
                                id: text_input_raft_base_thickness
                                objectName: "raft_base_thickness"
                                height: parent.height
                                anchors.top: parent.top
                                anchors.topMargin: 3
                                anchors.right: text_mm_raft_base_thickness.left
                                anchors.rightMargin: 3
                                anchors.left: parent.left
                                anchors.leftMargin: 4
                                color: "#d1d1d2"
                                font.family: "Lato"
                                font.pixelSize: 11
                                horizontalAlignment: TextInput.AlignHCenter
                                validator: DoubleValidator{bottom: 0;}
                                readOnly: false
                                cursorVisible: row_options.current_input == text_input_raft_base_thickness
                                Keys.onPressed: {
                                    if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                                        mainwindow.onFloatSettingChange(text_input_raft_base_thickness.objectName, text)
                                    }
                                }
                            }

                            Text {
                                id: text_mm_raft_base_thickness
                                height: parent.height
                                width: 22
                                text: qsTr("mm")
                                color: "#d1d1d2"
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
                                    text_input_raft_base_thickness.forceActiveFocus();
                                    row_options.current_input = text_input_raft_base_thickness;
                                }
                            }
                        }
                    }

                    Rectangle {
                        id: rect_raft_interface_thickness
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: rect_raft_base_thickness.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_raft_interface_thickness
                            color: "#a8a8a8"
                            text: qsTr("Interface thickness")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: raft_interface_thickness
                            width: options_layer.input_width
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter

                            TextInput {
                                id: text_input_raft_interface_thickness
                                objectName: "raft_interface_thickness"
                                height: parent.height
                                anchors.top: parent.top
                                anchors.topMargin: 3
                                anchors.right: text_mm_raft_interface_thickness.left
                                anchors.rightMargin: 3
                                anchors.left: parent.left
                                anchors.leftMargin: 4
                                color: "#d1d1d2"
                                font.family: "Lato"
                                font.pixelSize: 11
                                horizontalAlignment: TextInput.AlignHCenter
                                validator: DoubleValidator{bottom: 0;}
                                readOnly: false
                                cursorVisible: row_options.current_input == text_input_raft_interface_thickness
                                Keys.onPressed: {
                                    if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                                        mainwindow.onFloatSettingChange(text_input_raft_interface_thickness.objectName, text)
                                    }
                                }
                            }

                            Text {
                                id: text_mm_raft_interface_thickness
                                height: parent.height
                                width: 22
                                text: qsTr("mm")
                                color: "#d1d1d2"
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
                                    text_input_raft_interface_thickness.forceActiveFocus();
                                    row_options.current_input = text_input_raft_interface_thickness;
                                }
                            }
                        }
                    }

                    Rectangle {
                        id: rect_raft_interface_linewidth
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: rect_raft_interface_thickness.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_raft_interface_linewidth
                            color: "#a8a8a8"
                            text: qsTr("Interface line width")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: raft_interface_linewidth
                            width: options_layer.input_width
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter

                            TextInput {
                                id: text_input_raft_interface_linewidth
                                objectName: "raft_interface_linewidth"
                                height: parent.height
                                anchors.top: parent.top
                                anchors.topMargin: 3
                                anchors.right: text_mm_raft_interface_linewidth.left
                                anchors.rightMargin: 3
                                anchors.left: parent.left
                                anchors.leftMargin: 4
                                color: "#d1d1d2"
                                font.family: "Lato"
                                font.pixelSize: 11
                                horizontalAlignment: TextInput.AlignHCenter
                                validator: DoubleValidator{bottom: 0;}
                                readOnly: false
                                cursorVisible: row_options.current_input == text_input_raft_interface_linewidth
                                Keys.onPressed: {
                                    if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                                        mainwindow.onFloatSettingChange(text_input_raft_interface_linewidth.objectName, text)
                                    }
                                }
                            }

                            Text {
                                id: text_mm_raft_interface_linewidth
                                height: parent.height
                                width: 22
                                text: qsTr("mm")
                                color: "#d1d1d2"
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
                                    text_input_raft_interface_linewidth.forceActiveFocus();
                                    row_options.current_input = text_input_raft_interface_linewidth;
                                }
                            }
                        }
                    }

                    Rectangle {
                        id: rect_raft_airgap
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: rect_raft_interface_linewidth.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_raft_airgap
                            color: "#a8a8a8"
                            text: qsTr("Airgap")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: raft_airgap
                            width: options_layer.input_width
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter

                            TextInput {
                                id: text_input_raft_airgap
                                objectName: "raft_airgap"
                                height: parent.height
                                anchors.top: parent.top
                                anchors.topMargin: 3
                                anchors.right: text_mm_raft_airgap.left
                                anchors.rightMargin: 3
                                anchors.left: parent.left
                                anchors.leftMargin: 4
                                color: "#d1d1d2"
                                font.family: "Lato"
                                font.pixelSize: 11
                                horizontalAlignment: TextInput.AlignHCenter
                                validator: DoubleValidator{bottom: 0;}
                                readOnly: false
                                cursorVisible: row_options.current_input == text_input_raft_airgap
                                Keys.onPressed: {
                                    if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                                        mainwindow.onFloatSettingChange(text_input_raft_airgap.objectName, text)
                                    }
                                }
                            }

                            Text {
                                id: text_mm_raft_airgap
                                height: parent.height
                                width: 22
                                text: qsTr("mm")
                                color: "#d1d1d2"
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
                                    text_input_raft_airgap.forceActiveFocus();
                                    row_options.current_input = text_input_raft_airgap;
                                }
                            }
                        }
                    }

                    Rectangle {
                        id: rect_raft_surface_layers
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: rect_raft_airgap.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_raft_surface_layers
                            color: "#a8a8a8"
                            text: qsTr("Surface layers")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: raft_surface_layers
                            width: options_layer.input_width
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter

                            TextInput {
                                id: text_input_raft_surface_layers
                                objectName: "raft_surface_layers"
                                height: parent.height
                                anchors.top: parent.top
                                anchors.topMargin: 3
                                anchors.right: text_mm_raft_surface_layers.left
                                anchors.rightMargin: 3
                                anchors.left: parent.left
                                anchors.leftMargin: 4
                                color: "#d1d1d2"
                                font.family: "Lato"
                                font.pixelSize: 11
                                horizontalAlignment: TextInput.AlignHCenter
                                validator: DoubleValidator{bottom: 0;}
                                readOnly: false
                                cursorVisible: row_options.current_input == text_input_raft_surface_layers
                                Keys.onPressed: {
                                    if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                                        mainwindow.onFloatSettingChange(text_input_raft_surface_layers.objectName, text)
                                    }
                                }
                            }

                            Text {
                                id: text_mm_raft_surface_layers
                                height: parent.height
                                width: 22
                                text: qsTr("mm")
                                color: "#d1d1d2"
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
                                    text_input_raft_surface_layers.forceActiveFocus();
                                    row_options.current_input = text_input_raft_surface_layers;
                                }
                            }
                        }
                    }

                    Rectangle {
                        id: rect_skirt_line_count
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: rect_raft_surface_layers.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_skirt_line_count
                            color: "#a8a8a8"
                            text: qsTr("Line count")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: skirt_line_count
                            width: options_layer.input_width
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter

                            TextInput {
                                id: text_input_skirt_line_count
                                objectName: "skirt_line_count"
                                height: parent.height
                                anchors.top: parent.top
                                anchors.topMargin: 3
                                anchors.right: text_mm_skirt_line_count.left
                                anchors.rightMargin: 3
                                anchors.left: parent.left
                                anchors.leftMargin: 4
                                color: "#d1d1d2"
                                font.family: "Lato"
                                font.pixelSize: 11
                                horizontalAlignment: TextInput.AlignHCenter
                                validator: DoubleValidator{bottom: 0;}
                                readOnly: false
                                cursorVisible: row_options.current_input == text_input_skirt_line_count
                                Keys.onPressed: {
                                    if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                                        mainwindow.onFloatSettingChange(text_input_skirt_line_count.objectName, text)
                                    }
                                }
                            }

                            Text {
                                id: text_mm_skirt_line_count
                                height: parent.height
                                width: 22
                                text: qsTr("mm")
                                color: "#d1d1d2"
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
                                    text_input_skirt_line_count.forceActiveFocus();
                                    row_options.current_input = text_input_skirt_line_count;
                                }
                            }
                        }
                    }

                    Rectangle {
                        id: rect_fill_overlap
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: rect_skirt_line_count.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_fill_overlap
                            color: "#a8a8a8"
                            text: qsTr("Layer height")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: fill_overlap
                            width: options_layer.input_width
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter

                            TextInput {
                                id: text_input_fill_overlap
                                objectName: "fill_overlap"
                                height: parent.height
                                anchors.top: parent.top
                                anchors.topMargin: 3
                                anchors.right: text_mm_fill_overlap.left
                                anchors.rightMargin: 3
                                anchors.left: parent.left
                                anchors.leftMargin: 4
                                color: "#d1d1d2"
                                font.family: "Lato"
                                font.pixelSize: 11
                                horizontalAlignment: TextInput.AlignHCenter
                                validator: IntValidator{bottom: 0; top: 100;}
                                readOnly: false
                                cursorVisible: row_options.current_input == text_input_fill_overlap
                                Keys.onPressed: {
                                    if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                                        mainwindow.onFloatSettingChange(text_input_fill_overlap.objectName, text)
                                    }
                                }
                            }

                            Text {
                                id: text_mm_fill_overlap
                                height: parent.height
                                width: 22
                                text: qsTr("%")
                                color: "#d1d1d2"
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
                                    text_input_fill_overlap.forceActiveFocus();
                                    row_options.current_input = text_input_fill_overlap;
                                }
                            }
                        }
                    }

                    Rectangle {
                        id: rect_skirt_minimal_length
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: rect_fill_overlap.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_skirt_minimal_length
                            color: "#a8a8a8"
                            text: qsTr("Minimal length")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: skirt_minimal_length
                            width: options_layer.input_width
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter

                            TextInput {
                                id: text_input_skirt_minimal_length
                                objectName: "skirt_minimal_length"
                                height: parent.height
                                anchors.top: parent.top
                                anchors.topMargin: 3
                                anchors.right: text_mm_skirt_minimal_length.left
                                anchors.rightMargin: 3
                                anchors.left: parent.left
                                anchors.leftMargin: 4
                                color: "#d1d1d2"
                                font.family: "Lato"
                                font.pixelSize: 11
                                horizontalAlignment: TextInput.AlignHCenter
                                validator: DoubleValidator{bottom: 0;}
                                readOnly: false
                                cursorVisible: row_options.current_input == text_input_skirt_minimal_length
                                Keys.onPressed: {
                                    if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                                        mainwindow.onFloatSettingChange(text_input_skirt_minimal_length.objectName, text)
                                    }
                                }
                            }

                            Text {
                                id: text_mm_skirt_minimal_length
                                height: parent.height
                                width: 22
                                text: qsTr("mm")
                                color: "#d1d1d2"
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
                                    text_input_skirt_minimal_length.forceActiveFocus();
                                    row_options.current_input = text_input_skirt_minimal_length;
                                }
                            }
                        }
                    }

                    Text {
                        id: title_support
                        color: "#ffffff"
                        text: qsTr("Support")
                        anchors.left: parent.left
                        anchors.leftMargin: 0
                        anchors.top: rect_skirt_minimal_length.bottom
                        anchors.topMargin: row_spacing * 4
                        font.pixelSize: 13
                        font.bold: true
                        font.family: lato_font.name
                    }

                    Rectangle {
                        id: rect_support_angle
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: title_support.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_support_angle
                            color: "#a8a8a8"
                            text: qsTr("Overhang angle for support")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: support_angle
                            width: options_layer.input_width
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter

                            TextInput {
                                id: text_input_support_angle
                                objectName: "support_angle"
                                height: parent.height
                                anchors.top: parent.top
                                anchors.topMargin: 3
                                anchors.right: text_mm_support_angle.left
                                anchors.rightMargin: 3
                                anchors.left: parent.left
                                anchors.leftMargin: 4
                                color: "#d1d1d2"
                                font.family: "Lato"
                                font.pixelSize: 11
                                horizontalAlignment: TextInput.AlignHCenter
                                validator: DoubleValidator{bottom: 0; top: 360;}
                                readOnly: false
                                cursorVisible: row_options.current_input == text_input_support_angle
                                Keys.onPressed: {
                                    if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                                        mainwindow.onFloatSettingChange(text_input_support_angle.objectName, text)
                                    }
                                }
                            }

                            Text {
                                id: text_mm_support_angle
                                height: parent.height
                                width: 22
                                text: qsTr("deg")
                                color: "#d1d1d2"
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
                                    text_input_support_angle.forceActiveFocus();
                                    row_options.current_input = text_input_support_angle;
                                }
                            }
                        }
                    }

                    Rectangle {
                        id: rect_support_fill_rate
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: rect_support_angle.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_support_fill_rate
                            color: "#a8a8a8"
                            text: qsTr("Overhang angle for support")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: support_fill_rate
                            width: options_layer.input_width
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter

                            TextInput {
                                id: text_input_support_fill_rate
                                objectName: "support_fill_rate"
                                height: parent.height
                                anchors.top: parent.top
                                anchors.topMargin: 3
                                anchors.right: text_mm_support_fill_rate.left
                                anchors.rightMargin: 3
                                anchors.left: parent.left
                                anchors.leftMargin: 4
                                color: "#d1d1d2"
                                font.family: "Lato"
                                font.pixelSize: 11
                                horizontalAlignment: TextInput.AlignHCenter
                                validator: IntValidator{bottom: 0; top: 100;}
                                readOnly: false
                                cursorVisible: row_options.current_input == text_input_support_fill_rate
                                Keys.onPressed: {
                                    if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                                        mainwindow.onFloatSettingChange(text_input_support_fill_rate.objectName, text)
                                    }
                                }
                            }

                            Text {
                                id: text_mm_support_fill_rate
                                height: parent.height
                                width: 22
                                text: qsTr("%")
                                color: "#d1d1d2"
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
                                    text_input_support_fill_rate.forceActiveFocus();
                                    row_options.current_input = text_input_support_fill_rate;
                                }
                            }
                        }
                    }

                    Rectangle {
                        id: rect_support_xy_distance
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: rect_support_fill_rate.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_support_xy_distance
                            color: "#a8a8a8"
                            text: qsTr("Distance X/Y")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: support_xy_distance
                            width: options_layer.input_width
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter

                            TextInput {
                                id: text_input_support_xy_distance
                                objectName: "support_xy_distance"
                                height: parent.height
                                anchors.top: parent.top
                                anchors.topMargin: 3
                                anchors.right: text_mm_support_xy_distance.left
                                anchors.rightMargin: 3
                                anchors.left: parent.left
                                anchors.leftMargin: 4
                                color: "#d1d1d2"
                                font.family: "Lato"
                                font.pixelSize: 11
                                horizontalAlignment: TextInput.AlignHCenter
                                validator: DoubleValidator{bottom: 0; top: 360;}
                                readOnly: false
                                cursorVisible: row_options.current_input == text_input_support_xy_distance
                                Keys.onPressed: {
                                    if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                                        mainwindow.onFloatSettingChange(text_input_support_xy_distance.objectName, text)
                                    }
                                }
                            }

                            Text {
                                id: text_mm_support_xy_distance
                                height: parent.height
                                width: 22
                                text: qsTr("mm")
                                color: "#d1d1d2"
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
                                    text_input_support_xy_distance.forceActiveFocus();
                                    row_options.current_input = text_input_support_xy_distance;
                                }
                            }
                        }
                    }

                    Rectangle {
                        id: rect_support_z_distance
                        width: options_layer.line_width
                        height: options_layer.line_height
                        color: "#00000000"
                        anchors.top: rect_support_xy_distance.bottom
                        anchors.topMargin: row_spacing

                        Text {
                            id: text_support_z_distance
                            color: "#a8a8a8"
                            text: qsTr("Distance Z")
                            anchors.left: parent.left
                            anchors.leftMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 11
                            font.family: lato_font.name
                        }

                        Rectangle {
                            id: support_z_distance
                            width: options_layer.input_width
                            height: 20
                            color: "#333333"
                            radius: 1
                            border.color: "#333333"
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter

                            TextInput {
                                id: text_input_support_z_distance
                                objectName: "support_z_distance"
                                height: parent.height
                                anchors.top: parent.top
                                anchors.topMargin: 3
                                anchors.right: text_mm_support_z_distance.left
                                anchors.rightMargin: 3
                                anchors.left: parent.left
                                anchors.leftMargin: 4
                                color: "#d1d1d2"
                                font.family: "Lato"
                                font.pixelSize: 11
                                horizontalAlignment: TextInput.AlignHCenter
                                validator: DoubleValidator{bottom: 0; top: 10;}
                                readOnly: false
                                cursorVisible: row_options.current_input == text_input_support_z_distance
                                Keys.onPressed: {
                                    if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                                        mainwindow.onFloatSettingChange(text_input_support_z_distance.objectName, text)
                                    }
                                }
                            }

                            Text {
                                id: text_mm_support_z_distance
                                height: parent.height
                                width: 22
                                text: qsTr("mm")
                                color: "#d1d1d2"
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
                                    text_input_support_z_distance.forceActiveFocus();
                                    row_options.current_input = text_input_support_z_distance;
                                }
                            }
                        }
                    }

                    Rectangle {
                        id: button
                        width: 100
                        height: 32
                        color: "#ff5724"
                        anchors.right: parent.right
                        anchors.rightMargin: row_options.padding
                        anchors.bottom: parent.bottom
                        anchors.bottomMargin: row_options.padding

                        Text {
                            id: button_text
                            color: "#ffffff"
                            text: qsTr("Start")
                            font.bold: true
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                            anchors.fill: parent
                            font.pixelSize: 14
                            font.family: lato_font.name
                        }

                        MouseArea {
                            id: mouse_area_button
                            anchors.fill: parent
                            onClicked: {
                                options_layer.hideLayer();
                                mainwindow.saveAdvancedOptions();
                                graphicsscene.onRunEngine();
                                print_button.state = "SLICING";
                            }
                        }
                    }

                }
            }

            Rectangle {
                id: row_gcodes
                color: "#5d6169"
                width: parent.width
                height: parent.height - row_tabs.height
                anchors.top: row_tabs.bottom
                anchors.topMargin: 0
                anchors.left: parent.left
                anchors.leftMargin: row_options.padding/2
                anchors.right: parent.right
                anchors.rightMargin: row_options.padding/2
                opacity: tab_gcodes.active ? 1 : 0

                Rectangle {
                    id: start_gcode_rect
                    color: "#00000000"
                    width: (parent.width - 2*row_options.padding) / 2 - 20
                    height: parent.height
                    anchors.left: parent.left
                    anchors.leftMargin: row_options.padding
                    anchors.top: parent.top
                    anchors.topMargin: 10

                    Text {
                        id: start_gcode_label
                        text: qsTr("Start GCode")
                        verticalAlignment: Text.AlignVCenter
                        horizontalAlignment: Text.AlignHCenter
                        width: parent.width
                        font.pixelSize: 12
                        color: "#ffffff"
                        font.bold: true
                        font.family: lato_font.name
                    }

                    Rectangle {
                        width: parent.width
                        anchors.top: start_gcode_label.bottom
                        anchors.topMargin: 10
                        color: "#333333"
                        height: parent.height - start_gcode_label.height - 50

                        TextEdit {
                            id: startgcode
                            objectName: "startgcode"
                            font.pixelSize: 12
                            color: "#d1d1d2"
                            wrapMode: TextEdit.WordWrap
                            anchors.fill: parent
                            cursorVisible: row_options.current_input == startgcode
                        }

                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                startgcode.forceActiveFocus();
                                row_options.current_input = startgcode;
                            }
                        }
                    }

                }

                Rectangle {
                    id: end_gcode_rect
                    color: "#00000000"
                    width: (parent.width - 2*row_options.padding) / 2 - 20
                    height: parent.height
                    anchors.right: parent.right
                    anchors.rightMargin: row_options.padding
                    anchors.left: start_gcode_rect.right
                    anchors.leftMargin: 40
                    anchors.top: parent.top
                    anchors.topMargin: 10

                    Text {
                        id: end_gcode_label
                        text: qsTr("End GCode")
                        verticalAlignment: Text.AlignVCenter
                        horizontalAlignment: Text.AlignHCenter
                        width: parent.width
                        font.pixelSize: 13
                        color: "#ffffff"
                        font.bold: true
                        font.family: lato_font.name
                    }

                    Rectangle {
                        width: parent.width
                        anchors.top: end_gcode_label.bottom
                        anchors.topMargin: 10
                        color: "#333333"
                        height: parent.height - end_gcode_label.height - 50

                        TextEdit {
                            id: endgcode
                            objectName: "endgcode"
                            font.pixelSize: 12
                            color: "#d1d1d2"
                            wrapMode: TextEdit.WordWrap
                            anchors.fill: parent
                            cursorVisible: row_options.current_input == endgcode
                        }

                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                endgcode.forceActiveFocus();
                                row_options.current_input = endgcode;
                            }
                        }
                    }
                }
            }

            // Only show the scrollbars when the view is moving.
            // states: State {
            //     name: "ShowBars"
            //     when: view.movingVertically || view.movingHorizontally
            //     PropertyChanges { target: verticalScrollBar; opacity: 1 }
            //     PropertyChanges { target: horizontalScrollBar; opacity: 1 }
            // }

            // transitions: Transition {
            //     NumberAnimation { properties: "opacity"; duration: 400 }
            // }

            // Attach scrollbars to the right and bottom edges of the view.
            ScrollBar {
                id: verticalScrollBar
                width: 12; height: parent.height-12
                anchors.right: parent.right
                opacity: pageSize == 1 ? 0 : 1
                orientation: Qt.Vertical
                position: view.visibleArea.yPosition
                pageSize: view.visibleArea.heightRatio
            }

            ScrollBar {
                id: horizontalScrollBar
                width: parent.width-12; height: 12
                anchors.bottom: parent.bottom
                opacity: pageSize == 1 ? 0 : 1
                orientation: Qt.Horizontal
                position: view.visibleArea.xPosition
                pageSize: view.visibleArea.widthRatio
            }
        }
    }

    function showLayer() {
        options_layer.enabled = true;
        options_layer.opacity = 1;
        graphicsscene.setLayerOn();
    }

    function hideLayer() {
        options_layer.enabled = false;
        options_layer.opacity = 0;
        graphicsscene.setLayerOff();
    }

    function setFields(fdict) {
        text_input_layer_height.text = qsTr(fdict['layer_height']);
        text_input_wall_thickness.text = qsTr(fdict['wall_thickness']);
        text_input_solid_layer_thickness.text = qsTr(fdict['solid_layer_thickness']);
        text_input_bottom_thickness.text = qsTr(fdict['bottom_thickness']);
        text_input_layer0_width_factor.text = qsTr(fdict['layer0_width_factor']);
        text_input_print_temperature.text = qsTr(fdict['print_temperature']);
        text_input_print_temperature_2.text = qsTr(fdict['print_temperature2']);
        text_input_print_bed_temperature.text = qsTr(fdict['print_bed_temperature']);
        text_input_cool_min_layer_time.text = qsTr(fdict['cool_min_layer_time']);
        text_input_fan_full_height.text = qsTr(fdict['fan_full_height']);
        text_input_fan_speed.text = qsTr(fdict['fan_speed']);
        text_input_fan_speed_max.text = qsTr(fdict['fan_speed_max']);
        text_input_cool_min_feedrate.text = qsTr(fdict['cool_min_feedrate']);
        text_input_object_sink.text = qsTr(fdict['object_sink']);
        text_input_filament_flow.text = qsTr(fdict['filament_flow']);
        text_input_retraction_speed.text = qsTr(fdict['retraction_speed']);
        text_input_retraction_min_travel.text = qsTr(fdict['retraction_min_travel']);
        text_input_retraction_dual_amount.text = qsTr(fdict['retraction_dual_amount']);
        text_input_fill_density.text = qsTr(fdict['fill_density']);
        text_input_raft_margin.text = qsTr(fdict['raft_margin']);
        text_input_raft_line_spacing.text = qsTr(fdict['raft_line_spacing']);
        text_input_raft_base_thickness.text = qsTr(fdict['raft_base_thickness']);
        text_input_raft_interface_thickness.text = qsTr(fdict['raft_interface_thickness']);
        text_input_raft_interface_linewidth.text = qsTr(fdict['raft_interface_linewidth']);
        text_input_raft_airgap.text = qsTr(fdict['raft_airgap']);
        text_input_raft_surface_layers.text = qsTr(fdict['raft_surface_layers']);
        text_input_skirt_line_count.text = qsTr(fdict['skirt_line_count']);
        text_input_fill_overlap.text = qsTr(fdict['fill_overlap']);
        text_input_skirt_minimal_length.text = qsTr(fdict['skirt_minimal_length']);
        text_input_support_angle.text = qsTr(fdict['support_angle']);
        text_input_support_fill_rate.text = qsTr(fdict['support_fill_rate']);
        text_input_support_xy_distance.text = qsTr(fdict['support_xy_distance']);
        text_input_support_z_distance.text = qsTr(fdict['support_z_distance']);
        startgcode.text = fdict['startgcode'];
        endgcode.text = fdict['endgcode'];

        // ticks
        cool_head_lift.isActive = fdict['cool_head_lift'];
        simple_mode.isActive = fdict['simple_mode'];
        spiralize.isActive = fdict['spiralize'];
        fan_enabled.isActive = fdict['fan_enabled'];
        retraction_enable.isActive = fdict['retraction_enable'];
        solid_bottom.isActive = fdict['solid_bottom'];
        solid_top.isActive = fdict['solid_top'];
        fix_horrible_union_all_type_a.isActive = fdict['fix_horrible_union_all_type_a'];
        fix_horrible_union_all_type_b.isActive = fdict['fix_horrible_union_all_type_b'];
        fix_horrible_use_open_bits.isActive = fdict['fix_horrible_use_open_bits'];
        fix_horrible_extensive_stitching.isActive = fdict['fix_horrible_extensive_stitching'];
    }

    function getFields() {
        return {
            'layer_height': text_input_layer_height.text,
            'wall_thickness': text_input_wall_thickness.text,
            'solid_layer_thickness': text_input_solid_layer_thickness.text,
            'bottom_thickness': text_input_bottom_thickness.text,
            'layer0_width_factor': text_input_layer0_width_factor.text,
            'print_temperature': text_input_print_temperature.text,
            'print_temperature2': text_input_print_temperature_2.text,
            'print_bed_temperature': text_input_print_bed_temperature.text,
            'cool_min_layer_time': text_input_cool_min_layer_time.text,
            'fan_full_height': text_input_fan_full_height.text,
            'fan_speed': text_input_fan_speed.text,
            'fan_speed_max': text_input_fan_speed_max.text,
            'cool_min_feedrate': text_input_cool_min_feedrate.text,
            'object_sink': text_input_object_sink.text,
            'filament_flow': text_input_filament_flow.text,
            'retraction_speed': text_input_retraction_speed.text,
            'retraction_min_travel': text_input_retraction_min_travel.text,
            'retraction_dual_amount': text_input_retraction_dual_amount.text,
            'fill_density': text_input_fill_density.text,
            'raft_margin': text_input_raft_margin.text,
            'raft_line_spacing': text_input_raft_line_spacing.text,
            'raft_surface_layers': text_input_raft_surface_layers.text,
            'raft_base_thickness': text_input_raft_base_thickness.text,
            'raft_interface_thickness': text_input_raft_interface_thickness.text,
            'raft_interface_linewidth': text_input_raft_interface_linewidth.text,
            'raft_airgap': text_input_raft_airgap.text,
            'skirt_line_count': text_input_skirt_line_count.text,
            'fill_overlap': text_input_fill_overlap.text,
            'skirt_minimal_length': text_input_skirt_minimal_length.text,
            'support_angle': text_input_support_angle.text,
            'support_fill_rate': text_input_support_fill_rate.text,
            'support_xy_distance': text_input_support_xy_distance.text,
            'support_z_distance': text_input_support_z_distance.text,
            'startgcode': startgcode.text,
            'endgcode': endgcode.text,
            'cool_head_lift': cool_head_lift.isActive,
            'simple_mode': simple_mode.isActive,
            'spiralize': spiralize.isActive,
            'fan_enabled': fan_enabled.isActive,
            'retraction_enable': retraction_enable.isActive,
            'solid_bottom': solid_bottom.isActive,
            'solid_top': solid_top.isActive,
            'fix_horrible_union_all_type_a': fix_horrible_union_all_type_a.isActive,
            'fix_horrible_union_all_type_b': fix_horrible_union_all_type_b.isActive,
            'fix_horrible_use_open_bits': fix_horrible_use_open_bits.isActive,
            'fix_horrible_extensive_stitching': fix_horrible_extensive_stitching.isActive,
            }
    }
}

