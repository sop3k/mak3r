import QtQuick 1.1

Rectangle {
    id: gauges
    width: 420
    height: 60
    color: "#00000000"

    Rectangle {
        id: temp_1
        width: parent.width
        height: 22
        color: "#00000000"
        anchors.top: parent.top
        anchors.topMargin: 0

        property real value: 0

        Rectangle {
            id: temp_1_text
            width: parent.width
            height: 20
            color: "#00000000"

            Text {
                id: text_1
                color: "#d1d1d2"
                text: qsTr("Extruder temp")
                font.pixelSize: 12
                font.family: lato_font.name
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: 0
            }

            Text {
                id: max_1
                color: "#d1d1d2"
                text: qsTr("max: ")
                font.pixelSize: 11
                font.family: lato_font.name
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: text_1.right
                anchors.leftMargin: 10
            }

            Rectangle {
                id: rect_temp1
                width: 40
                height: 20
                color: "#222222"
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: max_1.right
                anchors.leftMargin: 10

                TextInput {
                    id: temp1val
                    objectName: "temp1val"

                    property bool isCurrentInput: false

                    text: qsTr("0.0")
                    color: "#d1d1d2"
                    font.family: lato_font.name
                    font.pixelSize: 11
                    height: parent.height
                    width: parent.width
                    anchors.top: parent.top
                    anchors.topMargin: 3
                    horizontalAlignment: TextInput.AlignHCenter
                    validator: DoubleValidator{bottom: 0;}
                    readOnly: false;
                    cursorVisible: isCurrentInput
                    Keys.onPressed: {
                        if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                            mainwindow.setPrintTemp(text)
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            temp1val.forceActiveFocus();
                            temp1val.isCurrentInput = true;
                            tempbedval.isCurrentInput = false;
                        }
                    }
                }
            }

            Text {
                id: text_deg_temp1
                height: parent.height
                text: qsTr("C")
                color: "#d1d1d2"
                anchors.left: rect_temp1.right
                anchors.leftMargin: 4
                anchors.top: parent.top
                anchors.topMargin: 3
                horizontalAlignment: Text.AlignHCenter
                font.pixelSize: 11
                font.family: lato_font.name
            }

            Text {
                id: text_current_temp_1
                color: "#d1d1d2"
                text: qsTr("current:")
                font.pixelSize: 11
                font.family: lato_font.name
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: text_deg_temp1.right
                anchors.leftMargin: 10
            }

            Text {
                id: current_temp_1
                color: "#d1d1d2"
                text: qsTr("")
                font.pixelSize: 11
                font.family: lato_font.name
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: text_current_temp_1.right
                anchors.leftMargin: 5
            }
        }

        Rectangle {
            id: temp_1_bars
            width: parent.width
            height: 3
            color: "#00000000"
            anchors.top: temp_1_text.bottom
            anchors.topMargin: 2

            Rectangle {
                id: bar_1
                color: "#00000000"
                border.color: "#000000"
                anchors.fill: parent
            }

            Rectangle {
                id: temp_1_full
                width: temp_1.value * parent.width
                height: parent.height
                color: "#ff5724"
                border.color: "#000000"
                anchors.left: parent.left
                anchors.leftMargin: 0
                Behavior on width { PropertyAnimation {} }
            }
        }
    }

    Rectangle {
        id: temp_bed
        width: parent.width
        height: 22
        color: "#00000000"
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 0

        property real value: 0

        Rectangle {
            id: temp_bed_text
            width: parent.width
            height: 20
            color: "#00000000"

            Text {
                id: text_bed
                width: text_1.width
                color: "#d1d1d2"
                text: qsTr("Bed temp")
                font.pixelSize: 12
                font.family: lato_font.name
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: 0
            }

            Text {
                id: max_bed
                color: "#d1d1d2"
                text: qsTr("max: ")
                font.pixelSize: 11
                font.family: lato_font.name
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: text_bed.right
                anchors.leftMargin: 10
            }

            Rectangle {
                id: rect_tempbed
                width: 40
                height: 20
                color: "#222222"
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: max_bed.right
                anchors.leftMargin: 10

                TextInput {
                    id: tempbedval
                    objectName: "tempbedval"

                    property bool isCurrentInput: false

                    text: qsTr("0.0")
                    color: "#d1d1d2"
                    font.family: lato_font.name
                    font.pixelSize: 11
                    height: parent.height
                    width: parent.width
                    anchors.top: parent.top
                    anchors.topMargin: 3
                    horizontalAlignment: TextInput.AlignHCenter
                    validator: DoubleValidator{bottom: 0;}
                    readOnly: false;
                    cursorVisible: isCurrentInput
                    Keys.onPressed: {
                        if (event.key == Qt.Key_Enter || event.key == Qt.Key_Return) {
                            mainwindow.setBedTemp(text)
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            tempbedval.forceActiveFocus();
                            tempbedval.isCurrentInput = true;
                            temp1val.isCurrentInput = false;
                        }
                    }
                }
            }

            Text {
                id: text_deg_tempbed
                height: parent.height
                text: qsTr("C")
                color: "#d1d1d2"
                anchors.left: rect_tempbed.right
                anchors.leftMargin: 4
                anchors.top: parent.top
                anchors.topMargin: 3
                horizontalAlignment: Text.AlignHCenter
                font.pixelSize: 11
                font.family: lato_font.name
            }

            Text {
                id: text_current_temp_bed
                color: "#d1d1d2"
                text: qsTr("current:")
                font.pixelSize: 11
                font.family: lato_font.name
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: text_deg_tempbed.right
                anchors.leftMargin: 10
            }

            Text {
                id: current_temp_bed
                color: "#d1d1d2"
                text: qsTr("")
                font.pixelSize: 11
                font.family: lato_font.name
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: text_current_temp_bed.right
                anchors.leftMargin: 5
            }
        }

        Rectangle {
            id: temp_bed_bars
            width: parent.width
            height: 3
            color: "#00000000"
            anchors.top: temp_bed_text.bottom
            anchors.topMargin: 2

            Rectangle {
                id: bar_bed
                color: "#00000000"
                border.color: "#000000"
                anchors.fill: parent
            }

            Rectangle {
                id: temp_bed_full
                color: "#ff5724"
                width: temp_bed.value * parent.width
                height: parent.height
                border.color: "#000000"
                anchors.left: parent.left
                anchors.leftMargin: 0

                Behavior on width { PropertyAnimation {} }
            }
        }
    }

    function setPrinttempValue(val) {
        temp_1.value = val;
    }

    function setBedtempValue(val) {
        temp_bed.value = val;
    }

    function setCurrentPrinttemp(temp) {
        current_temp_1.text = temp
    }

    function setCurrentBedtemp(temp) {
        current_temp_bed.text = temp
    }

    function setTemperatures(printtemp, bedtemp) {
        temp1val.text = qsTr(printtemp)
        tempbedval.text = qsTr(bedtemp)
    }
}
