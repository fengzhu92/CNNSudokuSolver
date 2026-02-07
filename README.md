# Sudoku Solver

A desktop app that uses computer vision and a CNN to recognize Sudoku puzzles from images and solve them.

## Features

- Load a Sudoku image (JPG, PNG)
- Detect and extract the grid automatically
- Recognize digits with a trained CNN (MNIST-style)
- Solve the puzzle using backtracking
- Highlight answer digits vs given clues

## Requirements

- Python 3.9+
- PyQt5, OpenCV, Pillow, NumPy, TensorFlow 2.15

## Installation

```bash
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install PyQt5 opencv-python Pillow numpy "tensorflow>=2.12,<2.16"
```

## Usage

```bash
python mainPage.py
```

1. **Browse** — Select a Sudoku image
2. **Recognize** — Detect grid and recognize digits
3. **Solve!** — Solve the puzzle (answers are highlighted)
4. **Reset** — Clear and start over

## How It Works

- **Grid detection**: OpenCV finds the largest quadrilateral (the Sudoku border), warps to a square, and crops to 9×9 cells
- **Digit recognition**: Each cell is resized to 28×28 and fed to a CNN trained on MNIST-like digits
- **Solving**: Backtracking algorithm fills empty cells while respecting row, column, and 3×3 box constraints

## Project Structure

```
├── mainPage.py          # Main application
├── model/mnistCNN.h5    # Trained CNN for digit recognition
├── pics/                # Sample Sudoku images
├── intermediate/        # Debug images (detected grid, extracted grid)
└── venv/                # Virtual environment
```
