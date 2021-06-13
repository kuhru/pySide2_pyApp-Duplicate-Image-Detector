import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Dialogs 1.2
import "components"

Window {
    // CUSTOM PROPERTIES
    property color bgColor: "#0a0f18"
    property color primaryColor: "#dbdddf"
    property color accentColor: "#e14d4d"
    property string primaryFont: "Bahnschrift"

    id: mainWindow
    width: 1000
    height: 707
    minimumWidth: 1000
    minimumHeight: 707
    maximumWidth: 1000
    maximumHeight: 707
    visible: true
    color: "#222222"
    title: qsTr("Duplicate Image Detector")

    onClosing: {
        backend.ensureExit()
    }

    Rectangle {
        id: windowContentBox
        color: "#00000000"

        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom

        anchors.leftMargin: 10
        anchors.rightMargin: 450
        anchors.topMargin: 10
        anchors.bottomMargin: 10

        Rectangle {
            id: titleBoxArea
            height: 260
            color: bgColor

            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top

            anchors.leftMargin: 0
            anchors.rightMargin: 0
            anchors.topMargin: 0

            Label {
                id: label
                width: 340
                text: qsTr("Duplicate Image Detector")

                color: accentColor
                font.family: primaryFont
                font.pointSize: 42
                font.bold: true
                wrapMode: Text.WordWrap
                textFormat: Text.RichText

                anchors.bottom: parent.bottom
                anchors.bottomMargin: 10
                anchors.horizontalCenterOffset: 0
                anchors.horizontalCenter: parent.horizontalCenter

                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter

            }

        }

        Rectangle {
            id: selectionChoiceArea
            height: 100
            color: bgColor

            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: titleBoxArea.bottom

            anchors.leftMargin: 0
            anchors.rightMargin: 0
            anchors.topMargin: 0

            Rectangle {
                id: selectionChoiceAreaAlign
                width: 260
                color: bgColor
                height: 100

                anchors.horizontalCenter: parent.horizontalCenter

                CustomBtn {
                    id: btnInclusion
                    anchors.left: parent.left
                    btnName: "include"
                    isActiveBtn: true
                    onClicked: {
                        btnInclusion.isActiveBtn = true
                        btnExclusion.isActiveBtn = false
                        //                        stackView.push(Qt.resolvedUrl("components/InclusionPane.qml"))
                        inclusionPane.visible = true
                        exclusionPane.visible = false
                    }

                    anchors.bottom: parent.bottom
                    anchors.leftMargin: 0
                    anchors.bottomMargin: 20

                }

                CustomBtn {
                    id: btnExclusion
                    anchors.right: parent.right
                    btnName: "exclude"
                    isActiveBtn: false
                    onClicked: {
                        btnInclusion.isActiveBtn = false
                        btnExclusion.isActiveBtn = true
                        //                        stackView.push(Qt.resolvedUrl("components/ExclusionPane.qml"))
                        inclusionPane.visible = false
                        exclusionPane.visible = true
                    }

                    anchors.bottom: parent.bottom
                    anchors.rightMargin: 0
                    anchors.bottomMargin: 20
                }

            }

        }

        Rectangle {
            id: selectionPageArea
            color: bgColor

            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: selectionChoiceArea.bottom
            anchors.bottom: runningBoxArea.top
            anchors.bottomMargin: 0
            clip: true

            anchors.leftMargin: 0
            anchors.rightMargin: 0
            anchors.topMargin: 0

            //            StackView {
            //                id: stackView
            //                x: 140
            //                y: 20
            //                width: 420
            //                anchors.top: parent.top
            //                anchors.bottom: parent.bottom
            //                anchors.bottomMargin: 0
            //                anchors.horizontalCenter: parent.horizontalCenter
            //                initialItem: Qt.resolvedUrl("components/InclusionPane.qml")
            //            }
            //            Loader {
            //                id: inclusionPane
            //                x: 140
            //                y: 20
            //                width: 420
            //                anchors.top: parent.top
            //                anchors.bottom: parent.bottom
            //                anchors.bottomMargin: 0
            //                anchors.horizontalCenter: parent.horizontalCenter
            //                source: Qt.resolvedUrl("components/InclusionPane.qml")
            //                visible: true
            //            }
            //            Loader {
            //                id: exclusionPane
            //                x: 140
            //                y: 20
            //                width: 420
            //                anchors.top: parent.top
            //                anchors.bottom: parent.bottom
            //                anchors.bottomMargin: 0
            //                anchors.horizontalCenter: parent.horizontalCenter
            //                source: Qt.resolvedUrl("components/ExclusionPane.qml")
            //                visible: false
            //            }

            InclusionPane {
                id: inclusionPane
                x: 140
                y: 20
                width: 420
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 0
                anchors.horizontalCenter: parent.horizontalCenter
                visible: true
            }

            ExclusionPane {
                id: exclusionPane
                x: 140
                y: 20
                width: 420
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 0
                anchors.horizontalCenter: parent.horizontalCenter
                visible: false
            }


        }

        Rectangle {
            id: runningBoxArea
            color: bgColor
            height: 80

            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom

            anchors.leftMargin: 0
            anchors.rightMargin: 0
            anchors.bottomMargin: 0

            CustomBtn {
                btnName: "START"
                fontNameColor: accentColor
                fontNameSize: 18
                anchors.verticalCenter: parent.verticalCenter
                anchors.horizontalCenter: parent.horizontalCenter

                onClicked: {
                    window2.visible = true
//                    coverRect.visible = true
                    backend.startRunning()

                }

            }

        }

        Running {
            id: window2
            visible: false



        }

    }

    Rectangle {
        id: windowContentBoxOther
        color: "#00000000"

        anchors.left: windowContentBox.right
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom

        anchors.leftMargin: 10
        anchors.rightMargin: 10
        anchors.topMargin: 10
        anchors.bottomMargin: 10

        Rectangle {
            id: algoChooser
            height: 344
            color: bgColor
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.rightMargin: 0
            anchors.leftMargin: 0
            anchors.topMargin: 0

            Label {
                id: algoChooserTitle
                text: qsTr("choose algorithm(s)")

                color: accentColor
                font.family: primaryFont
                font.pointSize: 25
                font.bold: true

                anchors.right: parent.right
                anchors.top: parent.top
                anchors.topMargin: 25
                anchors.rightMargin: 25

            }

            CustomSwitch {
                id: switchP
                switchLabel: "pHash"
                conditional: "pHash"
                startState: true

                anchors.left: parent.left
                anchors.bottom: switchW.top
                anchors.bottomMargin: 16
                anchors.leftMargin: 25
            }
            CustomSwitch {
                id: switchW
                switchLabel: "wHash"
                conditional: "wHash"

                anchors.left: parent.left
                anchors.bottom: switchD.top
                anchors.bottomMargin: 16
                anchors.leftMargin: 25
            }
            CustomSwitch {
                id: switchD
                switchLabel: "dHash"
                conditional: "dHash"

                anchors.left: parent.left
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 20
                anchors.leftMargin: 25
            }
//            CustomSwitch {
//                id: switchMy
//                text: "Custom Algorithm"
//                switchLabel: "Custom Algorithm"
//                conditional: "myHash"

//                anchors.left: parent.left
//                anchors.bottom: parent.bottom
//                anchors.bottomMargin: 20
//                anchors.leftMargin: 25
//            }

        }

        Rectangle {
            id: customizationsArea
            color: bgColor

            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: algoChooser.bottom
            anchors.bottom: reverseOptionsArea.top
            anchors.bottomMargin: 10
            anchors.topMargin: 10

            anchors.rightMargin: 0
            anchors.leftMargin: 0

            Label {
                id: cus
                text: qsTr("select export location")

                color: accentColor
                font.family: primaryFont
                font.pointSize: 25
                font.bold: true

                anchors.right: parent.right
                anchors.bottom: exportPathHolder.top
                anchors.bottomMargin: 30
                anchors.rightMargin: 25

            }

            Rectangle {
                id: exportPathHolder
                width: 200
                height: 40
                color: "#ffffff"
                radius: 20
                anchors.bottom: customizationsArea.bottom
                anchors.bottomMargin: 20
                clip: true


                anchors {
                    right: parent.right
                    left: getExportFolder.right
                    rightMargin: 25
                    leftMargin: -20
                }

                Text {
                    id: exportPathLocation
                    text: "<i>(default folder)</i>"
                    font.pixelSize: 14
                    font.family: primaryFont

                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.rightMargin: 10
                    anchors.leftMargin: 30

                    Component.onCompleted: { backend.setDefaultPath() }
                }
            }

            CustomBtn {
                id: getExportFolder
                width: 90

                btnName: "export to:"
                btnRadius: 0
                fontNameColor: bgColor
                fontNameSize: 13
                btncolorPressed: "#cb3535"
                btncolorMouseHover: "#db3535"
                btncolorDefault: "#e14d4d"
                activeMenuColor: "#222222"

                anchors {
                    left: parent.left
                    leftMargin: 25
                    bottom: customizationsArea.bottom
                    bottomMargin: 20

                }

                FileDialog {
                    id: folderSector
                    title: "Please choose a folder"
                    folder: shortcuts.desktop
                    selectFolder: true
                    nameFilters: ["Image File (*.jpg, *jpeg, *png)"]
                    onAccepted: {
                        backend.exportFolder(folderSector.fileUrl)

                        const badFilePath = String(folderSector.fileUrl)
                        const goodFilePath = badFilePath.slice(8, badFilePath.length)
                        exportPathLocation.text = `<i>${goodFilePath}</i>`
                    }
                    onRejected: {
                        console.log("Canceled")
                    }
                }

                onClicked: {
                    folderSector.open()
                }

            }

        }

        Rectangle {
            id: reverseOptionsArea
            width: 200
            height: 160
            color: bgColor

            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom

            Label {
                id: reversalTitle
                text: qsTr("reverse to source")

                color: accentColor
                font.family: primaryFont
                font.pointSize: 25
                font.bold: true
                wrapMode: Text.NoWrap

                anchors.right: parent.right
                anchors.bottom: sendBackToSource.top
                horizontalAlignment: Text.AlignRight
                anchors.rightMargin: 25
                anchors.bottomMargin: 30
            }

            CustomBtn {
                id: sendBackToSource
                y: 100
                width: 164
                height: 40
                btnName: "SEND BACK"
                fontNameColor: accentColor
                fontNameSize: 18

                anchors {
                    bottom: parent.bottom
                    bottomMargin: 20
                    right: parent.right
                    rightMargin: 25
                }
                onClicked: { backend.trySendFilesBack() }
            }

            CustomBtn {
                id: openExports
                y: 100
                width: 200
                height: 40
                btnName: "OPEN EXPORTS"
                fontNameColor: accentColor
                fontNameSize: 18

                anchors {
                    bottom: parent.bottom
                    bottomMargin: 20
                    right: sendBackToSource.left
                    rightMargin: 25
                }
                onClicked: { backend.openExportsFolder() }
            }

        }

    }


    Rectangle {
        id: coverRect
        color: "#80000000"
        anchors.fill: parent
        z: 100
        clip: true
        visible: window2.close() === true ? false : true
    }

    Rectangle {
        id: movingStatusBox
        color: accentColor
        radius: 25
        width: movingStatus.width + 100
        height: 80
        visible: movingStatus.text != "" ? true : false

        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter

        Label {
            id: movingStatus
            text: ""
            font.family: primaryFont
            font.pointSize: 15
            font.bold: true
            font.italic: true
            color: bgColor

            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
        }


    }

    Timer {
        id: timer
        running: false
        repeat: false

        property var callback

        onTriggered: callback()
    }

    function setTimeout(callback, delay)
    {
        if (timer.running) {
            console.error("nested calls to setTimeout are not supported!");
            return;
        }
        timer.callback = callback;
        // note: an interval of 0 is directly triggered, so add a little padding
        timer.interval = delay + 1;
        timer.running = true;
    }

    Connections {
        target: backend

        function onCurrentExport(stringy){
            exportPathLocation.text = "<i>"+stringy+"</i>"
        }
        function onSelfLogger(stringy){
            movingStatus.text = stringy
            setTimeout(removeMovingStatus, 2000)
        }
        function removeMovingStatus(){
            movingStatus.text = ""
        }
    }

}



/*##^##
Designer {
    D{i:0;formeditorZoom:1.1}
}
##^##*/
