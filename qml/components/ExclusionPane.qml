import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Dialogs 1.3


Item {
    // CUSTOM PROPERTIES
    property string primaryFont: "Bahnschrift"
    property string accentColor: "#e14d4d"
    property int numExclusions: -40
    width: 420
    height: 247

    Rectangle {
        id: customSelectionPages
        color: accentColor
        anchors.fill: parent

        Rectangle {
            id: someMarginInPage
            color: "#dbdddf"

            anchors {
                fill: parent
                leftMargin: 8
                rightMargin: 8
                topMargin: 8
                bottomMargin: 8
            }

            Rectangle {
                id: rectangle
                x: 102
                y: 0
                width: 180
                height: 40
                color: "#00000000"
                anchors.top: parent.top
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.topMargin: 10

                CustomBtn {
                    id: btnReset
                    x: 197
                    y: 0
                    width: 80
                    height: 40
                    anchors.right: parent.right
                    btnName: "<i>RESET</i>"
                    btnRadius: 20
                    fontNameSize: 15
                    fontNameColor: "#e14d4d"

                    anchors.top: parent.top
                    anchors.rightMargin: 0
                    anchors.topMargin: 0

                    onPressed: {
//                        console.log(exclusionPaneScroller.contentItem.children.length)
                        for(var i = exclusionPaneScroller.contentItem.children.length ; i > 0 ; i--){
                            exclusionPaneScroller.contentItem.children[i-1].destroy()
                        };
                        numExclusions = -40
                        backend.clearListSelection("excluded")
                    }
                }

                CustomBtn {
                    QtObject {
                        id: internalCreate

                        function createBoxes() {
                            numExclusions += 40
                            const badFilePath = String(folderSector.fileUrl)
                            const goodFilePath = badFilePath.slice(8, badFilePath.length)

//                            console.log( `excPath${numExclusions}`)
                            const comm = Qt.createComponent("CustomTextField.qml")
                            const details = comm.createObject(exclusionPaneScroller.contentItem,
                                                            {
                                                                id: `excPath${numExclusions}`,
                                                                setText: goodFilePath,
                                                                marginTop: numExclusions,
                                                                wantVisible: false
                                                            });

                            if (details === null) {
                                console.log("Error Creating Object")
                            }
                        }
                    }

                    id: btnCreate
                    y: 0
                    width: 80
                    height: 40
                    anchors.left: parent.left
                    btnName: "<i>ADD</i>"
                    btnRadius: 20
                    fontNameSize: 15
                    fontNameColor: "#e14d4d"

                    anchors.top: parent.top
                    anchors.leftMargin: 0
                    anchors.topMargin: 0

                    onPressed: {
                        folderSector.open()
                    }
                }

            }

            FileDialog {
                id: folderSector
                title: "Please choose a folder"
                folder: shortcuts.desktop
                selectFolder: true
                nameFilters: ["Image File (*.jpg, *jpeg, *png)"]
                onAccepted: {
                    backend.deSelectFolder(folderSector.fileUrl)
                    internalCreate.createBoxes()
                }
                onRejected: {
                    console.log("Canceled")
                }
            }

            Flickable {
                id: exclusionPaneScroller
                interactive:true
                flickableDirection: Flickable.VerticalFlick
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: rectangle.bottom
                anchors.bottom: parent.bottom
                anchors.topMargin: 10
                clip: true
                //                contentHeight: parent.height-removebtn.height
            }

        }

    }

    Connections {
        target: backend
    }

}


