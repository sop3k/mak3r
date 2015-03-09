// import QtQuick 1.0 // to target S60 5th Edition or Maemo 5
import QtQuick 1.1
import QtQuick 1.0

Rectangle {
    id: wizard
    width: 700
    height: 500
    color: "#51545b"
    // clip: false
    enabled: false
    opacity: 0

    state: "WELCOME"

    Rectangle {
        id: header
        x: 0
        y: 0
        width: parent.width
        height: 34
        color: "#3f4245"

        Text {
            id: title
            color: "#d1d1d2"
            text: qsTr("Configuration wizard")
            verticalAlignment: Text.AlignVCenter
            anchors.fill: parent
            horizontalAlignment: Text.AlignHCenter
            font.pixelSize: 15
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
                hideLayer();
                // wizard.enabled = false;
                // wizard.opacity = 0;
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
        id: text_container
        width: 400
        height: 200
        color: "#00000000"
        anchors.left: parent.left
        anchors.leftMargin: 50
        anchors.top: parent.top
        anchors.topMargin: 80

        Rectangle {
            id: welcome_note
            color: "#00000000"
            anchors.fill: parent
            opacity: 1

            Text {
                id: text4
                color: "#a7a8ab"
                text: qsTr("This wizard help you set up Mak3r for your machine")
                font.pixelSize: 12
                anchors.left: parent.left
                anchors.leftMargin: 0
                anchors.top: text3.bottom
                anchors.topMargin: 20
            }

            Text {
                id: text3
                // color: "#ffffff"
                color: "#d1d1d2"
                font.pixelSize: 26
                font.bold: false
                text: qsTr("machine wizzard")
                anchors.left: parent.left
                anchors.leftMargin: 0
                anchors.top: text1.bottom
                anchors.topMargin: 0
            }

            Text {
                id: text2
                y: 0
                color: "#ffffff"
                font.pixelSize: 26
                font.bold: true
                text: qsTr("new")
                anchors.left: text1.right
                anchors.leftMargin: 10
            }

            Text {
                id: text1
                // color: "#ffffff"
                color: "#d1d1d2"
                font.bold: false
                font.pixelSize: 26
                text: qsTr("Add")
                anchors.left: parent.left
                anchors.leftMargin: 0
                anchors.top: parent.top
                anchors.topMargin: 0
            }
        }

        Rectangle {
            id: settings_panel
            anchors.fill: parent
            color: "#00000000"
            opacity: 0

            property TextInput current_input: null

            Text {
                id: settings_panel_text3
                color: "#d1d1d2"
                font.pixelSize: 26
                font.bold: false
                text: qsTr("machine settings")
                anchors.left: parent.left
                anchors.leftMargin: 0
                anchors.top: settings_panel_text1.bottom
                anchors.topMargin: 0
            }

            Text {
                id: settings_panel_text2
                color: "#d1d1d2"
                font.pixelSize: 26
                font.bold: false
                text: qsTr("your")
                anchors.left: settings_panel_text1.right
                anchors.leftMargin: 10
            }

            Text {
                id: settings_panel_text1
                color: "#ffffff"
                font.bold: true
                font.pixelSize: 26
                text: qsTr("Enter")
                anchors.left: parent.left
                anchors.leftMargin: 0
                anchors.top: parent.top
                anchors.topMargin: 0
            }

            Rectangle {
                id: rect_machine_name
                width: options_layer.line_width
                height: options_layer.line_height
                color: "#00000000"
                anchors.top: settings_panel_text3.bottom
                anchors.topMargin: options_layer.row_spacing*3

                Text {
                    id: text_machine_name
                    color: "#a8a8a8"
                    text: qsTr("Machine name")
                    anchors.left: parent.left
                    anchors.leftMargin: 0
                    anchors.verticalCenter: parent.verticalCenter
                    verticalAlignment: Text.AlignVCenter
                    font.pixelSize: 11
                    font.family: lato_font.name
                }

                Rectangle {
                    id: machine_name
                    width: options_layer.input_width
                    height: 20
                    color: "#333333"
                    radius: 1
                    border.color: "#333333"
                    anchors.right: parent.right
                    anchors.rightMargin: 0
                    anchors.verticalCenter: parent.verticalCenter

                    TextInput {
                        id: text_input_machine_name
                        objectName: "machine_name"
                        height: parent.height
                        anchors.top: parent.top
                        anchors.topMargin: 3
                        anchors.right: parent.right
                        anchors.rightMargin: 3
                        anchors.left: parent.left
                        anchors.leftMargin: 4
                        color: "#d1d1d2"
                        font.family: "Lato"
                        font.pixelSize: 11
                        horizontalAlignment: TextInput.AlignHCenter
                        validator: RegExpValidator { regExp: /\w{1,30}/ }
                        readOnly: false
                        cursorVisible: settings_panel.current_input == text_input_machine_name
                        // Keys.onPressed: {
                        //     if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                        //         mainwindow.onFloatSettingChange(text_input_machine_name.objectName, text)
                        //     }
                        // }
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            text_input_machine_name.forceActiveFocus();
                            settings_panel.current_input = text_input_machine_name;
                        }
                    }
                }
            }

            Rectangle {
                id: rect_machine_width
                width: options_layer.line_width
                height: options_layer.line_height
                color: "#00000000"
                anchors.top: rect_machine_name.bottom
                anchors.topMargin: options_layer.row_spacing

                Text {
                    id: text_machine_width
                    color: "#a8a8a8"
                    text: qsTr("Machine width")
                    anchors.left: parent.left
                    anchors.leftMargin: 0
                    anchors.verticalCenter: parent.verticalCenter
                    verticalAlignment: Text.AlignVCenter
                    font.pixelSize: 11
                    font.family: lato_font.name
                }

                Rectangle {
                    id: machine_width
                    width: options_layer.input_width
                    height: 20
                    color: "#333333"
                    radius: 1
                    border.color: "#333333"
                    anchors.right: parent.right
                    anchors.rightMargin: 0
                    anchors.verticalCenter: parent.verticalCenter

                    TextInput {
                        id: text_input_machine_width
                        objectName: "machine_width"
                        height: parent.height
                        anchors.top: parent.top
                        anchors.topMargin: 3
                        anchors.right: text_mm_machine_width.left
                        anchors.rightMargin: 3
                        anchors.left: parent.left
                        anchors.leftMargin: 4
                        color: "#d1d1d2"
                        font.family: "Lato"
                        font.pixelSize: 11
                        horizontalAlignment: TextInput.AlignHCenter
                        validator: DoubleValidator{bottom: 0; top: 10;}
                        readOnly: false
                        cursorVisible: settings_panel.current_input == text_input_machine_width
                        // Keys.onPressed: {
                        //     if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                        //         mainwindow.onFloatSettingChange(text_input_machine_width.objectName, text)
                        //     }
                        // }
                    }

                    Text {
                        id: text_mm_machine_width
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
                            text_input_machine_width.forceActiveFocus();
                            settings_panel.current_input = text_input_machine_width;
                        }
                    }
                }
            }

            Rectangle {
                id: rect_machine_depth
                width: options_layer.line_width
                height: options_layer.line_height
                color: "#00000000"
                anchors.top: rect_machine_width.bottom
                anchors.topMargin: options_layer.row_spacing

                Text {
                    id: text_machine_depth
                    color: "#a8a8a8"
                    text: qsTr("Machine depth")
                    anchors.left: parent.left
                    anchors.leftMargin: 0
                    anchors.verticalCenter: parent.verticalCenter
                    verticalAlignment: Text.AlignVCenter
                    font.pixelSize: 11
                    font.family: lato_font.name
                }

                Rectangle {
                    id: machine_depth
                    width: options_layer.input_width
                    height: 20
                    color: "#333333"
                    radius: 1
                    border.color: "#333333"
                    anchors.right: parent.right
                    anchors.rightMargin: 0
                    anchors.verticalCenter: parent.verticalCenter

                    TextInput {
                        id: text_input_machine_depth
                        objectName: "machine_depth"
                        height: parent.height
                        anchors.top: parent.top
                        anchors.topMargin: 3
                        anchors.right: text_mm_machine_depth.left
                        anchors.rightMargin: 3
                        anchors.left: parent.left
                        anchors.leftMargin: 4
                        color: "#d1d1d2"
                        font.family: "Lato"
                        font.pixelSize: 11
                        horizontalAlignment: TextInput.AlignHCenter
                        validator: DoubleValidator{bottom: 0; top: 10;}
                        readOnly: false
                        cursorVisible: settings_panel.current_input == text_input_machine_depth
                        // Keys.onPressed: {
                        //     if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                        //         mainwindow.onFloatSettingChange(text_input_machine_depth.objectName, text)
                        //     }
                        // }
                    }

                    Text {
                        id: text_mm_machine_depth
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
                            text_input_machine_depth.forceActiveFocus();
                            settings_panel.current_input = text_input_machine_depth;
                        }
                    }
                }
            }

            Rectangle {
                id: rect_machine_height
                width: options_layer.line_width
                height: options_layer.line_height
                color: "#00000000"
                anchors.top: rect_machine_depth.bottom
                anchors.topMargin: options_layer.row_spacing

                Text {
                    id: text_machine_height
                    color: "#a8a8a8"
                    text: qsTr("Machine height")
                    anchors.left: parent.left
                    anchors.leftMargin: 0
                    anchors.verticalCenter: parent.verticalCenter
                    verticalAlignment: Text.AlignVCenter
                    font.pixelSize: 11
                    font.family: lato_font.name
                }

                Rectangle {
                    id: machine_height
                    width: options_layer.input_width
                    height: 20
                    color: "#333333"
                    radius: 1
                    border.color: "#333333"
                    anchors.right: parent.right
                    anchors.rightMargin: 0
                    anchors.verticalCenter: parent.verticalCenter

                    TextInput {
                        id: text_input_machine_height
                        objectName: "machine_height"
                        height: parent.height
                        anchors.top: parent.top
                        anchors.topMargin: 3
                        anchors.right: text_mm_machine_height.left
                        anchors.rightMargin: 3
                        anchors.left: parent.left
                        anchors.leftMargin: 4
                        color: "#d1d1d2"
                        font.family: "Lato"
                        font.pixelSize: 11
                        horizontalAlignment: TextInput.AlignHCenter
                        validator: DoubleValidator{bottom: 0; top: 10;}
                        readOnly: false
                        cursorVisible: settings_panel.current_input == text_input_machine_height
                        // Keys.onPressed: {
                        //     if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                        //         mainwindow.onFloatSettingChange(text_input_machine_height.objectName, text)
                        //     }
                        // }
                    }

                    Text {
                        id: text_mm_machine_height
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
                            text_input_machine_height.forceActiveFocus();
                            settings_panel.current_input = text_input_machine_height;
                        }
                    }
                }
            }

            Rectangle {
                id: rect_nozzle_size
                width: options_layer.line_width
                height: options_layer.line_height
                color: "#00000000"
                anchors.top: rect_machine_height.bottom
                anchors.topMargin: options_layer.row_spacing

                Text {
                    id: text_nozzle_size
                    color: "#a8a8a8"
                    text: qsTr("Nozzle size")
                    anchors.left: parent.left
                    anchors.leftMargin: 0
                    anchors.verticalCenter: parent.verticalCenter
                    verticalAlignment: Text.AlignVCenter
                    font.pixelSize: 11
                    font.family: lato_font.name
                }

                Rectangle {
                    id: nozzle_size
                    width: options_layer.input_width
                    height: 20
                    color: "#333333"
                    radius: 1
                    border.color: "#333333"
                    anchors.right: parent.right
                    anchors.rightMargin: 0
                    anchors.verticalCenter: parent.verticalCenter

                    TextInput {
                        id: text_input_nozzle_size
                        objectName: "nozzle_size"
                        height: parent.height
                        anchors.top: parent.top
                        anchors.topMargin: 3
                        anchors.right: text_mm_nozzle_size.left
                        anchors.rightMargin: 3
                        anchors.left: parent.left
                        anchors.leftMargin: 4
                        color: "#d1d1d2"
                        font.family: "Lato"
                        font.pixelSize: 11
                        horizontalAlignment: TextInput.AlignHCenter
                        validator: DoubleValidator{bottom: 0; top: 10;}
                        readOnly: false
                        cursorVisible: settings_panel.current_input == text_input_nozzle_size
                        // Keys.onPressed: {
                        //     if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                        //         mainwindow.onFloatSettingChange(text_input_nozzle_size.objectName, text)
                        //     }
                        // }
                    }

                    Text {
                        id: text_mm_nozzle_size
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
                            text_input_nozzle_size.forceActiveFocus();
                            settings_panel.current_input = text_input_nozzle_size;
                        }
                    }
                }
            }

            Rectangle {
                id: rect_heated_bed
                width: options_layer.line_width
                height: options_layer.line_height
                color: "#00000000"
                anchors.top: rect_nozzle_size.bottom
                anchors.topMargin: options_layer.row_spacing

                Text {
                    id: text_heated_bed
                    color: "#a8a8a8"
                    text: qsTr("Heated bed")
                    anchors.left: parent.left
                    anchors.leftMargin: 0
                    anchors.verticalCenter: parent.verticalCenter
                    verticalAlignment: Text.AlignVCenter
                    font.pixelSize: 11
                    font.family: lato_font.name
                }

                Rectangle {
                    id: heated_bed
                    objectName: "heated_bed"
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
                        id: mouse_area_heated_bed
                        anchors.fill: parent
                        onClicked: {
                            heated_bed.isActive = !heated_bed.isActive
                            // mainwindow.onBoolSettingChange(heated_bed.objectName, heated_bed.isActive)
                        }

                        Image {
                            id: image_heated_bed
                            opacity: heated_bed.isActive ? 1 : 0
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.verticalCenter: parent.verticalCenter
                            source: "resources/icons/checked.png"
                        }
                    }
                }
            }

            Rectangle {
                id: rect_bed_center
                width: options_layer.line_width
                height: options_layer.line_height
                color: "#00000000"
                anchors.top: rect_heated_bed.bottom
                anchors.topMargin: options_layer.row_spacing

                Text {
                    id: text_bed_center
                    color: "#a8a8a8"
                    text: qsTr("Bed center is (0,0,0)")
                    anchors.left: parent.left
                    anchors.leftMargin: 0
                    anchors.verticalCenter: parent.verticalCenter
                    verticalAlignment: Text.AlignVCenter
                    font.pixelSize: 11
                    font.family: lato_font.name
                }

                Rectangle {
                    id: bed_center
                    objectName: "bed_center"
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
                        id: mouse_area_bed_center
                        anchors.fill: parent
                        onClicked: {
                            bed_center.isActive = !bed_center.isActive
                            // mainwindow.onBoolSettingChange(bed_center.objectName, bed_center.isActive)
                        }

                        Image {
                            id: image_bed_center
                            opacity: bed_center.isActive ? 1 : 0
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.verticalCenter: parent.verticalCenter
                            source: "resources/icons/checked.png"
                        }
                    }
                }
            }
        }
    }

    Rectangle {
        id: buttons_container
        y: 0
        width: 400
        height: 32
        color: "#00000000"
        anchors.left: parent.left
        anchors.leftMargin: 50
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 50

        Rectangle {
            id: button_cancel
            width: 100
            height: 32
            color: "#3f4245"

            Text {
                color: "#a7a8ab"
                text: qsTr("Cancel")
                font.family: "Arial"
                font.bold: false
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                anchors.fill: parent
                font.pixelSize: 13
            }

            MouseArea {
                id: mouse_area_cancel
                anchors.fill: parent
                onClicked: {
                    wizard.hideLayer();
                }
            }
        }

        Rectangle {
            id: button_next
            width: 100
            height: 32
            color: "#ff5724"
            anchors.left: button_cancel.right
            anchors.leftMargin: 10

            Text {
                id: button_next_text
                color: "#ffffff"
                text: qsTr("Next")
                font.family: "Arial"
                font.bold: false
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                anchors.fill: parent
                font.pixelSize: 13
            }

            MouseArea {
                id: mouse_area_next
                anchors.fill: parent
                onClicked: {
                    if (wizard.state == "SETTINGS") {
                        mainwindow.saveMachineSettings();
                        wizard.hideLayer()
                        wizard.state = "WELCOME";
                    } else if (wizard.state == "WELCOME") {
                        wizard.state = "SETTINGS";
                    }
                }
            }
        }
    }

    states: [
        State {
            name: "WELCOME"
            
            PropertyChanges {
                target: welcome_note
                opacity: 1
            }

            PropertyChanges {
                target: settings_panel
                opacity: 0
            }
        },

        State {
            name: "SETTINGS"
            
            PropertyChanges {
                target: settings_panel
                opacity: 1
            }

            PropertyChanges {
                target: welcome_note
                opacity: 0
            }

            PropertyChanges {
                target: button_next_text
                text: qsTr("Finish")
            }
        }
    ]

    function showLayer() {
        wizard.enabled = true;
        wizard.opacity = 1;
        graphicsscene.setLayerOn();
    }

    function hideLayer() {
        wizard.enabled = false;
        wizard.opacity = 0;
        graphicsscene.setLayerOff();
    }

    function getMachineSettings() {
        return {
            'machine_name': text_input_machine_name,
            'machine_width': text_input_machine_width,
            'machine_depth': text_input_machine_depth,
            'machine_height': text_input_machine_height,
            'nozzle_size': text_input_nozzle_size,
            'has_heated_bed': heated_bed.isActive,
            'machine_center_is_zero': bed_center.isActive
        }
    }

}
