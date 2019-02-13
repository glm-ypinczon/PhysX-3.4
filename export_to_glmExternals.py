import sys
import os
import string
import errno
import shutil
import imp
from PySide import QtGui
# pySideVer = 1
# try:
#     imp.find_module("PySide")
#     from PySide.QtCore import *
#     from PySide.QtGui import *
# except ImportError:
#     from PySide2.QtCore import *
#     from PySide2.QtGui import *
#     from PySide2.QtWidgets import *
#     pySideVer = 2

def makeDir(dir_path):
    try:
        absDir = os.path.abspath(dir_path)
        os.makedirs(absDir)
    except OSError as error:
        if error.errno == errno.EEXIST and os.path.isdir(absDir):
            pass
        else:
            raise

def doCopyFileTree(src, dst, fileExtensions, ignoreDirectories):
    filesFoundCount = list()
    for iExtension in range(0,len(fileExtensions)):
        filesFoundCount.append(0)

    for root, dirs, files in os.walk(src):
        for ignoreDir in ignoreDirectories:
            for dir in dirs:
                if(string.find(dir, ignoreDir)>=0):
                    dirs.remove(dir)
                    continue

        # create the destination dir
        dstDir = string.replace(root, src, dst)
        print("\nSource dir: {}\nDestination dir: {}").format(root, dstDir)

        for file in files:
            iExtension = 0
            for fileExtension in fileExtensions:
               if(string.find(file, fileExtension)>=0):
                   filesFoundCount[iExtension] = filesFoundCount[iExtension]+1
                   print("\n          Copying file: {}").format(file)
                   srcFile = "{}/{}".format(root, file)
                   dstFile = "{}/{}".format(dstDir, file)
                   makeDir(dstDir)
                   shutil.copy2(srcFile, dstFile)
                   break
               iExtension = iExtension+1

    msg = "\nDone. Found:"
    iExtension = 0
    for fileExtension in fileExtensions:
        msg = "{}\n -{} {} files".format(msg, filesFoundCount[iExtension], fileExtension)
        iExtension = iExtension+1
    print(msg)

def main():
    src = os.path.abspath(".")
    dst = "{}/pack".format(src)
    ignoreDirectories = {".git", ".vs", "Externals", "KaplaDemo", "Documentation", "Sample", "Snippets", "Media", "compiler", "vc11win32", "vc12win32", "vc12win64", "vc14win32"}
    fileExtensions = {".h", ".inl", ".lib", ".dll", ".pdb", ".a", ".so"}

    app = QtGui.QApplication(sys.argv)

    dialog = QtGui.QFileDialog()
    dialog.setWindowTitle("Output directory")
    dialog.setFileMode(QtGui.QFileDialog.Directory)
    dialog.setDirectory(os.path.dirname(src))
    execCode = dialog.exec_()
    if execCode == QtGui.QDialog.Accepted:
        selectedFiles = dialog.selectedFiles()
        dst = selectedFiles[0]

    doCopyFileTree(src, dst, fileExtensions, ignoreDirectories)

if __name__ == '__main__':
    main()
    exit()
