// import QtQuick 1.0 // to target S60 5th Edition or Maemo 5
import QtQuick 1.1
import QtQuick 1.0

Rectangle {
    id: options_layer
    width: 700
    height: 850
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
        color: "#3f4245"

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
                options_layer.enabled = false;
                options_layer.opacity = 0;
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

        Rectangle {
            id: row_tabs
            color: "#00000000"
            width: parent.width
            height: 30
        }

        Rectangle {
            id: row_options
            color: "#00000000"
            width: parent.width
            height: parent.height - row_tabs.height
            anchors.top: row_tabs.bottom
            anchors.topMargin: 0
            anchors.right: parent.right
            anchors.rightMargin: 0

            property int padding: 50

            Rectangle {
                id: column_left
                color: "#00000000"
                width: (parent.width - 2*row_options.padding) / 2
                height: parent.height
                anchors.left: parent.left
                anchors.leftMargin: row_options.padding

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
                            width: parent.width - text_mm_layer_height.width
                            height: parent.height
                            text: qsTr("1.0")
                            anchors.top: parent.top
                            anchors.topMargin: 3
                            anchors.right: text_mm_layer_height.left
                            anchors.rightMargin: 3
                            color: "#d1d1d2"
                            font.family: "Lato"
                            font.pixelSize: 11
                            horizontalAlignment: TextInput.AlignRight
                            validator: DoubleValidator{bottom: 0;}
                            readOnly: false
                        }

                        Text {
                            id: text_mm_layer_height
                            height: parent.height
                            width: 25
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
                            width: parent.width - text_mm_wall_thickness.width
                            height: parent.height
                            text: qsTr("1.0")
                            anchors.top: parent.top
                            anchors.topMargin: 3
                            anchors.right: text_mm_wall_thickness.left
                            anchors.rightMargin: 3
                            color: "#d1d1d2"
                            font.family: "Lato"
                            font.pixelSize: 11
                            horizontalAlignment: TextInput.AlignRight
                            validator: DoubleValidator{bottom: 0;}
                            readOnly: false
                        }

                        Text {
                            id: text_mm_wall_thickness
                            height: parent.height
                            width: 25
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
                            width: parent.width - text_mm_solid_layer_thickness.width
                            height: parent.height
                            text: qsTr("0.6")
                            anchors.top: parent.top
                            anchors.topMargin: 3
                            anchors.right: text_mm_solid_layer_thickness.left
                            anchors.rightMargin: 3
                            color: "#d1d1d2"
                            font.family: "Lato"
                            font.pixelSize: 11
                            horizontalAlignment: TextInput.AlignRight
                            validator: DoubleValidator{bottom: 0;}
                            readOnly: false
                        }

                        Text {
                            id: text_mm_solid_layer_thickness
                            height: parent.height
                            width: 25
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
                            width: parent.width - text_mm_bottom_thickness.width
                            height: parent.height
                            text: qsTr("0.3")
                            anchors.top: parent.top
                            anchors.topMargin: 3
                            anchors.right: text_mm_bottom_thickness.left
                            anchors.rightMargin: 3
                            color: "#d1d1d2"
                            font.family: "Lato"
                            font.pixelSize: 11
                            horizontalAlignment: TextInput.AlignRight
                            validator: DoubleValidator{bottom: 0;}
                            readOnly: false
                        }

                        Text {
                            id: text_mm_bottom_thickness
                            height: parent.height
                            width: 25
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
                            width: parent.width - text_mm_layer0_width_factor.width
                            height: parent.height
                            text: qsTr("100.0")
                            anchors.top: parent.top
                            anchors.topMargin: 3
                            anchors.right: text_mm_layer0_width_factor.left
                            anchors.rightMargin: 3
                            color: "#d1d1d2"
                            font.family: "Lato"
                            font.pixelSize: 11
                            horizontalAlignment: TextInput.AlignRight
                            validator: DoubleValidator{bottom: 0;}
                            readOnly: false
                        }

                        Text {
                            id: text_mm_layer0_width_factor
                            height: parent.height
                            width: 25
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
                            width: parent.width - text_mm_print_temperature.width
                            height: parent.height
                            text: qsTr("220")
                            anchors.top: parent.top
                            anchors.topMargin: 3
                            anchors.right: text_mm_print_temperature.left
                            anchors.rightMargin: 3
                            color: "#d1d1d2"
                            font.family: "Lato"
                            font.pixelSize: 11
                            horizontalAlignment: TextInput.AlignRight
                            validator: IntValidator{bottom: 0; top: 340;}
                            readOnly: false
                        }

                        Text {
                            id: text_mm_print_temperature
                            height: parent.height
                            width: 25
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
                            objectName: "print_temperature_2"
                            width: parent.width - text_mm_print_temperature_2.width
                            height: parent.height
                            text: qsTr("220")
                            anchors.top: parent.top
                            anchors.topMargin: 3
                            anchors.right: text_mm_print_temperature_2.left
                            anchors.rightMargin: 3
                            color: "#d1d1d2"
                            font.family: "Lato"
                            font.pixelSize: 11
                            horizontalAlignment: TextInput.AlignRight
                            validator: IntValidator{bottom: 0; top: 340;}
                            readOnly: false
                        }

                        Text {
                            id: text_mm_print_temperature_2
                            height: parent.height
                            width: 25
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
                            width: parent.width - text_mm_print_bed_temperature.width
                            height: parent.height
                            text: qsTr("70")
                            anchors.top: parent.top
                            anchors.topMargin: 3
                            anchors.right: text_mm_print_bed_temperature.left
                            anchors.rightMargin: 3
                            color: "#d1d1d2"
                            font.family: "Lato"
                            font.pixelSize: 11
                            horizontalAlignment: TextInput.AlignRight
                            validator: IntValidator{bottom: 0; top: 340;}
                            readOnly: false
                        }

                        Text {
                            id: text_mm_print_bed_temperature
                            height: parent.height
                            width: 25
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
                            width: parent.width - text_mm_cool_min_layer_time.width
                            height: parent.height
                            text: qsTr("5.0")
                            anchors.top: parent.top
                            anchors.topMargin: 3
                            anchors.right: text_mm_cool_min_layer_time.left
                            anchors.rightMargin: 3
                            color: "#d1d1d2"
                            font.family: "Lato"
                            font.pixelSize: 11
                            horizontalAlignment: TextInput.AlignRight
                            validator: DoubleValidator{bottom: 0;}
                            readOnly: false
                        }

                        Text {
                            id: text_mm_cool_min_layer_time
                            height: parent.height
                            width: 25
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
                            width: parent.width - text_mm_fan_full_height.width
                            height: parent.height
                            text: qsTr("0.5")
                            anchors.top: parent.top
                            anchors.topMargin: 3
                            anchors.right: text_mm_fan_full_height.left
                            anchors.rightMargin: 3
                            color: "#d1d1d2"
                            font.family: "Lato"
                            font.pixelSize: 11
                            horizontalAlignment: TextInput.AlignRight
                            validator: DoubleValidator{bottom: 0;}
                            readOnly: false
                        }

                        Text {
                            id: text_mm_fan_full_height
                            height: parent.height
                            width: 25
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
                            width: parent.width - text_mm_fan_speed.width
                            height: parent.height
                            text: qsTr("100")
                            anchors.top: parent.top
                            anchors.topMargin: 3
                            anchors.right: text_mm_fan_speed.left
                            anchors.rightMargin: 3
                            color: "#d1d1d2"
                            font.family: "Lato"
                            font.pixelSize: 11
                            horizontalAlignment: TextInput.AlignRight
                            validator: IntValidator{bottom: 0; top: 100;}
                            readOnly: false
                        }

                        Text {
                            id: text_mm_fan_speed
                            height: parent.height
                            width: 25
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
                            width: parent.width - text_mm_fan_speed_max.width
                            height: parent.height
                            text: qsTr("100")
                            anchors.top: parent.top
                            anchors.topMargin: 3
                            anchors.right: text_mm_fan_speed_max.left
                            anchors.rightMargin: 3
                            color: "#d1d1d2"
                            font.family: "Lato"
                            font.pixelSize: 11
                            horizontalAlignment: TextInput.AlignRight
                            validator: IntValidator{bottom: 0; top: 100;}
                            readOnly: false
                        }

                        Text {
                            id: text_mm_fan_speed_max
                            height: parent.height
                            width: 25
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
                            width: parent.width - text_mm_cool_min_feedrate.width
                            height: parent.height
                            text: qsTr("10")
                            anchors.top: parent.top
                            anchors.topMargin: 3
                            anchors.right: text_mm_cool_min_feedrate.left
                            anchors.rightMargin: 3
                            color: "#d1d1d2"
                            font.family: "Lato"
                            font.pixelSize: 11
                            horizontalAlignment: TextInput.AlignRight
                            validator: DoubleValidator{bottom: 0;}
                            readOnly: false
                        }

                        Text {
                            id: text_mm_cool_min_feedrate
                            height: parent.height
                            width: 25
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
                            width: parent.width - text_mm_object_sink.width
                            height: parent.height
                            text: qsTr("0.0")
                            anchors.top: parent.top
                            anchors.topMargin: 3
                            anchors.right: text_mm_object_sink.left
                            anchors.rightMargin: 3
                            color: "#d1d1d2"
                            font.family: "Lato"
                            font.pixelSize: 11
                            horizontalAlignment: TextInput.AlignRight
                            validator: DoubleValidator{bottom: 0;}
                            readOnly: false
                        }

                        Text {
                            id: text_mm_object_sink
                            height: parent.height
                            width: 25
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
                            width: parent.width - text_mm_filament_flow.width
                            height: parent.height
                            text: qsTr("100.0")
                            anchors.top: parent.top
                            anchors.topMargin: 3
                            anchors.right: text_mm_filament_flow.left
                            anchors.rightMargin: 3
                            color: "#d1d1d2"
                            font.family: "Lato"
                            font.pixelSize: 11
                            horizontalAlignment: TextInput.AlignRight
                            validator: DoubleValidator{bottom: 5; top: 300;}
                            readOnly: false
                        }

                        Text {
                            id: text_mm_filament_flow
                            height: parent.height
                            width: 25
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
                                fix_horrible_use_open_bits.isActive = !fix_horrible_extensive_stitching.isActive
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
                            width: parent.width - text_mm_retraction_speed.width
                            height: parent.height
                            text: qsTr("40.0")
                            anchors.top: parent.top
                            anchors.topMargin: 3
                            anchors.right: text_mm_retraction_speed.left
                            anchors.rightMargin: 3
                            color: "#d1d1d2"
                            font.family: "Lato"
                            font.pixelSize: 11
                            horizontalAlignment: TextInput.AlignRight
                            validator: DoubleValidator{bottom: 0.1;}
                            readOnly: false
                        }

                        Text {
                            id: text_mm_retraction_speed
                            height: parent.height
                            width: 25
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
                            width: parent.width - text_mm_retraction_min_travel.width
                            height: parent.height
                            text: qsTr("1.5")
                            anchors.top: parent.top
                            anchors.topMargin: 3
                            anchors.right: text_mm_retraction_min_travel.left
                            anchors.rightMargin: 3
                            color: "#d1d1d2"
                            font.family: "Lato"
                            font.pixelSize: 11
                            horizontalAlignment: TextInput.AlignRight
                            validator: DoubleValidator{bottom: 0;}
                            readOnly: false
                        }

                        Text {
                            id: text_mm_retraction_min_travel
                            height: parent.height
                            width: 25
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
                            width: parent.width - text_mm_retraction_dual_amount.width
                            height: parent.height
                            text: qsTr("16.5")
                            anchors.top: parent.top
                            anchors.topMargin: 3
                            anchors.right: text_mm_retraction_dual_amount.left
                            anchors.rightMargin: 3
                            color: "#d1d1d2"
                            font.family: "Lato"
                            font.pixelSize: 11
                            horizontalAlignment: TextInput.AlignRight
                            validator: DoubleValidator{bottom: 0;}
                            readOnly: false
                        }

                        Text {
                            id: text_mm_retraction_dual_amount
                            height: parent.height
                            width: 25
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
                            width: parent.width - text_mm_fill_density.width
                            height: parent.height
                            text: qsTr("20.0")
                            anchors.top: parent.top
                            anchors.topMargin: 3
                            anchors.right: text_mm_fill_density.left
                            anchors.rightMargin: 3
                            color: "#d1d1d2"
                            font.family: "Lato"
                            font.pixelSize: 11
                            horizontalAlignment: TextInput.AlignRight
                            validator: DoubleValidator{bottom: 0; top: 100;}
                            readOnly: false
                        }

                        Text {
                            id: text_mm_fill_density
                            height: parent.height
                            width: 25
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
                    id: title_support
                    color: "#ffffff"
                    text: qsTr("Support")
                    anchors.left: parent.left
                    anchors.leftMargin: 0
                    anchors.top: rect_solid_top.bottom
                    anchors.topMargin: row_spacing * 4
                    font.pixelSize: 13
                    font.bold: true
                    font.family: lato_font.name
                }

                Rectangle {
                    id: rect_platform_adhesion
                    width: options_layer.line_width
                    height: options_layer.line_height
                    color: "#00000000"
                    anchors.top: title_support.bottom
                    anchors.topMargin: row_spacing

                    Text {
                        id: text_platform_adhesion
                        color: "#a8a8a8"
                        text: qsTr("Platform adhesion type")
                        anchors.left: parent.left
                        anchors.leftMargin: 0
                        anchors.verticalCenter: parent.verticalCenter
                        verticalAlignment: Text.AlignVCenter
                        font.pixelSize: 11
                        font.family: lato_font.name
                    }

                    Rectangle {
                        id: platform_adhesion
                        objectName: "platform_adhesion"
                        width: options_layer.line_width
                        height: 20
                        color: "#333333"
                        radius: 1
                        border.color: "#333333"
                        anchors.right: parent.right
                        anchors.rightMargin: 0
                        anchors.verticalCenter: parent.verticalCenter
                        property bool isActive: false

                        MouseArea {
                            id: mouse_area_platform_adhesion
                            anchors.fill: parent
                            onClicked: {
                                platform_adhesion.isActive = !platform_adhesion.isActive
                            }

                            Image {
                                id: image_platform_adhesion
                                opacity: platform_adhesion.isActive ? 1 : 0
                                anchors.horizontalCenter: parent.horizontalCenter
                                anchors.verticalCenter: parent.verticalCenter
                                source: "resources/icons/checked.png"
                            }
                        }

                    }
                }

                Rectangle {
                    id: rect_raft_margin
                    width: options_layer.line_width
                    height: options_layer.line_height
                    color: "#00000000"
                    anchors.top: rect_platform_adhesion.bottom
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
                            width: parent.width - text_mm_raft_margin.width
                            height: parent.height
                            text: qsTr("5.0")
                            anchors.top: parent.top
                            anchors.topMargin: 3
                            anchors.right: text_mm_raft_margin.left
                            anchors.rightMargin: 3
                            color: "#d1d1d2"
                            font.family: "Lato"
                            font.pixelSize: 11
                            horizontalAlignment: TextInput.AlignRight
                            validator: DoubleValidator{bottom: 0;}
                            readOnly: false
                        }

                        Text {
                            id: text_mm_raft_margin
                            height: parent.height
                            width: 25
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
                            width: parent.width - text_mm_raft_line_spacing.width
                            height: parent.height
                            text: qsTr("3.0")
                            anchors.top: parent.top
                            anchors.topMargin: 3
                            anchors.right: text_mm_raft_line_spacing.left
                            anchors.rightMargin: 3
                            color: "#d1d1d2"
                            font.family: "Lato"
                            font.pixelSize: 11
                            horizontalAlignment: TextInput.AlignRight
                            validator: DoubleValidator{bottom: 0;}
                            readOnly: false
                        }

                        Text {
                            id: text_mm_raft_line_spacing
                            height: parent.height
                            width: 25
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
                            width: parent.width - text_mm_raft_base_thickness.width
                            height: parent.height
                            text: qsTr("0.3")
                            anchors.top: parent.top
                            anchors.topMargin: 3
                            anchors.right: text_mm_raft_base_thickness.left
                            anchors.rightMargin: 3
                            color: "#d1d1d2"
                            font.family: "Lato"
                            font.pixelSize: 11
                            horizontalAlignment: TextInput.AlignRight
                            validator: DoubleValidator{bottom: 0;}
                            readOnly: false
                        }

                        Text {
                            id: text_mm_raft_base_thickness
                            height: parent.height
                            width: 25
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
                            width: parent.width - text_mm_raft_interface_thickness.width
                            height: parent.height
                            text: qsTr("0.27")
                            anchors.top: parent.top
                            anchors.topMargin: 3
                            anchors.right: text_mm_raft_interface_thickness.left
                            anchors.rightMargin: 3
                            color: "#d1d1d2"
                            font.family: "Lato"
                            font.pixelSize: 11
                            horizontalAlignment: TextInput.AlignRight
                            validator: DoubleValidator{bottom: 0;}
                            readOnly: false
                        }

                        Text {
                            id: text_mm_raft_interface_thickness
                            height: parent.height
                            width: 25
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
                            width: parent.width - text_mm_raft_interface_linewidth.width
                            height: parent.height
                            text: qsTr("0.4")
                            anchors.top: parent.top
                            anchors.topMargin: 3
                            anchors.right: text_mm_raft_interface_linewidth.left
                            anchors.rightMargin: 3
                            color: "#d1d1d2"
                            font.family: "Lato"
                            font.pixelSize: 11
                            horizontalAlignment: TextInput.AlignRight
                            validator: DoubleValidator{bottom: 0;}
                            readOnly: false
                        }

                        Text {
                            id: text_mm_raft_interface_linewidth
                            height: parent.height
                            width: 25
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
                            width: parent.width - text_mm_raft_airgap.width
                            height: parent.height
                            text: qsTr("0.22")
                            anchors.top: parent.top
                            anchors.topMargin: 3
                            anchors.right: text_mm_raft_airgap.left
                            anchors.rightMargin: 3
                            color: "#d1d1d2"
                            font.family: "Lato"
                            font.pixelSize: 11
                            horizontalAlignment: TextInput.AlignRight
                            validator: DoubleValidator{bottom: 0;}
                            readOnly: false
                        }

                        Text {
                            id: text_mm_raft_airgap
                            height: parent.height
                            width: 25
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
                    }
                }

                Rectangle {
                    id: rect_skirt_line_count
                    width: options_layer.line_width
                    height: options_layer.line_height
                    color: "#00000000"
                    anchors.top: rect_raft_airgap.bottom
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
                            width: parent.width - text_mm_skirt_line_count.width
                            height: parent.height
                            text: qsTr("1.0")
                            anchors.top: parent.top
                            anchors.topMargin: 3
                            anchors.right: text_mm_skirt_line_count.left
                            anchors.rightMargin: 3
                            color: "#d1d1d2"
                            font.family: "Lato"
                            font.pixelSize: 11
                            horizontalAlignment: TextInput.AlignRight
                            validator: DoubleValidator{bottom: 0;}
                            readOnly: false
                        }

                        Text {
                            id: text_mm_skirt_line_count
                            height: parent.height
                            width: 25
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
                            width: parent.width - text_mm_fill_overlap.width
                            height: parent.height
                            text: qsTr("15")
                            anchors.top: parent.top
                            anchors.topMargin: 3
                            anchors.right: text_mm_fill_overlap.left
                            anchors.rightMargin: 3
                            color: "#d1d1d2"
                            font.family: "Lato"
                            font.pixelSize: 11
                            horizontalAlignment: TextInput.AlignRight
                            validator: IntValidator{bottom: 0; top: 100;}
                            readOnly: false
                        }

                        Text {
                            id: text_mm_fill_overlap
                            height: parent.height
                            width: 25
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
                            width: parent.width - text_mm_skirt_minimal_length.width
                            height: parent.height
                            text: qsTr("150.0")
                            anchors.top: parent.top
                            anchors.topMargin: 3
                            anchors.right: text_mm_skirt_minimal_length.left
                            anchors.rightMargin: 3
                            color: "#d1d1d2"
                            font.family: "Lato"
                            font.pixelSize: 11
                            horizontalAlignment: TextInput.AlignRight
                            validator: DoubleValidator{bottom: 0;}
                            readOnly: false
                        }

                        Text {
                            id: text_mm_skirt_minimal_length
                            height: parent.height
                            width: 25
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
                    }
                }
            }
        }
    }

    function showLayer() {
        options_layer.enabled = true;
        options_layer.opacity = 1;
    }
}
