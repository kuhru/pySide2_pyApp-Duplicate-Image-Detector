# This Python file uses the following encoding: utf-8
"""BACK LOGIC IMPORTS"""
import os, sys, time, traceback, shutil, webbrowser
from multiprocessing import freeze_support
from pathlib import Path
from tqdm import tqdm as tqdmBar
from PIL import Image as PILimage
from imagehash import ( phash, whash, dhash )
import concurrent.futures as ConFut

"""FRONT GUI IMPORTS"""
from PySide2.QtGui import QGuiApplication, QIcon
from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtCore import QObject, QRunnable, QThreadPool, Slot, Signal, QUrl


class tqdmMod(tqdmBar):
    """
    ABOUT:  This class inherits tqdm.tqdm essentially to create a function that can return the
            current progress percent. All other things are essentially same.
    """
    @property
    def n(self):
        return self.__n
    
    @n.setter
    def n(self, value):
        # print(value, self.total)
        self.__n = value

    @property
    def nPerc(self):
        """this is the important function that was not present in the original tqdm.tqdm class."""
        return (self.__n / self.total) * 100

class Worker(QRunnable):
    # https://www.mfitzp.com/tutorials/multithreading-pyside-applications-qthreadpool/
    """
    ABOUT:  This class exists to inherit QRunnable, which essentially helps PySide2 GUI run any
            functions in the background and let the application run free without hanging in the
            main thread.
    """
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
    """
    ABOUT:  This class exists to inherit QObject just to create signals for the Worker Class above
            because a QRunnable Class cannot facilitate creation of these.
    """
    finished = Signal()  # Throw this signal when the thread function is finished.
    error = Signal(tuple)  # Throw the tuple of error tracebacks if the function raises any exceptions.
    result = Signal(object)  # Throws the return of the threaded function.
    progressBar = Signal(int)  # Throws the current completion percentage for progressbar in front end.
    progressLog = Signal(str)  # Throws any information to indicate the progress of background background process.

