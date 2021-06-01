import QtQuick 2.0
import QtQuick.Controls 2.15

    Rectangle {
        property string slugLine: "Enter Path"
        property string setText: ""
        property string textFieldArea: "textFieldArea"
        property string primaryFont: "Bahnschrift"
        property int marginTop: 10
//        property string tellMeDestroy: "textFieldArea"
        property bool wantVisible: true

        id: textFieldArea
        height: 30
        radius: 15
        color: "#ffffff"
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.leftMargin: 10
        anchors.rightMargin: 10
        anchors.topMargin: marginTop

        ScrollView {
            id: scrollViewforTextBar
            anchors.fill: parent
            layer.smooth: true
            clip: true
            anchors.rightMargin: 5
            anchors.leftMargin: 5
            anchors.bottomMargin: 2
            anchors.topMargin: 2

            Text {

//                QtObject {
//                    id: textEditInternal
//                    property var defText: if(textEdit.focus){
//                                            (textEdit.text == slugLine) ? textEdit.text = "" : textEdit.text = "ok"
//                                              //        property int marginTop: 280
//                                          } else{
//                                            textEdit.text = slugLine
//                                          }
//                }

                id: textEdit
                text: setText

                anchors.fill: parent
                font.pixelSize: 12
                font.family: primaryFont
                anchors.rightMargin: -296
                anchors.bottomMargin: -12
                verticalAlignment: Text.AlignVCenter
                clip: true
            }
        }

//        CustomBtn {
//            id: deletionBtn
//            width: 30
//            height: 30
//            btnName: "X"
//            btnRadius: 15
//            fontNameSize: 20
//            fontNameColor: "#e14d4d"

//            anchors.verticalCenter: parent.verticalCenter
//            anchors.right: parent.right
//            anchors.rightMargin: -30
//            visible: wantVisible

//            onClicked: {
////                textFieldArea.destroy()
//                tellMeDestroy
//            }
//        }

        Connections {
            target: backend
        }
    }

/*##^##
Designer {
    D{i:0;formeditorZoom:1.66}
}
##^##*/
