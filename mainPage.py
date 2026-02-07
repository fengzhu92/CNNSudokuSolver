# -*- coding: utf-8 -*-
"""Smart Sudoku Solver - CNN-based puzzle recognition with PyQt5 UI."""

import cv2
import numpy as np
import PIL.ImageOps
from PIL import Image
from PyQt5 import QtCore, QtGui, QtWidgets
from tensorflow.keras.models import load_model

# Paths and config
MODEL_PATH = "model/mnistCNN.h5"
INTERMEDIATE_DIR = "intermediate"
CELL_SIZE = 28
EMPTY_CELL_THRESHOLD = 20
MIN_GRID_WIDTH = 300


def find_largest_quadrilateral(contours):
    """Find the largest 4-sided contour (likely the Sudoku grid)."""
    rects, lengths = [], []
    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)
        if len(approx) == 4:
            rects.append(approx)
            lengths.append(cv2.arcLength(cnt, True))
    if not rects:
        return None
    return rects[lengths.index(max(lengths))]


def extract_grid_from_image(img_array):
    """Detect grid, warp perspective, return cropped 9x9 image."""
    _, threshold = cv2.threshold(img_array, 180, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(
        threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    target = find_largest_quadrilateral(contours)
    if target is None:
        raise ValueError("No Sudoku grid found in image")

    width = min(cv2.boundingRect(target)[2:])
    if width < MIN_GRID_WIDTH:
        raise ValueError("Grid too small to process")

    # Warp to square
    pts1 = np.float32([target[1], target[0], target[2], target[3]])
    pts2 = np.float32([[0, 0], [width, 0], [0, width], [width, width]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    warped = cv2.warpPerspective(threshold, matrix, (width, width))

    # Center-crop to multiple of 9
    crop_w = (width // 9) * 9
    margin = (width - crop_w) // 2
    return Image.fromarray(warped).crop(
        (margin, margin, margin + crop_w, margin + crop_w)
    )


def recognize_digits(grid_image, model):
    """Run CNN on each cell, return 81-char string of digits (0 = empty)."""
    cell_w = grid_image.size[0] // 9
    result = []

    for r in range(9):
        for c in range(9):
            cell = grid_image.crop(
                (c * cell_w, r * cell_w, (c + 1) * cell_w, (r + 1) * cell_w)
            )
            cell = cell.crop((5, 5, cell_w - 5, cell_w - 5))
            cell = cell.resize((CELL_SIZE, CELL_SIZE))

            arr = np.array(cell).reshape(1, CELL_SIZE, CELL_SIZE, 1)
            if arr.any(axis=-1).sum() < EMPTY_CELL_THRESHOLD:
                result.append("0")
            else:
                pred = model.predict(arr)
                result.append(str(pred.argmax()))

    return "".join(result)


def solve_sudoku(grid):
    """Backtracking solver. Modifies grid in place. Returns True if solved."""
    def next_empty(i, j):
        for x in range(i, 9):
            for y in range(j, 9):
                if grid[x][y] == 0:
                    return x, y
        for x in range(9):
            for y in range(9):
                if grid[x][y] == 0:
                    return x, y
        return -1, -1

    def valid(i, j, val):
        if any(grid[i][x] == val for x in range(9)):
            return False
        if any(grid[x][j] == val for x in range(9)):
            return False
        box_x, box_y = 3 * (i // 3), 3 * (j // 3)
        for x in range(box_x, box_x + 3):
            for y in range(box_y, box_y + 3):
                if grid[x][y] == val:
                    return False
        return True

    i, j = next_empty(0, 0)
    if i == -1:
        return True
    for val in range(1, 10):
        if valid(i, j, val):
            grid[i][j] = val
            if solve_sudoku(grid):
                return True
            grid[i][j] = 0
    return False


class Ui_MainWindow:
    """Main application window."""

    def setupUi(self, MainWindow):
        self.puzzle = ""
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(760, 730)

        self._create_widgets(MainWindow)
        self._connect_signals()
        self.retranslateUi(MainWindow)
        MainWindow.setCentralWidget(self.centralwidget)

    def _create_widgets(self, MainWindow):
        self.centralwidget = QtWidgets.QWidget(MainWindow)

        # File browser
        widget = QtWidgets.QWidget(self.centralwidget)
        widget.setGeometry(140, 70, 470, 50)
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.filePath = QtWidgets.QLabel(widget)
        layout.addWidget(self.filePath)
        self.lineEdit = QtWidgets.QLineEdit(widget)
        layout.addWidget(self.lineEdit)
        self.browserBtn = QtWidgets.QPushButton(widget)
        layout.addWidget(self.browserBtn)

        # Title
        self.appTitleLabel = QtWidgets.QLabel(self.centralwidget)
        self.appTitleLabel.setGeometry(250, 10, 251, 61)
        self.appTitleLabel.setFont(QtGui.QFont("", 23, QtGui.QFont.Bold))
        self.appTitleLabel.setAlignment(QtCore.Qt.AlignCenter)

        # Buttons (centered: run + solve + reset)
        btn_y, btn_h, gap = 140, 30, 9
        run_w, solve_w, reset_w = 221, 160, 80
        total_w = run_w + gap + solve_w + gap + reset_w
        btn_start_x = (760 - total_w) // 2
        self.runBtn = QtWidgets.QPushButton(self.centralwidget)
        self.runBtn.setGeometry(btn_start_x, btn_y, run_w, btn_h)
        self.runBtn.setEnabled(False)
        self.solveBtn = QtWidgets.QPushButton(self.centralwidget)
        self.solveBtn.setGeometry(btn_start_x + run_w + gap, btn_y, solve_w, btn_h)
        self.solveBtn.setEnabled(False)
        self.resetBtn = QtWidgets.QPushButton(self.centralwidget)
        self.resetBtn.setGeometry(btn_start_x + run_w + gap + solve_w + gap, btn_y, reset_w, btn_h)

        # Image displays (image + caption above)
        self._init_image_with_caption("originalImage", "originalImageCaption", 70, 200, "")
        self._init_image_with_caption("interImage1", "interImage1Caption", 70, 480, "")
        self._init_image_with_caption("interImage2", "interImage2Caption", 370, 200, "")

        # Grid for digits
        grid_widget = QtWidgets.QWidget(self.centralwidget)
        grid_widget.setGeometry(370, 485, 250, 250)
        self.grid = QtWidgets.QGridLayout(grid_widget)
        self.grid.setContentsMargins(0, 0, 0, 0)

    def _init_image_with_caption(self, img_name, cap_name, x, y, caption):
        cap = QtWidgets.QLabel(self.centralwidget)
        cap.setGeometry(x, y - 22, 250, 20)
        cap.setText(caption)
        setattr(self, cap_name, cap)
        img = QtWidgets.QLabel(self.centralwidget)
        img.setGeometry(x, y, 250, 250)
        img.setScaledContents(True)
        setattr(self, img_name, img)

    def _connect_signals(self):
        self.browserBtn.clicked.connect(self._open_file_dialog)
        self.runBtn.clicked.connect(self._recognize_puzzle)
        self.solveBtn.clicked.connect(self._solve_puzzle)
        self.resetBtn.clicked.connect(self._reset)

    def retranslateUi(self, MainWindow):
        _ = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_("MainWindow", "Sudoku Solver"))
        self.filePath.setText(_("MainWindow", "FileName:"))
        self.browserBtn.setText(_("MainWindow", "Browse"))
        self.runBtn.setText(_("MainWindow", "Recognize"))
        self.solveBtn.setText(_("MainWindow", "Solve!"))
        self.resetBtn.setText(_("MainWindow", "Reset"))
        self.appTitleLabel.setText(_("MainWindow", "Smart Sudoku Solver"))

    def _reset(self):
        """Clear all state and reset UI to initial."""
        self.puzzle = ""
        self.inputImage = None
        self.lineEdit.clear()
        self.runBtn.setEnabled(False)
        self.solveBtn.setEnabled(False)
        for name in ("originalImage", "interImage1", "interImage2"):
            getattr(self, name).clear()
            getattr(self, name).repaint()
        for cap in ("originalImageCaption", "interImage1Caption", "interImage2Caption"):
            getattr(self, cap).setText("")
        self._clear_grid()

    def _open_file_dialog(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            None, "", "", "All Files (*);;Image Files (*.jpg *.png)"
        )
        if path:
            self.inputImage = path
            self.lineEdit.setText(path)
            self.runBtn.setEnabled(True)
            self.solveBtn.setEnabled(False)
            self.originalImageCaption.setText("Original")
            self.originalImage.setPixmap(QtGui.QPixmap(path))
            self.originalImage.repaint()

    def _recognize_puzzle(self):
        try:
            model = load_model(MODEL_PATH)
            img = Image.open(self.inputImage).convert("L")
            img = PIL.ImageOps.invert(img)
            img_array = np.array(img)

            # Find grid and extract
            grid_img = extract_grid_from_image(img_array)

            # Debug: save intermediate images
            img_rgb = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
            contours, _ = cv2.findContours(
                cv2.threshold(img_array, 180, 255, cv2.THRESH_BINARY)[1],
                cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            target = find_largest_quadrilateral(contours)
            if target is not None:
                cv2.drawContours(img_rgb, [target], -1, (0, 255, 0), 15)
            cv2.imwrite(f"{INTERMEDIATE_DIR}/img1.jpg", img_rgb)
            cv2.imwrite(f"{INTERMEDIATE_DIR}/img2.jpg", np.array(grid_img))

            digits = recognize_digits(grid_img, model)
            self.puzzle = digits
            self.runBtn.setEnabled(False)
            self.solveBtn.setEnabled(True)
            self._display_digits(digits, empty_color="green")
            self.interImage1Caption.setText("Extracted Grid")
            self.interImage2Caption.setText("Detected Game")
            self.interImage1.setPixmap(QtGui.QPixmap(f"{INTERMEDIATE_DIR}/img2.jpg"))
            self.interImage2.setPixmap(QtGui.QPixmap(f"{INTERMEDIATE_DIR}/img1.jpg"))
            self.interImage1.repaint()
            self.interImage2.repaint()

        except (ValueError, FileNotFoundError) as e:
            self.solveBtn.setEnabled(False)
            QtWidgets.QMessageBox.warning(
                None, "Error", f"Could not recognize puzzle: {e}"
            )

    def _clear_grid(self):
        """Remove all widgets from the digit grid."""
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w:
                w.setParent(None)

    def _display_digits(self, digits, empty_color="green", original_digits=None):
        """Fill grid with digit labels. If original_digits given, highlight answer cells."""
        self._clear_grid()
        for idx, (i, j) in enumerate((r, c) for r in range(9) for c in range(9)):
            label = QtWidgets.QLabel()
            if digits[idx] != "0":
                label.setText(digits[idx])
                # Highlight cells that were filled by the solver (originally empty)
                if original_digits and original_digits[idx] == "0":
                    label.setStyleSheet(
                        "background-color: #b3e5fc; font-weight: bold; color: #01579b;"
                    )
                else:
                    label.setStyleSheet("")
            else:
                label.setStyleSheet(f"background-color:{empty_color}")
            label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            self.grid.addWidget(label, i, j)

    def _solve_puzzle(self):
        grid = np.reshape([int(c) for c in self.puzzle], (9, 9)).tolist()
        if solve_sudoku(grid):
            solved = "".join(str(grid[i][j]) for i in range(9) for j in range(9))
            self._display_digits(solved, empty_color="transparent", original_digits=self.puzzle)
            self.solveBtn.setEnabled(False)
        else:
            QtWidgets.QMessageBox.warning(None, "Error", "No solution found.")


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(window)
    window.show()
    sys.exit(app.exec_())
