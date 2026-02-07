# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!

import PIL.ImageOps
import cv2
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(760, 730)
        MainWindow.setDocumentMode(False)
        self.puzzle = ""
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.originalImage = QtWidgets.QLabel(self.centralwidget)
        self.originalImage.setGeometry(QtCore.QRect(70, 200, 250, 250))
        self.originalImage.setText("")
        self.originalImage.setPixmap(QtGui.QPixmap("pics/no-image-icon.png"))
        self.originalImage.setScaledContents(True)
        self.originalImage.setObjectName("originalImage")
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(140, 70, 470, 50))
        self.widget.setObjectName("widget")
        self.fileBrowserPanel = QtWidgets.QHBoxLayout(self.widget)
        self.fileBrowserPanel.setContentsMargins(0, 0, 0, 0)
        self.fileBrowserPanel.setObjectName("fileBrowserPanel")
        self.filePath = QtWidgets.QLabel(self.widget)
        self.filePath.setObjectName("filePath")
        self.fileBrowserPanel.addWidget(self.filePath)
        self.lineEdit = QtWidgets.QLineEdit(self.widget)
        self.lineEdit.setObjectName("lineEdit")
        self.fileBrowserPanel.addWidget(self.lineEdit)
        self.browserBtn = QtWidgets.QPushButton(self.widget)
        self.browserBtn.setObjectName("browserBtn")
        self.fileBrowserPanel.addWidget(self.browserBtn)
        self.interImage1 = QtWidgets.QLabel(self.centralwidget)
        self.interImage1.setGeometry(QtCore.QRect(70, 460, 250, 250))
        self.interImage1.setSizeIncrement(QtCore.QSize(200, 200))
        self.interImage1.setText("")
        self.interImage1.setPixmap(QtGui.QPixmap("pics/no-image-icon.png"))
        self.interImage1.setScaledContents(True)
        self.interImage1.setObjectName("interImage1")
        self.runBtn = QtWidgets.QPushButton(self.centralwidget)
        self.runBtn.setEnabled(False)
        self.runBtn.setGeometry(QtCore.QRect(250, 140, 221, 30))
        self.runBtn.setCheckable(False)
        self.runBtn.setAutoDefault(False)
        self.runBtn.setDefault(False)
        self.runBtn.setObjectName("runBtn")
        self.interImage2 = QtWidgets.QLabel(self.centralwidget)
        self.interImage2.setGeometry(QtCore.QRect(370, 200, 250, 250))
        self.interImage2.setMinimumSize(QtCore.QSize(100, 100))
        self.interImage2.setMaximumSize(QtCore.QSize(250, 250))
        self.interImage2.setSizeIncrement(QtCore.QSize(200, 200))
        self.interImage2.setBaseSize(QtCore.QSize(200, 200))
        self.interImage2.setText("")
        self.interImage2.setPixmap(QtGui.QPixmap("pics/no-image-icon.png"))
        self.interImage2.setScaledContents(True)
        self.interImage2.setObjectName("interImage2")
        self.gridLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(370, 485, 250, 250))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.grid = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setObjectName("grid")
        self.solveBtn = QtWidgets.QPushButton(self.centralwidget)
        self.solveBtn.setGeometry(QtCore.QRect(370, 455, 160, 30))
        self.solveBtn.setEnabled(False)
        self.solveBtn.setCheckable(False)
        self.solveBtn.setAutoDefault(False)
        self.solveBtn.setDefault(False)
        self.solveBtn.setObjectName("solveBtn")
        self.appTitleLabel = QtWidgets.QLabel(self.centralwidget)
        self.appTitleLabel.setGeometry(QtCore.QRect(250, 10, 251, 61))
        font = QtGui.QFont()
        font.setPointSize(23)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.appTitleLabel.setFont(font)
        self.appTitleLabel.setScaledContents(False)
        self.appTitleLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.appTitleLabel.setObjectName("appTitleLabel")
        self.widget1 = QtWidgets.QWidget(self.centralwidget)
        self.widget1.setGeometry(QtCore.QRect(47, 548, 200, 16))
        self.widget1.setObjectName("widget1")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.browserBtn.clicked.connect(self.open_fileDialog)
        self.runBtn.clicked.connect(self.recognizePuzzle)
        self.solveBtn.clicked.connect(self.resolve_btn_handler)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.filePath.setText(_translate("MainWindow", "FileName:"))
        self.browserBtn.setText(_translate("MainWindow", "Browse"))
        self.runBtn.setText(_translate("MainWindow", "Recognize"))
        self.solveBtn.setText(_translate("MainWindow", "Solve!"))
        self.appTitleLabel.setText(_translate("MainWindow", "Smart Sudoku Solver"))

    def open_fileDialog(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
            None,
            "QFileDialog.getOpenFileName()",
            "",
            "All Files (*);;Image Files (*.jpg *.png)",
            options=options)
        if fileName:
            self.display_input(fileName)
            self.inputImage = fileName

    def display_input(self, selectedFile):
        self.lineEdit.setText(selectedFile)
        self.runBtn.setEnabled(True)
        self.originalImage.setPixmap(QtGui.QPixmap(selectedFile))
        self.originalImage.repaint()

    def display_output(self, inter1, inter2, digits):
        self.interImage1.setPixmap(QtGui.QPixmap(inter1))
        self.interImage2.setPixmap(QtGui.QPixmap(inter2))
        self.interImage1.repaint()
        self.interImage2.repaint()

        numsArray = list(digits)
        positions = [(i, j) for i in range(9) for j in range(9)]
        for position, number in zip(positions, numsArray):
            if number != '0':
                label = QtWidgets.QLabel(number)
            elif number == '0':
                label = QtWidgets.QLabel()
                label.setStyleSheet('background-color:green')
            label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            self.grid.addWidget(label, *position)

    def recognizePuzzle(self, imagePath):
        model = load_model('model/mnistCNN.h5')
        orgImg = Image.open(self.inputImage).convert("L")
        orgImg = PIL.ImageOps.invert(orgImg)
        img = np.array(orgImg)

        rects = []
        rectLengths = []
        _, threshold = cv2.threshold(img, 180, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            approx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)
            if len(approx) == 4:
                rects.append(approx)
                rectLengths.append(cv2.arcLength(cnt, True))
        maxLength = max(rectLengths)
        ind = rectLengths.index(maxLength)
        targetApprox = rects[ind]
        rx, ry, rw, rh = cv2.boundingRect(targetApprox)
        print(rx, ry, rw, rh)
        cv2.drawContours(img, targetApprox, -1, (0, 255, 0), 15)
        cv2.imwrite("intermediate/img1.jpg", img)

        width = min(rw, rh)
        if width < 300:
            exit(2)
        pts1 = np.float32([targetApprox[1], targetApprox[0], targetApprox[2], targetApprox[3]])
        pts2 = np.float32([[0, 0], [width, 0], [0, width], [width, width]])
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        img = cv2.warpPerspective(threshold, matrix, (width, width))
        cv2.imwrite("intermediate/img2.jpg", img)

        img_pil = Image.fromarray(img)
        w, h = img_pil.size
        cropWidth = (width // 9) * 9
        img_pil = img_pil.crop(
            ((w - cropWidth) // 2, (w - cropWidth) // 2, (w - cropWidth) // 2 + cropWidth,
             (w - cropWidth) // 2 + cropWidth))
        actW, actH = img_pil.size
        # print(actW,actH)
        actCellWidth = actW // 9
        # print(actCellWidth)
        result = ""

        for r in range(0, 9):
            for c in range(0, 9):
                currImg = img_pil.crop(
                    (c * actCellWidth, r * actCellWidth, c * actCellWidth + actCellWidth,
                     r * actCellWidth + actCellWidth))
                currImg = currImg.crop((5, 5, actCellWidth - 5, actCellWidth - 5))
                currImg = currImg.resize((28, 28))
                # currImg.show()
                npImg = np.array(currImg)
                npImg = npImg.reshape(1, 28, 28, 1)
                # print(npImg.any(axis=-1).sum())
                if npImg.any(axis=-1).sum() < 20:
                    result = result + str(0)
                else:
                    prediction = model.predict(npImg)
                    result = result + str(prediction.argmax())
        self.solveBtn.setEnabled(True) 
        self.display_output("intermediate/img1.jpg", "intermediate/img2.jpg", result)
        self.puzzle = result


    def resolve_btn_handler(self, result):
        # solve puzzle
        puzzleNumbers = [int(x) for x in self.puzzle]
        numGrid = np.reshape(list(puzzleNumbers), (-1, 9))
        success = self.solveSudoku(numGrid)
        if success:
            self.display_answer(numGrid)

    def display_answer(self, answerGrid):
        positions = [(i, j) for i in range(9) for j in range(9)]
        for position in positions:
            num = str(answerGrid[position[0]][position[1]])
            label = QtWidgets.QLabel(num)
            label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            self.grid.addWidget(label, *position)

    def findNextCellToFill(self, grid, i, j):
        for x in range(i, 9):
            for y in range(j, 9):
                if grid[x][y] == 0:
                    return x, y
        for x in range(0, 9):
            for y in range(0, 9):
                if grid[x][y] == 0:
                    return x, y
        return -1, -1

    def isValid(self, grid, i, j, e):
        rowOk = all([e != grid[i][x] for x in range(9)])
        if rowOk:
            columnOk = all([e != grid[x][j] for x in range(9)])
            if columnOk:
                # finding the top left x,y co-ordinates of the section containing the i,j cell
                secTopX, secTopY = 3 * (i // 3), 3 * (j // 3)  # floored quotient should be used here.
                for x in range(secTopX, secTopX + 3):
                    for y in range(secTopY, secTopY + 3):
                        if grid[x][y] == e:
                            return False
                return True
        return False

    def solveSudoku(self, grid, i=0, j=0):
        i, j = self.findNextCellToFill(grid, i, j)
        if i == -1:
            return True
        for e in range(1, 10):
            if self.isValid(grid, i, j, e):
                grid[i][j] = e
                if self.solveSudoku(grid, i, j):
                    return True
                # Undo the current cell for backtracking
                grid[i][j] = 0
        return False


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
