import QtQuick 1.0

Rectangle {
    id: rectangle2
    width: 420
    height: 300
    color: "#00000000"

    Rectangle {
        id: rectangle1
        width: parent.height
        height: parent.height
        color: "#00000000"
        anchors.left: parent.left
        anchors.leftMargin: 0
        anchors.top: parent.top
        anchors.topMargin: 0

        Image {
            id: image_home_z
            anchors.right: parent.right
            anchors.rightMargin: 0
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 0
            source: "resources/axes/home_z.png"
        }

        Image {
            id: image_home_y
            anchors.right: parent.right
            anchors.rightMargin: 0
            anchors.top: parent.top
            anchors.topMargin: 0
            source: "resources/axes/home_y.png"
        }

        Image {
            id: image_home
            anchors.left: parent.left
            anchors.leftMargin: 0
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 0
            source: "resources/axes/home.png"
        }

        Image {
            id: image_home_x
            anchors.left: parent.left
            anchors.leftMargin: 0
            anchors.top: parent.top
            anchors.topMargin: 0
            source: "resources/axes/home_x.png"
        }

        MouseArea {
            id: mouse_area_home_x
            width: image_home_x.width
            height: image_home_x.height
            anchors.left: parent.left
            anchors.leftMargin: 0
            anchors.top: parent.top
            anchors.topMargin: 0

            onClicked: {
                mainwindow.homeAxis('x')
            }
        }

        MouseArea {
            id: mouse_area_home
            width: image_home.width
            height: image_home.height
            anchors.left: parent.left
            anchors.leftMargin: 0
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 0

            onClicked: {
                mainwindow.homeAxis('all')
            }
        }

        MouseArea {
            id: mouse_area_home_y
            width: image_home_y.width
            height: image_home_y.height
            anchors.right: parent.right
            anchors.rightMargin: 0
            anchors.top: parent.top
            anchors.topMargin: 0

            onClicked: {
                mainwindow.homeAxis('y')
            }
        }

        MouseArea {
            id: mouse_area_home_z
            width: image_home_z.width
            height: image_home_z.height
            anchors.right: parent.right
            anchors.rightMargin: 0
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 0

            onClicked: {
                mainwindow.homeAxis('z')
            }
        }

        Rectangle {
            id: top
            width: image_top.width
            height: image_top.height
            color: "#00000000"
            opacity: 1
            anchors.top: parent.top
            anchors.topMargin: 4
            anchors.horizontalCenter: parent.horizontalCenter

            Image {
                id: image_top
                source: "resources/axes/top.png"
            }

            MouseArea {
                id: mouse_area_top
                anchors.fill: parent

                Image {
                    id: image_y_plus
                    anchors.top: parent.top
                    anchors.topMargin: 20
                    anchors.horizontalCenter: parent.horizontalCenter
                    source: "resources/axes/yplus_arrow.png"
                }

                onClicked: {
                    console.log("plus y");
                }
            }
        }

        Rectangle {
            id: bottom
            width: image_bottom.width
            height: image_bottom.height
            color: "#00000000"
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 4
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top1
            anchors.topMargin: 0
            opacity: 1

            Image {
                id: image_bottom
                source: "resources/axes/bottom.png"
            }

            MouseArea {
                id: mouse_area_bottom
                anchors.fill: parent

                Image {
                    id: image_y_minus
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.bottom: parent.bottom
                    anchors.bottomMargin: 20
                    source: "resources/axes/yminus_arrow.png"
                }

                onClicked: {
                    console.log("minus y")
                }
            }
        }

        Rectangle {
            id: left
            width: image_left.width
            height: image_left.height
            color: "#00000000"
            anchors.left: parent.left
            anchors.leftMargin: 4
            anchors.verticalCenter: parent.verticalCenter
            anchors.top: parent.top1
            anchors.topMargin: 0
            anchors.bottom: parent.bottom1
            anchors.bottomMargin: 0
            opacity: 1

            Image {
                id: image_left
                source: "resources/axes/left.png"
            }

            MouseArea {
                id: mouse_area_left
                anchors.fill: parent

                Image {
                    id: image_x_minus
                    anchors.left: parent.left
                    anchors.leftMargin: 20
                    anchors.verticalCenter: parent.verticalCenter
                    source: "resources/axes/xminus_arrow.png"
                }

                onClicked: {
                    var tg = (image_left.width - mouseX) / (image_left.height/2 - mouseY);
                    if (mouseX > 39 && mouseY < image_left.height/2 && tg < 1) {
                        topClicked();
                    } else {
                        console.log("minus x");
                    }
                }
            }
        }

        Rectangle {
            id: right
            width: image_right.width
            height: image_right.height
            color: "#00000000"
            anchors.right: parent.right
            anchors.rightMargin: 4
            anchors.top: parent.top1
            anchors.topMargin: 0
            anchors.bottom: parent.bottom1
            anchors.bottomMargin: 0
            anchors.verticalCenter: parent.verticalCenter
            anchors.leftMargin: 0
            opacity: 1
            anchors.left: parent.left1

            Image {
                id: image_right
                source: "resources/axes/right.png"
            }

            MouseArea {
                id: mouse_area_right
                anchors.fill: parent

                Image {
                    id: image_x_plus
                    anchors.right: parent.right
                    anchors.rightMargin: 20
                    anchors.verticalCenter: parent.verticalCenter
                    source: "resources/axes/xplus_arrow.png"
                }

                onClicked: {
                    console.log("plus x")
                }
            }
        }

    }

    Rectangle {
        id: minus_z_10
        width: 100
        height: 46
        color: "#51545b"
        radius: 5
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 0
        anchors.right: parent.right
        anchors.rightMargin: 0

        MouseArea {
            id: mouse_area_minus_z_10
            anchors.fill: parent

            onClicked: {
                mainwindow.moveZ(-10.0)
            }
        }
    }

    Rectangle {
        id: minus_z_1
        width: 100
        height: 46
        color: "#51545b"
        radius: 5
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 48
        anchors.right: parent.right
        anchors.rightMargin: 0

        MouseArea {
            id: mouse_area_minus_z_1
            anchors.fill: parent

            onClicked: {
                mainwindow.moveZ(-1.0)
            }
        }
    }

    Rectangle {
        id: minus_z_01
        width: 100
        height: 46
        color: "#51545b"
        radius: 5
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 96
        anchors.right: parent.right
        anchors.rightMargin: 0

        MouseArea {
            id: mouse_area_minus_z_01
            anchors.fill: parent

            onClicked: {
                mainwindow.moveZ(-0.1)
            }
        }
    }

    Rectangle {
        id: plus_z_10
        width: 100
        height: 46
        color: "#51545b"
        radius: 5
        anchors.top: parent.top
        anchors.topMargin: 0
        anchors.rightMargin: 0
        anchors.right: parent.right

        MouseArea {
            id: mouse_area_plus_z_10
            anchors.fill: parent

            onClicked: {
                mainwindow.moveZ(10.0)
            }
        }
    }

    Rectangle {
        id: plus_z_1
        width: 100
        height: 46
        color: "#51545b"
        radius: 5
        anchors.top: parent.top
        anchors.topMargin: 48
        anchors.rightMargin: 0
        anchors.right: parent.right

        MouseArea {
            id: mouse_area5_plus_z_1
            anchors.fill: parent

            onClicked: {
                mainwindow.moveZ(1.0)
            }
        }
    }

    Rectangle {
        id: plus_z_01
        width: 100
        height: 46
        color: "#51545b"
        radius: 5
        anchors.top: parent.top
        anchors.topMargin: 96
        anchors.rightMargin: 0
        anchors.right: parent.right

        MouseArea {
            id: mouse_area_plus_z_01
            anchors.fill: parent

            onClicked: {
                mainwindow.moveZ(0.1)
            }
        }
    }

    function topClicked() {
        console.log("plus y")
    }
}
