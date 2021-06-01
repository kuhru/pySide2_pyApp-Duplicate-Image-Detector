import QtQuick 2.3
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Dialogs 1.3

Window {
    id: mainDialog
    property color bgColor: "#0a0f18"
    property color primaryColor: "#dbdddf"
    property color accentColor: "#e14d4d"
    property string primaryFont: "Bahnschrift"

    width: 900
    height: 600
    title: "Running Your Search"
//    standardButtons: StandardButton.Save | StandardButton.Cancel

//    contentItem: Rectangle {
//        id: dialogBackground
//        color: bgColor
//        anchors.fill: parent
//    }

    onClosing: {
        consoleOut.text = ""
        circularProgress.value = 0
        backend.ensureExit()
    }

    Rectangle {
        id: generalBar
        width: mainDialog.width
        height: 150
        color: bgColor

        anchors.top: parent.top
        anchors.topMargin: 0

        Label {
            id: runningNow
            text: "<i>running...</i>"

            color: accentColor
            font.family: primaryFont
            font.pointSize: 42
            font.bold: true
            textFormat: Text.RichText

            anchors.left: parent.left
            anchors.bottom: parent.bottom
            anchors.leftMargin: 50
        }

        CustomBtn {
            id: btnCancelDialog
            width: 160
            height: 60
            btnName: "cancel"
            fontNameSize: 24

            fontNameColor: bgColor
            btncolorDefault: accentColor
            btncolorPressed: "#d61313"
            btncolorMouseHover: "#ed3434"

            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.rightMargin: 50

            onClicked: {
//                Qt.quit()
                backend.stopRunning()
//                mainDialog.close()
            }
        }

        CustomBtn {
            id: btnOpenExport
            width: 220
            height: 60
            btnName: "show exports"
            fontNameSize: 24

            fontNameColor: bgColor
            btncolorDefault: accentColor
            btncolorPressed: "#d61313"
            btncolorMouseHover: "#ed3434"

            anchors.right: btnCancelDialog.left
            anchors.bottom: parent.bottom
            anchors.rightMargin: 30

            onClicked: { backend.openExportsFolder() }
        }
    }
    Rectangle {
        id: infoBox
        width: mainDialog.width
        color: bgColor

        anchors.top: generalBar.bottom
        anchors.topMargin: 0
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 0

        CircularProgress {
            id: circularProgress
            width: 250
            height: circularProgress.width
            anchors.verticalCenter: parent.verticalCenter
            textSize: 30
            textFontFamily: primaryFont
            value: 100

            textColor: accentColor
            progressColor: accentColor
            bgStrokeColor: "#00000000"
            samples: 16

            anchors.leftMargin: 50
            anchors.left: parent.left
//                anchors.rightMargin: 50
//                anchors.right: detailsShadowBox.left
        }

        Rectangle {
            id: detailsShadowBox
            color: "#313439"
            radius: 20
            border.width: 5
            implicitHeight: mainDialog.height*3/4
            implicitWidth: mainDialog.width*3/4

            anchors.left: circularProgress.right
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.leftMargin: 50
            anchors.topMargin: 50
            anchors.bottomMargin: 50
            anchors.rightMargin: 50

            Rectangle {
                id: detailsShowBox
                color: bgColor
                radius: 14
                border.width: 5
                anchors.fill: parent
                anchors.rightMargin: 10
                anchors.leftMargin: 10
                anchors.bottomMargin: 10
                anchors.topMargin: 10

                ScrollView {
                    id: consoleOutScroller
                    clip: true
                    anchors.fill: parent
                    contentWidth: 400
                    anchors.rightMargin: 15
                    anchors.leftMargin: 15
                    anchors.bottomMargin: 15
                    anchors.topMargin: 15

                    Text {
                        id: consoleOut
                        text: ""
                        color: accentColor
                        font.family: primaryFont
                        font.pixelSize: 18
                        wrapMode: Text.WrapAnywhere

                        anchors.rightMargin: 0
                        anchors.bottomMargin: 0
                        anchors.fill: parent

                    }
                }
            }
        }
    }

    Connections {
        target: backend
        // function onUpdateProgressLog(stringy){
        //     consoleOut.text += stringy
        // }
        function onCurrentProgressPerc(inty){
            console.log = inty
            circularProgress.value = inty
        }
        function onCurrentProgressLog(stringy){
            console.log += stringy
            consoleOut.text += stringy
        }

    }

}




/*##^##
Designer {
    D{i:0;formeditorZoom:0.5}
}
##^##*/
