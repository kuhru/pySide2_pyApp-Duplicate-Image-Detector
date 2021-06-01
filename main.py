# This Python file uses the following encoding: utf-8
"""BACK LOGIC IMPORTS"""
import os, sys, time, traceback, shutil, webbrowser
from multiprocessing import freeze_support
from pathlib import Path
from tqdm import tqdm as tqdmBar
from PIL import Image as PILimage
from imagehash import ( phash, whash, dhash )
import concurrent.futures as ConFut
# from itertools import combinations as iterCombine

"""FRONT LOGIC IMPORTS"""
from PySide2.QtGui import QGuiApplication, QIcon
from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtCore import QObject, QRunnable, QThreadPool, Slot, Signal, QUrl


class tqdmMod(tqdmBar):
    @property
    def n(self):
        return self.__n
    
    @n.setter
    def n(self, value):
        # print(value, self.total)
        self.__n = value

    @property
    def nPerc(self):
        return (self.__n / self.total) * 100

class Worker(QRunnable):
    # https://www.mfitzp.com/tutorials/multithreading-pyside-applications-qthreadpool/
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['percProgress'] = self.signals.progressBar
        self.kwargs['logProgress'] = self.signals.progressLog

    @Slot()
    def run(self):
        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except KeyboardInterrupt as key:
            print(f"\nEnding Life Guys because {key}")
            self.stop()
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done
    
    def stop(self):
        self.autoDelete()

class WorkerSignals(QObject):
    finished = Signal()  # QtCore.Signal
    error = Signal(tuple)
    result = Signal(object)
    progressBar = Signal(int)
    progressLog = Signal(str)

