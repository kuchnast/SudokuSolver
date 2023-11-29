import cv2
import numpy as np
import os
import imutils
import imutils.perspective
from pathlib import Path

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

DEBUG = 1
DEBUG_DATA_DIR = 'data/debug'


def _find_board(img):
    """ Take an image as input and find a sudoku board inside the image."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if DEBUG:
        file_path = f'{DEBUG_DATA_DIR}/1_gray.png'
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(file_path, gray)

    bfilter = cv2.bilateralFilter(gray, 13, 20, 20)
    if DEBUG:
        cv2.imwrite(f"{DEBUG_DATA_DIR}/2_bilateralFilter.png", bfilter)

    edged = cv2.Canny(bfilter, 30, 180)
    if DEBUG:
        cv2.imwrite(f"{DEBUG_DATA_DIR}/3_canny.png", edged)

    key_points = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(key_points)

    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # Finds biggest, rectangular contour
    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, peri * 0.01, True)
        if len(approx) == 4:
            location = approx
            result = imutils.perspective.four_point_transform(img, location.reshape(4, 2))
            result = cv2.resize(result, (900, 900), interpolation=cv2.INTER_CUBIC)
            if DEBUG:
                cv2.imwrite(f"{DEBUG_DATA_DIR}/4_board.png", result)
            return result

    return None


def _split_boxes(board):
    """
    Take a sudoku board and split it into 81 cells using simple board area division.

    Each cell contains an element of that board either given or an empty cell.
    """
    if DEBUG:
        Path(f'{DEBUG_DATA_DIR}/split_boxes_cells').mkdir(parents=True, exist_ok=True)

    rows = np.vsplit(board, 9)
    cells = []
    for r in range(len(rows)):
        cols = np.hsplit(rows[r], 9)
        for c in range(len(cols)):
            cells.append(cols[c])
            if DEBUG:
                cv2.imwrite(f"{DEBUG_DATA_DIR}/split_boxes_cells/r{r + 1}c{c + 1}.png", cols[c])

    return cells


def _split_boxes_enchanted(board):
    cells = _split_cells_without_lines(board)
    if DEBUG:
        Path(f'{DEBUG_DATA_DIR}/split_boxes_enchanted_cells').mkdir(parents=True, exist_ok=True)
        for i in range(len(cells)):
            cv2.imwrite(f"{DEBUG_DATA_DIR}/split_boxes_enchanted_cells/cell_{i}.png", cells[i])

    filtered_cells = _filter_cells(cells)
    if DEBUG:
        Path(f'{DEBUG_DATA_DIR}/split_boxes_enchanted_filtered').mkdir(parents=True, exist_ok=True)
        for i in range(len(filtered_cells)):
            cv2.imwrite(f"{DEBUG_DATA_DIR}/split_boxes_enchanted_filtered/cell_r{(int(i / 9) + 1)}_c{(i % 9) + 1}.png",
                        filtered_cells[i])

    if len(filtered_cells) != 81:
        if DEBUG:
            print(f"Incorrect number of cells: {len(filtered_cells)}")
        return None

    return filtered_cells


def _split_cells_without_lines(board):
    """
       Take a sudoku board, convert on binary image, find contours of rectangular boxes and split
    """
    blur = cv2.GaussianBlur(board, (5, 5), 0)
    _, binary = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    contours_with_indices = [(i, cv2.boundingRect(contour)) for i, contour in enumerate(contours)]
    contours_with_indices.sort(key=lambda x: (x[1][1] // 50, x[1][0] // 50))

    if DEBUG:
        contour_image = np.zeros_like(board)
        cv2.drawContours(contour_image, contours, -1, (255, 255, 255), 2)
        cv2.imwrite(f'{DEBUG_DATA_DIR}/split_cells_without_lines.png', binary)

    # Split board on rectangular boxes
    cells = []
    for i, _ in contours_with_indices:
        x, y, w, h = cv2.boundingRect(contours[i])
        cell = binary[y:y + h, x:x + w]
        cells.append(cell)

    return cells


def _filter_cells(cells):
    """
    Filter out cells that are too narrow, too long or have non-square proportions
    """
    filtered_cells = []
    aspect_ratio_tolerance = 0.2

    for cell in cells:
        height, width = cell.shape
        aspect_ratio = width / height

        if (1 - aspect_ratio_tolerance) < aspect_ratio < (1 + aspect_ratio_tolerance) and width > 10 and height > 10:
            filtered_cells.append(cell)

    return filtered_cells


def get_digits_from_image(image_or_path):
    if isinstance(image_or_path, str):
        img = cv2.imread(image_or_path, cv2.IMREAD_UNCHANGED)
    else:
        file_bytes = np.frombuffer(image_or_path.read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_UNCHANGED)

    max_dimension = 1000
    if img.shape[0] > max_dimension or img.shape[1] > max_dimension:
        height = img.shape[0]
        width = img.shape[1]
        proportion = height / width
        height = max_dimension
        width = round(height / proportion)
        img = cv2.resize(img, (width, height))

    board = _find_board(img)
    if board is None:
        return None
    gray_board = cv2.cvtColor(board, cv2.COLOR_BGR2GRAY)
    if DEBUG:
        cv2.imwrite(f"{DEBUG_DATA_DIR}/5_gray_board.png", gray_board)

    cells = _split_boxes(gray_board)
    cells = _split_boxes_enchanted(gray_board)

    # TODO: Add digits recognition from cells

    return None


if __name__ == "__main__":
    base_debug_dir = DEBUG_DATA_DIR
    DEBUG_DATA_DIR = base_debug_dir + '_sudoku1'
    get_digits_from_image("data/sudoku1.jpg")
    DEBUG_DATA_DIR = base_debug_dir + '_sudoku2'
    get_digits_from_image("data/sudoku2.png")