class BackSideLogic():
    """
    ABOUT:  This is the class that carries all the data and members for the main logic of
            finding duplicates.
    """
    # class variables
    includeList = []  # filled by inclusion pane
    excludeList = []  # filled by exclusion pane
    exportHere = "" # export location for the detected duplicates

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
    detectedDups = []  # list of detected duplicates
    """

    def improperExit(self):
        """
        ABOUT:  If the Runner is stopped then this deletes the unnecessary duplicate
                collector folder

        PARAMETER:  None

        RETURN: strings about nature of export folder
        """
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
        """
        ABOUT:  Creates a tuple of strings of all the hashes set to true

        PARAMETER:  None

        RETURN: list of all selected hashes
        """
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
        """
        ABOUT:  Generates a list of folders from the include and exclude lists, just all
                the folders and sub folders that are required for searching

        PARAMETER:  incList:    list of folders to include
                    excList:    list of folders to exclude
                    getPerc:    signal for current percentage for front end GUI

        RETURN: a list of all directories and sub-directories that contain any image.
        """
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
        """
        ABOUT:  Gets a list of all images from all the folders generated from proper folder
                list

        PARAMETER:  listOfDirs: list of all relevant directories
                    getPerc:    signal for current percentage for front end GUI

        RETURN: list of all detected images
        """
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
        """
        ABOUT:  Runs the hashing function for all hashes selected

        PARAMETER:  flagList:   list of all selected hashes
                    listOfImgs: list of all detected images
                    getPerc:    signal for current percentage for front end GUI
                    getLog:     signal for general information for front end GUI

        RETURN: None
        """
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
        """
        ABOUT:  Uses multiprocessing on the images list and executes hashing on images

        PARAMETER:  hashingFunc:    the called hashing funciton
                    listOfImgs:     list of all detected images
                    getPerc:        signal for current percentage for front end GUI

        RETURN: list of list of [hashes of single image, location of single image]
        """
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
        """
        ABOUT:  Uses pHash from imagehash

        PARAMETER:  singleImgFile:  image location of a single image

        RETURN: list of pHash and singleImgFile
        """
        currentImg = PILimage.open(singleImgFile)
        doPHash = phash(currentImg) #, hash_size=8
        currentImg.close()
        return [str(doPHash), singleImgFile]

    def wHashIt(self, singleImgFile):
        """
        ABOUT:  Uses wHash from imagehash

        PARAMETER:  singleImgFile:  image location of a single image

        RETURN: list of wHash and singleImgFile
        """
        currentImg = PILimage.open(singleImgFile)
        doWHash = whash(currentImg) #, hash_size=8
        currentImg.close()
        return [str(doWHash), singleImgFile]

    def dHashIt(self, singleImgFile):
        """
        ABOUT:  Uses dHash from imagehash

        PARAMETER:  singleImgFile:  image location of a single image

        RETURN: list of dHash and singleImgFile
        """
        currentImg = PILimage.open(singleImgFile)
        doDHash = dhash(currentImg) #, hash_size=8
        currentImg.close()
        return [str(doDHash), singleImgFile]

    def myHashIt(self, singleImgFile):
        pass

    def convertHex2Bin(self, hexVal):
        """
        ABOUT:  Since all the hashes are returned as 16Bit hexadecimal, they are changed
                to 64bit binaries

        PARAMETER:  hexVal: a hexadecimal 16bit string

        RETURN: 64bit binary number representation of hexVal
        """
        binNumArr = []
        num = int(hexVal, 16)
        binNum = str(bin(num))[2:].zfill(64)
        for i in range(64):
            binNumArr.append(binNum[i])
        return binNumArr

    def getHammingDistance(self, item1, item2):
        """
        ABOUT:  Gets hamming distance between two 64bit binaries

        PARAMETER:  item1:  a 64bit value
                    item2:  another 64bit value

        RETURN: hamming distance between item1 and item2
        """
        hamm = 0
        for i in range(64):
            if item1[i] != item2[i]:
                hamm += 1
        hammD = hamm / 64
        return hammD

    def runDetector(self, flagList, thresHold, getPerc, getLog):
        """
        ABOUT:  Calls the getDuplicate for all hashes that are selected

        PARAMETER:  flagList:   list of all selected hashes
                    thresHold:  the hamming distance threshold in percentage
                    getPerc:    signal for current percentage for front end GUI
                    getLog:     signal for general information for front end GUI

        RETURN: extended list of duplicates for all selected hashes
        """
        listOfDups = []
        print("Running Duplicates Check")
        if "pHash" in flagList:
            getLog.emit("\n   Going through pHash")
            listOfDups.extend(self.getDuplicates(self.pHashVals, thresHold, getPerc))
        if "wHash" in flagList:
            getLog.emit("\n   Going through wHash")
            listOfDups.extend(self.getDuplicates(self.wHashVals, thresHold, getPerc))
        if "dHash" in flagList:
            getLog.emit("\n   Going through dHash")
            listOfDups.extend(self.getDuplicates(self.dHashVals, thresHold, getPerc))
        return listOfDups

    def getDuplicates(self, listOfHashes, threshHold, getPerc):
        """
        ABOUT:  Compares all combinations of 2 of hashes, without repetitions

        PARAMETER:  listOfHashes:   a list of hashes, hash specific
                    threshHold:     the hamming distance threshold in percentage
                    getPerc:        signal for current percentage for front end GUI

        RETURN: list of duplicates for a specific hash type
        """
        duplicates = []
        lenHashes = len(listOfHashes)
        # totCycles = round((lenHashes*(lenHashes-1))/2)

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

    def sendForwardToExport(self, exptLoc, listOfDups, getLog):
        """
        ABOUT:  Changes file names
                from   > C:/Users/nmkzn/Desktop/welop/pix/89148536_p0.png
                to     > C:/Users/nmkzn/Desktop/welop/extra/89148536_p0 (!(C,,,!@!Users!@!nmkzn!@!Desktop!@!welop!@!pix)!).png
                as in  > (og path - og name) to (new path - og name - morphed og path)
                and moves the files to the export folder. Cut, not copy.

        PARAMETER:  exptLoc:    Export location
                    listOfDups: List of all duplicates
                    getLog:     For logging information to GUI

        RETURN: string about how many files moved
        """
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
        """
        ABOUT:  Changes files names
                from    > C:/Users/nmkzn/Desktop/welop/extra/89148536_p0 (!(C,,,!@!Users!@!nmkzn!@!Desktop!@!welop!@!pix)!).png
                to      > C:/Users/nmkzn/Desktop/welop/pix/89148536_p0.png
                as in   > (new path - og name - morphed og path) to (og path - og name)
                and moves files from export location to the original source.

        PARAMETER:  exptLoc:    Export location
                    getLog:     For logging information to GUI

        RETURN: string about how many files moved
        """
        print("Sending Back to Source...")
        if os.path.isdir(exptLoc) == False: return "Not a Folder"

        allFiles = [f for r, d, f in os.walk(exptLoc)][0]
        totalFiles = len(allFiles)
        unMoved = []

        while len(allFiles) != 0:
            currentFileName = allFiles.pop()
            currentFilePath = os.path.join(exptLoc, currentFileName)
            try:
                currentFileName = " ".join(currentFileName.split(" ")[1:])
                newLocStartInd = currentFileName.index(" (!(")
                newLocEndInd = currentFileName.index(")!).")

                cfpBaseNameNoExt = currentFileName[:newLocStartInd]
                cfpBaseNameOnlyExt = "."+currentFileName.split(".")[-1]

                newFileName = cfpBaseNameNoExt + cfpBaseNameOnlyExt
                newLocName = currentFileName[newLocStartInd + 4:newLocEndInd].replace("!@!", "\\").replace(",,,", ":")

                newFilePath = os.path.join(newLocName, newFileName)
                shutil.move(currentFilePath, newFilePath)
            except:
                info = f"\n   Failed to move: '{currentFilePath}'"
                getLog.emit(info)
                unMoved.append(currentFileName)
                traceback.print_exc()
                exctype, value = sys.exc_info()[:2]
                print((exctype, value, traceback.format_exc()), "\n")
            else:
                None
        
        return f"Moved {totalFiles - len(unMoved)} of {totalFiles}"

    def codeRunnerGui(self, percProgress, logProgress):
        """
        ABOUT:  1. let the application windows set up
                2. check if inputs are valid
                3. generate the folders list
                4. check if the export location exists
                5. make hashes of images
                6. start hamming distance comparison
                7. move files to new destination
        
        PARAMETER:  percProgress:   connects backend progress percentage to front end
                    logProgress:    connects backend progress information to front end
        RETURN: None
        """
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
        
        time.sleep(0.5)

        # hashing all the detected images based on whatever selected hash is
        logProgress.emit(f"\n> Hashing")
        self.makeHashLists(self.flagMap, self.imgListOriginal, percProgress, logProgress)

        time.sleep(0.5)

        # comparing the hamming distance for all the files
        logProgress.emit(f"\n> Comparing Hamming Distances")
        self.detectedDups = self.runDetector(self.flagMap, 0.16, percProgress, logProgress)

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

class MainWindow(QObject):
    def __init__(self):
        QObject.__init__(self)
        self.data = BackSideLogic()  # object of the backside class containing all data and functions
        self.threadpool = QThreadPool()  # object of the threadpool to make GUI not freeze during processing

    # signals for application
    currentExport = Signal(str)  # is emitted by default when launching the application
    currentProgressPerc = Signal(int)  # carries the current progress % from worker threads as well
    currentProgressLog = Signal(str)  # carries the console output logs from worker threads as well
    selfLogger = Signal(str)  # throws emit for the bonus functionality like revert to original location and open export folder

    # functions for the application
    @Slot()
    def setDefaultPath(self):
        """
        ABOUT:  sets the export folder path by default upon launching of the application"""
        self.data.exportHere = os.path.join(os.getcwd(), "_Duplicate_Images")  # default export location for the detected duplicates
        self.currentExport.emit(self.data.exportHere)

    @Slot(str)
    def changeAlgo(self, checkThis):
        """
        ABOUT:  for raising flags as in what algo the main application is running this
                can run all algos, for the correct set of flags.

        PARAMETER:  checkThis:  an algo name, comes from the switches in the application

        RETURN: None
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
        """
        ABOUT:  When an include folder is selected in front end, it gets logged in the backend

        PARAMETER:  filepath:   the path of the folder to be included

        RETURN: None
        """
        newLocation = QUrl(filepath).toLocalFile()
        self.data.includeList.append(newLocation)
        print(self.data.includeList)

    @Slot(str)
    def deSelectFolder(self, filepath):
        """
        ABOUT:  When an exclude folder is selected in front end, it gets logged in the backend

        PARAMETER:  filepath:   the path of the folder to be excluded

        RETURN: None
        """
        newLocation = QUrl(filepath).toLocalFile()
        self.data.excludeList.append(newLocation)
        print(self.data.excludeList)

    @Slot(str)
    def exportFolder(self, filepath):
        """
        ABOUT:  When the export folder is changed in the front end, it gets logged in the backend

        PARAMETER:  filepath:   the path of the folder to be export folder

        RETURN: None
        """
        newLocation = QUrl(filepath).toLocalFile()
        self.data.exportHere = newLocation

    @Slot(str)
    def clearListSelection(self, flag):
        """
        ABOUT:  Empties the include or exclude folders list in backend

        PARAMETER:  flag:   which folders list to empty

        RETURN: None
        """
        if flag == "excluded":
            self.data.excludeList.clear()
        elif flag == "included":
            self.data.includeList.clear()

    @Slot()
    def openExportsFolder(self):
        """
        ABOUT:  Opens the current export folder in file explorer
        """
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

    @Slot()
    def trySendFilesBack(self):
        """
        ABOUT:  Sends files back to the source from the export folder

        RETURN: string about how many files moved
        """
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
                # currentFileName = " ".join(currentFileName.split(" ")[1:])
                newLocStartInd = currentFileName.index(" (!(")
                newLocEndInd = currentFileName.index(")!).")

                cfpBaseNameNoExt = currentFileName[:newLocStartInd]
                cfpBaseNameOnlyExt = "."+currentFileName.split(".")[-1]

                newFileName = cfpBaseNameNoExt + cfpBaseNameOnlyExt
                newLocName = currentFileName[newLocStartInd + 4:newLocEndInd].replace("!@!", "\\").replace(",,,", ":")

                newFilePath = os.path.join(newLocName, newFileName)
                shutil.move(currentFilePath, newFilePath)
            except:
                info = f"\n Failed to move: '{currentFilePath}'"
                print(info)
                unMoved.append(currentFileName)
                traceback.print_exc()
                exctype, value = sys.exc_info()[:2]
                print((exctype, value, traceback.format_exc()), "\n")
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
        """
        ABOUT:  just for calling a backend function.
        """
        self.data.improperExit()

    @Slot()
    def startRunning(self):
        """
        ABOUT:  creates a new thread and worker instance, and runs the backend logic on it
                so that the main application window doesn't freeze
        """
        # self.data.codeRunnerGui(self.currentProgressPerc, self.currentProgressLog)
        self.worker = Worker(self.data.codeRunnerGui)

        self.worker.signals.progressBar.connect(self.newCurrentProgressPerc)
        self.worker.signals.progressLog.connect(self.newCurrentProgressMessage)
        self.worker.signals.result.connect(self.functionReturnMessage)
        self.worker.signals.finished.connect(self.whenTaskComplete)

        self.threadpool.start(self.worker)

    @Slot()
    def stopRunning(self):
        """
        ABOUT:  stop the backend function from running and end the application
        """
        app.deleteLater()

        # self.threadpool.clear()
        # self.threadpool.waitForDone(1)
        # self.threadpool.cancel(self.worker)
        # self.threadpool.releaseThread()
        # self.worker.stop()
        # sys.exit()
        
        # sys.exit(app)

    def forSelfLogger(self, infoString):
        """
        ABOUT:  prints a string on the front end GUI from the main GUI thread

        PARAMETER:  infoString: the string to be printed

        RETURN: None
        """
        self.selfLogger.emit(infoString)
        print(infoString)

    def newCurrentProgressPerc(self, percentage):
        """
        ABOUT:  prints the percentage value on the front end GUI from the worker thread

        PARAMETER:  percentage: the current progressbar percentage value of worker thread

        RETURN: None
        """
        self.currentProgressPerc.emit(percentage)

    def newCurrentProgressMessage(self, text):
        """
        ABOUT:  prints the information string on the front end GUI from the worker thread

        PARAMETER:  text:   information about progress about the worker thread

        RETURN: None
        """
        print(text)
        self.currentProgressLog.emit(text)

    def functionReturnMessage(self, functionReturn):
        """
        ABOUT:  prints the worker thread's return

        PARAMETER:  functionReturn: the returned value of the worker thread

        RETURN: None
        """
        print(functionReturn)

    def whenTaskComplete(self):
        """
        ABOUT:  Just a placeholder function
        """
        print("Completed")

if __name__ == "__main__":
    freeze_support()
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    main = MainWindow()

    app.setOrganizationName("Kuhru")
    app.setOrganizationDomain("KuhruNOINC")
    app.setWindowIcon(QIcon(os.fspath(Path(__file__).resolve().parent / "icon2.ico")))

    engine.rootContext().setContextProperty("backend", main)
    engine.load(os.fspath(Path(__file__).resolve().parent / "qml/main.qml"))

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec_())