class BackSideLogic():
    # class variables
    includeList = []  # filled by inclusion pane
    excludeList = []  # filled by exclusion pane
    exportHere = "" # export location for the detected duplicates
    detectedDups = []  # list of detected duplicates
    
    # internal flags
    flagP = True  # flag to run pHash
    flagW = False  # flag to run wHash
    flagD = False  # flag to run dHash
    flagMy = False  # flag to run custom hashing

    """
    flagMap = [] # is a list of all flags that are true
    dirListFinal = []  # generated later using generateFolderList()
    imgListOriginal = [] # only the list of full paths of all useful image files from all directories    
    pHashVals = []
    wHashVals = []
    dHashVals = []
    myHashVals = []
    """

    def improperExit(self):
        if self.exportHere.endswith("_Duplicate_Images"):
            for r, d, f in os.walk(self.exportHere):
                # print("length of files in {} is {}. Hence deleting and stopping program.".format(self.exportHere, len(f)))
                if len(f) == 0 and len(d) == 0:
                    os.rmdir(self.exportHere)
                    return "Export folder deleted since empty."
                break
            return "Export folder not empty, so preserved"
        return "User's personal export folder, so preserved"

    def whatHashes(self):
        allFlags = (self.flagP, self.flagW, self.flagD, self.flagMy)
        chosenFlags = []
        for ind, ele in enumerate(allFlags):
            if ele is True:
                if ind == 0:
                    chosenFlags.append("pHash")
                elif ind == 1:
                    chosenFlags.append("wHash")
                elif ind == 2:
                    chosenFlags.append("dHash")
                elif ind == 3:
                    chosenFlags.append("myHash")
        if len(chosenFlags) <= 0:
            return chosenFlags.append("pHash")
        return chosenFlags

    def generateFolderList(self, incList, excList, getPerc):
        outListOfDirs = []
        print("Optimizing Folders List")
        with tqdmMod(total = len(incList)) as pBar:
            for locs in incList:
                for r, d, f in os.walk(locs):
                    if r not in outListOfDirs:
                        if True in [r.startswith(escapeThese) for escapeThese in excList]:
                            continue
                        if any(file.endswith((".jpg", ".jpeg", ".png", ".gif")) for file in f):
                            outListOfDirs.append(r)
                pBar.update(1)
                getPerc.emit(int(pBar.nPerc))
        return outListOfDirs

    def getImages(self, listOfDirs, getPerc):
        outListOfImgs = []
        print("Getting Image Files")
        with tqdmMod(total = len(listOfDirs)) as pBar:
            for roots in listOfDirs:
                for root, directories, files in os.walk(roots):
                    currentListOfImgs = [os.path.join(root, file) for file in files if file.endswith((".jpg", ".jpeg", ".png", ".gif"))]
                    outListOfImgs.extend(currentListOfImgs)
                    time.sleep(0.1)
                    pBar.update(1)
                    getPerc.emit(int(pBar.nPerc))
                    break
                # if len(outListOfImgs) > 100:
                #     return outListOfImgs
        return outListOfImgs

    def makeHashLists(self, flagList, listOfImgs, getPerc, getLog):
        if "pHash" in flagList:
            getLog.emit("\n   Running pHash")
            self.pHashVals = self.runHashingMP(self.pHashIt, listOfImgs, getPerc)
            self.pHashVals.sort()
        if "wHash" in flagList:
            getLog.emit("\n   Running wHash")
            self.wHashVals = self.runHashingMP(self.wHashIt, listOfImgs, getPerc)
            self.wHashVals.sort()
        if "dHash" in flagList:
            getLog.emit("\n   Running dHash")
            self.dHashVals = self.runHashingMP(self.dHashIt, listOfImgs, getPerc)
            self.dHashVals.sort()
        if "myHash" in flagList:
            # self.myHashVals = self.runHashingMP(self.pHashIt, listOfImgs)
            pass

    def runHashingMP(self, hashingFunc, listOfImgs, getPerc):
        outSomething = []
        with tqdmMod(total=len(listOfImgs)) as pBar:
            with ConFut.ProcessPoolExecutor(max_workers = os.cpu_count() - 2) as executor:
                futures = {executor.submit(hashingFunc, arg): arg for arg in listOfImgs}
                for future in ConFut.as_completed(futures):
                    outSomething.append(future.result())
                    pBar.update(1)
                    getPerc.emit(int(pBar.nPerc))
        return outSomething

    def pHashIt(self, singleImgFile):
        currentImg = PILimage.open(singleImgFile)
        doPHash = phash(currentImg) #, hash_size=8
        currentImg.close()
        return [str(doPHash), singleImgFile]

    def wHashIt(self, singleImgFile):
        currentImg = PILimage.open(singleImgFile)
        doWHash = whash(currentImg) #, hash_size=8
        currentImg.close()
        return [str(doWHash), singleImgFile]

    def dHashIt(self, singleImgFile):
        currentImg = PILimage.open(singleImgFile)
        doDHash = dhash(currentImg) #, hash_size=8
        currentImg.close()
        return [str(doDHash), singleImgFile]

    def myHashIt(self, singleImgFile):
        pass

    def convertHex2Bin(self, hexVal):
        binNumArr = []
        num = int(hexVal, 16)
        binNum = str(bin(num))[2:].zfill(64)
        for i in range(64):
            binNumArr.append(binNum[i])
        return binNumArr

    def getHammingDistance(self, item1, item2):
        hamm = 0
        for i in range(64):
            if item1[i] != item2[i]:
                hamm += 1
        hammD = hamm / 64
        return hammD

    def runDetector(self, flagList, thresHold, getPerc, getLog):
        print("Running Duplicates Check")
        if "pHash" in flagList:
            getLog.emit("\n   Going through pHash")
            new = self.getDuplicates(self.pHashVals, thresHold, getPerc)
            self.detectedDups.extend(new)
        if "wHash" in flagList:
            getLog.emit("\n   Going through wHash")
            self.detectedDups.extend(self.getDuplicates(self.wHashVals, thresHold, getPerc))
        if "dHash" in flagList:
            getLog.emit("\n   Going through dHash")
            self.detectedDups.extend(self.getDuplicates(self.dHashVals, thresHold, getPerc))

    def getDuplicates(self, listOfHashes, threshHold, getPerc):
        duplicates = []
        lenHashes = len(listOfHashes)
        totCycles = round((lenHashes*(lenHashes-1))/2)

        with tqdmMod(total = lenHashes) as pBar:
            for i in range(lenHashes):
                for j in range(i+1, lenHashes):
                    itm1 = list(self.convertHex2Bin(listOfHashes[i][0]))
                    itm2 = list(self.convertHex2Bin(listOfHashes[j][0]))
                    hammD = self.getHammingDistance(itm1, itm2)

                    if hammD <= threshHold:
                        if listOfHashes[i][1] not in duplicates:
                            duplicates.append(listOfHashes[i][1])
                        if listOfHashes[j][1] not in duplicates:
                            duplicates.append(listOfHashes[j][1])
                        
                pBar.update(1)
                getPerc.emit(int(pBar.nPerc))
        return duplicates

    def getDuplicates2(self, listOfHashes, threshHold, getPerc):
        duplicates = []
        # lim = 10000000
        # with tqdmMod(total = lim / 100000) as pBar:
        #     for i in range(lim):
        #         if i % 100000 == 0:
        #             pBar.update(1)
        #             getPerc.emit(int(pBar.nPerc))
        return duplicates

    def sendForwardToExport(self, exptLoc, listOfDups, getLog):
        print("Moving Files...")

        if os.path.isdir(exptLoc) == False: return "Not a Folder"
        totalFiles = len(listOfDups)
        unMoved = []

        while len(listOfDups) != 0:
            currentFilePath = listOfDups.pop()

            cfpBaseName = os.path.basename(currentFilePath)
            cfpLocation = os.path.dirname(currentFilePath).replace("\\", "!@!").replace(":", ",,,").replace("/", "!@!")
            cfpBaseNameNoExt =  os.path.splitext(cfpBaseName)[0]
            cfpBaseNameOnlyExt = os.path.splitext(cfpBaseName)[1]

            newFileName = f"{cfpBaseNameNoExt} (!({cfpLocation})!){cfpBaseNameOnlyExt}"
            newFilePath = os.path.join(exptLoc, newFileName)

            try:
                shutil.move(currentFilePath, newFilePath)
            except Exception as e:
                print(e)
                # print(f"{currentFilePath}\n{newFilePath}")
                info = f"\n   Failed to Move: {currentFilePath} to\n   {newFilePath}"
                getLog.emit(info)
                unMoved.append(currentFilePath)
            else:
                None
        
        return f"Moved {totalFiles - len(unMoved)} of {totalFiles} files"

    def sendBackToSource(self, exptLoc, getLog):
        print("Sending Back to Source...")
        if os.path.isdir(exptLoc) == False: return "Not a Folder"
        
        allFiles = [f for r, d, f in os.walk(exptLoc)][0]
        totalFiles = len(allFiles)
        unMoved = []

        while len(allFiles) != 0:
            currentFileName = allFiles.pop()
            currentFilePath = os.path.join(exptLoc, currentFileName)
            try:
                newLocStartInd = currentFileName.index(" (!(")
                newLocEndInd = currentFileName.index(")!).")

                cfpBaseNameNoExt = currentFileName[:newLocStartInd]
                cfpBaseNameOnlyExt = "."+currentFileName.split(".")[-1]

                newFileName = cfpBaseNameNoExt + cfpBaseNameOnlyExt
                newLocName = currentFileName[newLocStartInd + 4:newLocEndInd].replace("!@!", "\\").replace(",,,", ":")
                newFilePath = os.path.join(newLocName, newFileName)
                shutil.move(currentFilePath, newFilePath)
            except:
                info = f"\n Failed to move: '{newFileName}' to\n\t '{newLocName}'"
                getLog.emit(info)
                unMoved.append(currentFileName)
            else:
                None
        
        return f"Moved {totalFiles - len(unMoved)} of {totalFiles}"

    # let the application windows set up
    # check if inputs are valid
    # generate the folders list
    # check if the export location exists
    # make hashes of images
    # start hamming distance comparison
    # move files to new destination

    def codeRunnerGui(self, percProgress, logProgress):
        # let the application process window manipulation
        time.sleep(0.5)

        # check whether any folder has been included
        logProgress.emit("> Checking Inclusion & Exclusion Paths")
        if len(self.includeList) == 0:
            logProgress.emit(f"\nERROR: Include folder's List can't be empty\n   Click on 'ADD' in main window and add a folder with images.")
            return "Exiting Application"

        # remove obvious redundancies in the lists
        self.excludeList.append(self.exportHere) # just for removing confusion
        # self.includeList = set(self.includeList) # removing duplicates
        # self.excludeList = set(self.excludeList) # same ^

        time.sleep(0.5)

        # check whether any also has been selected
        self.flagMap = self.whatHashes()
        if len(self.flagMap) == 0:
            logProgress.emit("\n No Flags Set")
            return "Exiting Application: No Flags Set"
        info = ", ".join(self.flagMap)
        logProgress.emit(f"\n   {info} chosen")

        time.sleep(0.5)

        # make a list of actually useful folders for the purpose of this application
        logProgress.emit(f"\n> Optimizing Folders List")
        self.dirListFinal = self.generateFolderList(self.includeList, self.excludeList, percProgress)
        if len(self.dirListFinal) == 0:
            logProgress.emit(f"\nNo Usable Folders Found in Mentioned Lists\n{info}")
            return "Exiting Application: No folders were found selectable"

        time.sleep(0.5)

        # make a list of all the image files in the gathered folders
        logProgress.emit(f"\n> Gathering Image Files")
        self.imgListOriginal = self.getImages(self.dirListFinal, percProgress)
        if len(self.imgListOriginal) == 0:
            logProgress.emit(f"\nNo Usable Images Found in Mentioned Directories\n{info}")
            return "Exiting Application: No image found in specified folders"

        time.sleep(0.5)

        # Validate the existance of Export folder
        logProgress.emit("\n> Checking Export Folder")
        if os.path.isdir(self.exportHere) == False:
            logProgress.emit(f"\n   '{self.exportHere}' doesn't exist.\nTrying to create folder")
            try:
                os.mkdir(self.exportHere)
            except Exception as e:
                info = self.improperExit()
                logProgress.emit(f"\nERROR: {e}\n{info}")
                return "Exiting Application: Where did you run this, you unpriviledged idiot"
        # elif len(os.listdir(self.exportHere)) !=0:
        #     info = self.improperExit()
        #     logProgress.emit(f"\nERROR: '{self.exportHere}' is not empty.\n   If you think the folder is truly empty, try deleting the folder and running this again\n{info}")
        #     return "Exiting Application"
        
        time.sleep(0.5)

        # hashing all the detected images based on whatever selected hash is
        logProgress.emit(f"\n> Hashing")
        self.makeHashLists(self.flagMap, self.imgListOriginal, percProgress, logProgress)

        time.sleep(0.5)

        # comparing the hamming distance for all the files
        logProgress.emit(f"\n> Comparing Hamming Distances")
        self.runDetector(self.flagMap, 0.16, percProgress, logProgress)

        time.sleep(0.5)

        # show the detected number of duplicates
        if len(self.detectedDups) == 0:
            logProgress.emit("\n> No Duplicated Detected")
            return "Exiting Application: No Duplicates Found"
        logProgress.emit(f"\n> Duplicated Detected: {len(self.detectedDups)}")

        time.sleep(0.5)

        # moving the duplicates to the export folder
        logProgress.emit(f"\n> Moving Detected Duplicates")
        self.sendForwardToExport(self.exportHere, self.detectedDups, logProgress)

        logProgress.emit("\n> Successful")
        return "Successfully Completed"

    def codeRunner(self, progress_callback):
        # since moving files to and from the export folder would cause issues
        # if self.exportHere == "":
        #     try:
        #         self.exportHere = os.path.join(os.getcwd(), "_Duplicate_Images")
        #         os.mkdir(self.exportHere)
        #     except Exception as e:
        #         print(e)
        #         print(self.improperExit())
        #         return "Exiting Application: Where did you run this, you unpriviledged idiot"

        # # for ease, the export folder is also not allowed to be a folder of searching
        # self.excludeList.append(self.exportHere)
        # # making the lists into sets to remove any easy duplicates
        # self.includeList = set(self.includeList)
        # self.excludeList = set(self.excludeList)
        # # making a dictionary of hashes to be performed
        # self.flagMap = self.whatHashes()
        # print(self.flagMap)


        # # if either of the lists is empty then we can't proceed.
        # if None in (self.includeList, self.excludeList, self.flagMap):
        #     print(self.improperExit())
        #     return "Exiting Application: Either include, exclude or hasher not given"
        # # else a proper list of directories is generated
        # self.dirListFinal = self.generateFolderList(self.includeList, self.excludeList)


        # # if no usable list of directories is found
        # if self.dirListFinal == None:
        #     print(self.improperExit())
        #     return "Exiting Application: No folders were found selectable"
        # # else a proper list of images with full path is generated
        # self.imgListOriginal = self.getImages(self.dirListFinal)


        # # if no usable list of images is found
        # if self.imgListOriginal == None:
        #     print(self.improperExit())
        #     return "Exiting Application: No image found in specified folders"
        # # else run hashes on the images
        # self.makeHashLists(self.flagMap, self.imgListOriginal)


        # # check for duplicates
        # self.runDetector(self.flagMap, 0.16)

        # print("Total Duplicates found: {}".format(len(self.detectedDups)))
        # print(self.detectedDups)

        # just in case, if this folder turns out to be useless
        # return self.improperExit()
        return "Ran"

