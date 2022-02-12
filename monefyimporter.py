# This Python file uses the following encoding: utf-8
import sys
import csv
import time

from phoneInterface import phoneInterface

# This Python QT things
from PyQt5.QtWidgets import QApplication, QWidget, QDialog, QFileDialog, QMessageBox
from PyQt5.QtCore import QCoreApplication

# This Python QT generated stuff
from MainWindow import Ui_MonefyFileSelect

class MonefyImporter(QWidget, Ui_MonefyFileSelect):
    def __init__(self):
        QWidget.__init__(self)

        self.setupUi(self)
        self.progressBar.hide()
        self.setWindowTitle("Monefy Importer")
        self.connectSignalsSlots()

    def connectSignalsSlots(self):
        print("Signal Connect Function used")

        self.actionexportFile.triggered.connect(self.exportFile)
        self.actionbrowseFile.triggered.connect(self.fileBrowse)

    def fileBrowse(self) :
        fileName, _ = QFileDialog.getOpenFileName(self, "Open purchase export", '',
                                                  "comma-separated values (*.csv);;All Files (*)")

        if not fileName:
            return

        try:
            fileTest = open(str(fileName))
        except IOError:
            QMessageBox.information(self, "Unable to open file",
                    f'There was an error opening "{fileName}"')
            return

        self.fileTextEdit.setPlainText(fileName)
        fileTest.close()

    def exportFile(self) :
        testFile = open(self.fileTextEdit.toPlainText())
        testReader = list(csv.reader(testFile))
        self.exportButton.hide()
        self.progressBar.show()
        self.progressBar.setProperty("value", 0)

        phone = phoneInterface()

        #for row in range(1) :


        for row in range(len(testReader)) :

            time.sleep(0.5) # wait for app to load
            phone.addInfo(testReader[row])

            self.progressBar.setProperty("value", row/len(testReader)*100)

        self.progressBar.setProperty("value", 100)
        self.exportButton.show()

if __name__ == "__main__":
    app = QApplication([])
    window = MonefyImporter()
    window.show()
    sys.exit(app.exec_())
