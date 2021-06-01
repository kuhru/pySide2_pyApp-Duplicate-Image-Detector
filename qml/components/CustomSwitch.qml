import QtQuick 2.15
import QtQuick.Controls 2.15

    Switch {
        property string switchLabel: "Label"
        property string primaryFont: "Bahnschrift"
        property color primaryColor: "#dbdddf"
        property color accentColor: "#e14d4d"
        property string conditional: ""
        property bool startState: false

        id: control
        text: switchLabel
        checked: startState

        indicator: Rectangle {
            implicitWidth: 48
            implicitHeight: 26
            x: control.leftPadding
            y: parent.height / 2 - height / 2
            radius: 13
            color: control.checked ? accentColor : primaryColor
            border.color: control.checked ? accentColor : "#cccccc"

            Rectangle {
                x: control.checked ? parent.width - width : 0
                width: 26
                height: 26
                radius: 13
                color: control.down ? "#cccccc" : "#ffffff"
                border.color: control.checked ? (control.down ? accentColor : accentColor) : "#999999"
            }

        }

        contentItem: Text {
            text: switchLabel
            font.family: primaryFont
            font.pointSize: 14
            opacity: enabled ? 1.0 : 0.3
            color: control.down ? accentColor : primaryColor
            verticalAlignment: Text.AlignVCenter
            leftPadding: control.indicator.width + control.spacing
        }

        onToggled: {
            backend.changeAlgo(conditional)
        }

        Connections {
            target: backend
        }
    }

/*##^##
Designer {
    D{i:0;autoSize:true;formeditorZoom:1.25;height:50;width:200}
}
##^##*/