class MainWindow(QObject):
    def __init__(self):
        QObject.__init__(self)
        self.data = BackSideLogic() # object of the backside class containing all data and functions
        self.threadpool = QThreadPool() # object of the threadpool to make GUI not freeze during processing

    # signals for application
    currentExport = Signal(str) # is emitted by default when no 
    currentProgressPerc = Signal(int) # carries the current progress % from worker threads as well
    currentProgressLog = Signal(str) # carries the console output logs from worker threads as well
    selfLogger = Signal(str)  # throws emit for the bonus functionality like revert to original location and open export folder

    # functions for the application
    @Slot()
    def setDefaultPath(self):
        self.data.exportHere = os.path.join(os.getcwd(), "_Duplicate_Images")  # default export location for the detected duplicates
        self.currentExport.emit(self.data.exportHere)

    @Slot(str)
    def changeAlgo(self, checkThis):
        """
        for raising flags as in what algo the main application is running
        this can run all algos, for the correct set of flags.
        @parameter: @checkThis: an algo name, comes from the switches in the application
        """
        print(checkThis)
        if checkThis == "pHash":
            self.data.flagP = not self.data.flagP
        elif checkThis == "wHash":
            self.data.flagW = not self.data.flagW
        elif checkThis == "dHash":
            self.data.flagD = not self.data.flagD
        elif checkThis == "myHash":
            self.data.flagMy = not self.data.flagMy
        print("{} {} {} {}".format(self.data.flagP, self.data.flagW, self.data.flagD, self.data.flagMy))

    @Slot(str)
    def selectFolder(self, filepath):
        newLocation = QUrl(filepath).toLocalFile()
        self.data.includeList.append(newLocation)
        print(self.data.includeList)

    @Slot(str)
    def deSelectFolder(self, filepath):
        newLocation = QUrl(filepath).toLocalFile()
        self.data.excludeList.append(newLocation)
        print(self.data.excludeList)

    @Slot(str)
    def exportFolder(self, filepath):
        newLocation = QUrl(filepath).toLocalFile()
        self.data.exportHere = newLocation

    @Slot(str)
    def clearListSelection(self, flag):
        if flag == "excluded":
            self.data.excludeList.clear()
        elif flag == "included":
            self.data.includeList.clear()
        pass

    @Slot()
    def openExportsFolder(self):
        if os.path.isdir(self.data.exportHere) == False:
            self.forSelfLogger("Folder Doesn't Exist, Opening Parent...")
            try:
                os.mkdir(self.data.exportHere)
            except Exception as e:
                print(f"\nERROR: {e}")
                self.forSelfLogger("Could Not Create Folder")
                return "Exiting Application: Where did you run this, you unpriviledged idiot"
        self.forSelfLogger("Opening Export Folder Now")
        webbrowser.open(os.path.realpath(self.data.exportHere))
        pass

    @Slot()
    def trySendFilesBack(self):
        if os.path.isdir(self.data.exportHere) == False:
            self.forSelfLogger("Export Folder Doesn't Exist")
            return print("Folder Doesn't Exist")
        allFiles = [f for r, d, f in os.walk(self.data.exportHere)][0]
        totalFiles = len(allFiles)
        if totalFiles == 0:
            self.forSelfLogger("No Usable Files Found")
            return print("No usable files found")

        unMoved = []
        while len(allFiles) != 0:
            currentFileName = allFiles.pop()
            currentFilePath = os.path.join(self.data.exportHere, currentFileName)
            try:
                newLocStartInd = currentFileName.index(" (!(")
                newLocEndInd = currentFileName.index(")!).")

                cfpBaseNameNoExt = currentFileName[:newLocStartInd]
                cfpBaseNameOnlyExt = "."+currentFileName.split(".")[-1]

                newFileName = cfpBaseNameNoExt + cfpBaseNameOnlyExt
                newLocName = currentFileName[newLocStartInd + 4:newLocEndInd].replace("!@!", "\\").replace(",,,", ":")
                newFilePath = os.path.join(newLocName, newFileName)
                shutil.move(currentFilePath, newFilePath)
            except:
                info = f"\n Failed to move: '{newFileName}' to\n\t '{newLocName}'"
                print(info)
                unMoved.append(currentFileName)
            else:
                None

        if len(unMoved) == 0:
            self.forSelfLogger("Moved All Files")
            return
        info = f"Moved {totalFiles - len(unMoved)} of {totalFiles}"
        self.forSelfLogger(info)
        return info

    @Slot()
    def ensureExit(self):
        self.data.improperExit()

    @Slot()
    def startRunning(self):
        self.data.codeRunnerGui(self.currentProgressPerc, self.currentProgressLog)
        # self.worker = Worker(self.data.codeRunnerGui)

        # self.worker.signals.progressBar.connect(self.newCurrentProgressPerc)
        # self.worker.signals.progressLog.connect(self.newCurrentProgressMessage)
        # self.worker.signals.result.connect(self.functionReturnMessage)
        # self.worker.signals.finished.connect(self.whenTaskComplete)

        # self.threadpool.start(self.worker)
        pass

    @Slot()
    def stopRunning(self):
        app.deleteLater()

        # self.threadpool.clear()
        # self.threadpool.waitForDone(1)
        # self.threadpool.cancel(self.worker)
        # self.threadpool.releaseThread()
        # self.worker.stop()
        # sys.exit()
        
        # sys.exit(app)
        pass

    def forSelfLogger(self, infoString):
        self.selfLogger.emit(infoString)
        print(infoString)

    def newCurrentProgressPerc(self, percentage):
        self.currentProgressPerc.emit(percentage)

    def newCurrentProgressMessage(self, text):
        print(text)
        self.currentProgressLog.emit(text)

    def functionReturnMessage(self, functionReturn):
        print(functionReturn)

    def whenTaskComplete(self):
        print("Completed")

if __name__ == "__main__":
    freeze_support()
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    main = MainWindow()

    app.setOrganizationName("Kuhru")
    app.setOrganizationDomain("N/A")
    app.setWindowIcon(QIcon(os.fspath(Path(__file__).resolve().parent / "icon2.ico")))

    engine.rootContext().setContextProperty("backend", main)
    engine.load(os.fspath(Path(__file__).resolve().parent / "qml/main.qml"))

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec_())
