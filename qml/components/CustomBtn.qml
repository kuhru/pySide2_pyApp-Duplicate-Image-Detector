import QtQuick 2.15
import QtQuick.Controls 2.15
import QtGraphicalEffects 1.15

Button {
    id: customBtn
    // CUSTOM PROPERTIES
    property string btnName: ""
    property int btnRadius: 10
    property int fontNameSize: 16
    property color fontNameColor: "#ffffff"

    // CLICK COLORS CHANGES
    property color btncolorDefault: "#222222"
    property color btncolorMouseHover: "#111111"
    property color btncolorPressed: "#000000"

    // CLICK ACTIVATION
    property color activeMenuColor: "#e14d4d"
    property bool isActiveBtn: false


    QtObject {
        id: internal
        property var dynamicColor: if(customBtn.down){
                                    customBtn.down ? btncolorPressed: btncolorDefault
                                   } else{
                                    customBtn.hovered ? btncolorMouseHover: btncolorDefault
                                   }
    }

    implicitWidth: 120
    implicitHeight: 40

    background: Rectangle {
        id: bgBtn
        color: internal.dynamicColor
        radius: btnRadius

        Rectangle {
            anchors{
                top: parent.top
                left: parent.left
                bottom: parent.bottom
            }
            color: activeMenuColor
            width: 3
            visible: isActiveBtn
        }

    }

    contentItem: Item {
        id: item1
        clip: true
        anchors {
            top: parent.top
            left: parent.left
            bottom: parent.bottom
            right: parent.right
        }
        Text {
            id: textBtn
            color: fontNameColor
            text: btnName
            font.family: "Bahnschrift"
            font.pointSize: fontNameSize
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
        }
    }
}

/*##^##
Designer {
    D{i:0;formeditorZoom:4}
}
##^##*/

