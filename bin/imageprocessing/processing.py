import cv2
import numpy as np
import os
import imutils
import imutils.perspective
from pathlib import Path
import shutil
from skimage.feature import hog

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

DEBUG = 1
DATA_DIR = 'data'
DEBUG_DATA_DIR = f'{DATA_DIR}/debug'


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
        Path(f'{DEBUG_DATA_DIR}/7_split_boxes_enchanted_cells').mkdir(parents=True, exist_ok=True)
        for i in range(len(cells)):
            cv2.imwrite(f"{DEBUG_DATA_DIR}/7_split_boxes_enchanted_cells/cell_{i}.png", cells[i])

    filtered_cells = _filter_cells(cells)
    if DEBUG:
        Path(f'{DEBUG_DATA_DIR}/8_split_boxes_enchanted_filtered').mkdir(parents=True, exist_ok=True)
        for i in range(len(filtered_cells)):
            cv2.imwrite(
                f"{DEBUG_DATA_DIR}/8_split_boxes_enchanted_filtered/cell_r{(int(i / 9) + 1)}_c{(i % 9) + 1}.png",
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
        cv2.imwrite(f'{DEBUG_DATA_DIR}/6_split_cells_without_lines.png', binary)

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

        if (1 - aspect_ratio_tolerance) < aspect_ratio < (1 + aspect_ratio_tolerance) and width > 50 and height > 50:
            filtered_cells.append(cell)

    return filtered_cells


def print_sudoku_board(board):
    print("┌───────┬───────┬───────┐")

    for i, row in enumerate(board):
        print("│ ", end="")
        for j, cell in enumerate(row):
            print(cell if cell is not None else " ", end=" ")
            if (j + 1) % 3 == 0 and j < 8:
                print("│ ", end="")
        print("│")

        if (i + 1) % 3 == 0 and i < 8:
            print("├───────┼───────┼───────┤")

    print("└───────┴───────┴───────┘")


def _create_sudoku_board(recognized_digits):
    board = [[None for _ in range(9)] for _ in range(9)]

    for index, image, digit in recognized_digits:
        row = int(index / 9)
        col = index % 9
        board[row][col] = digit

    return board


def _contains_digit(cell, threshold=0.02):
    total_pixels = cell.size
    black_pixels = np.sum(cell == 0)

    ratio = black_pixels / total_pixels

    return ratio > threshold


def _clear_cell_noise(cell):
    _, binary_inv = cv2.threshold(cell, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, hierarchy = cv2.findContours(binary_inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    height, width = binary_inv.shape
    border_contours = []
    significant_contour_removed = False

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        # If the contour is touching the border, add it to the list to be removed
        if x <= 1 or y <= 1 or (x + w) >= width - 1 or (y + h) >= height - 1:
            # Check if removing this contour would remove a significant part of the image
            if cv2.contourArea(cnt) > (height * width * 0.05):  # Threshold set to 5% of the image area
                significant_contour_removed = True
                continue
            border_contours.append(cnt)

    # Create a mask with only the border contours
    border_mask = np.zeros_like(binary_inv)
    cv2.drawContours(border_mask, border_contours, -1, (255, 255, 255), cv2.FILLED)

    # Use the border mask to remove the border contours from the original inverted binary image
    if not significant_contour_removed:
        digit_cleaned = cv2.bitwise_and(binary_inv, binary_inv, mask=~border_mask)
        # Invert the image back to original form (digit in black)
        digit_final = cv2.bitwise_not(digit_cleaned)
    else:
        # If a significant contour would have been removed, we return the original image
        digit_final = cell

    return digit_final


def _load_digit_templates(templates_dir):
    templates = {}
    for filename in os.listdir(templates_dir):
        if filename.endswith('.png'):
            digit = int(filename.split('.')[0])
            template_path = os.path.join(templates_dir, filename)
            template_img = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
            templates[digit] = template_img
    return templates


def _find_digit(input_img, templates_dir):
    templates = _load_digit_templates(templates_dir)
    input_height, input_width = input_img.shape[:2]
    highest_score = None
    recognized_digit = None

    for digit, template_img in templates.items():
        template_height, template_width = template_img.shape[:2]

        # Scale input image to match the template height or width (whichever is closer in aspect ratio)
        scale = template_height / input_height if (input_height / input_width) < (
                template_height / template_width) else template_width / input_width
        scaled_input_img = cv2.resize(input_img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

        # Calculate score using template matching
        result = cv2.matchTemplate(scaled_input_img, template_img, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)

        if highest_score is None or max_val > highest_score:
            highest_score = max_val
            recognized_digit = digit

    return recognized_digit


def _find_digit_hog(input_img, templates_dir):
    templates = _load_digit_templates(templates_dir)
    input_height, input_width = input_img.shape[:2]
    highest_score = None
    recognized_digit = None

    for digit, template_img in templates.items():
        template_height, template_width = template_img.shape[:2]

        # Scale input image to match the template height or width (whichever is closer in aspect ratio)
        scale = template_height / input_height if (input_height / input_width) < (
                template_height / template_width) else template_width / input_width
        scaled_input_img = cv2.resize(input_img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

        # If input image is smaller than template, pad it with white pixels
        if scaled_input_img.shape[0] < template_height or scaled_input_img.shape[1] < template_width:
            padded_input_img = np.full_like(template_img, 255)
            y_offset = (template_height - scaled_input_img.shape[0]) // 2
            x_offset = (template_width - scaled_input_img.shape[1]) // 2
            padded_input_img[y_offset:y_offset + scaled_input_img.shape[0],
            x_offset:x_offset + scaled_input_img.shape[1]] = scaled_input_img
            scaled_input_img = padded_input_img

        # If input image is bigger than template, pad template with white pixels
        if scaled_input_img.shape[0] > template_height or scaled_input_img.shape[1] > template_width:
            y_offset = (scaled_input_img.shape[0] - template_height) // 2
            x_offset = (scaled_input_img.shape[1] - template_width) // 2
            padded_template_img = np.full_like(scaled_input_img, 255)
            padded_template_img[y_offset:y_offset + template_height, x_offset:x_offset + template_width] = template_img
            template_img = padded_template_img

        cv2.imwrite(f"{DEBUG_DATA_DIR}/input.png", scaled_input_img)
        cv2.imwrite(f"{DEBUG_DATA_DIR}/template.png", template_img)

        input_hog = hog(scaled_input_img, pixels_per_cell=(8, 8), cells_per_block=(1, 1), visualize=False)
        template_hog = hog(template_img, pixels_per_cell=(8, 8), cells_per_block=(1, 1), visualize=False)

        # Calculate the similarity score using the dot product
        score = np.dot(input_hog, template_hog)

        if highest_score is None or score > highest_score:
            highest_score = score
            recognized_digit = digit

    return recognized_digit

    # Scale the input image to the size of the template images
    template_images = _load_digit_templates(templates_dir)
    template_size = next(iter(template_images.values())).shape
    input_img_resized = cv2.resize(input_img, template_size[::-1], interpolation=cv2.INTER_AREA)

    # Calculate HOG features for the resized input image
    input_hog = hog(input_img_resized, pixels_per_cell=(14, 14), cells_per_block=(1, 1), visualize=False)

    highest_score = -1
    recognized_digit = None

    # Compare HOG features of the input image with each template image
    for digit, template_img in template_images.items():
        # Ensure the template images are also resized to the common size (if not already)
        if template_img.shape != template_size:
            template_img = cv2.resize(template_img, template_size[::-1], interpolation=cv2.INTER_AREA)
        template_hog = hog(template_img, pixels_per_cell=(14, 14), cells_per_block=(1, 1), visualize=False)

        # Calculate the similarity score using the dot product
        score = np.dot(input_hog, template_hog)

        if score > highest_score:
            highest_score = score
            recognized_digit = digit

    return recognized_digit


def _crop_digit(cell):
    iverted_cell = cv2.bitwise_not(cell)

    # Find the bounding rectangle for the largest contour
    x, y, w, h = cv2.boundingRect(iverted_cell)

    # Crop the image to the bounding box
    cropped_digit = iverted_cell[y:y + h, x:x + w]
    cropped_digit = cv2.bitwise_not(cropped_digit)

    return cropped_digit


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

    cells = _split_boxes_enchanted(gray_board)

    if cells is None:
        return None

    labels = []

    cleared_cells = [_clear_cell_noise(cell) for cell in cells]

    for index, cell in enumerate(cleared_cells):
        if _contains_digit(cell):
            labels.append(f'{index}_Y')
        else:
            labels.append(f'{index}_N')

    if DEBUG:
        Path(f'{DEBUG_DATA_DIR}/9_cleared_cells_with_labels').mkdir(parents=True, exist_ok=True)
        for index, cell in enumerate(cleared_cells):
            cv2.imwrite(f"{DEBUG_DATA_DIR}/9_cleared_cells_with_labels/"
                        f"cell_r{(int(index / 9) + 1)}_c{(index % 9) + 1}_{labels[index][-1]}.png", cell)

    cropped_digits = [(index, _crop_digit(cell)) for index, (label, cell) in enumerate(zip(labels, cleared_cells))
                      if label[-1] == 'Y']

    if DEBUG:
        Path(f'{DEBUG_DATA_DIR}/10_cropped_digits').mkdir(parents=True, exist_ok=True)
        for index, cell in cropped_digits:
            cv2.imwrite(f"{DEBUG_DATA_DIR}/10_cropped_digits/"
                        f"d{index}.png", cell)

    recognized_digits = [(index, digit_img, _find_digit(digit_img, 'data/digit_templates'))
                         for index, digit_img in cropped_digits]

    if DEBUG:
        Path(f'{DEBUG_DATA_DIR}/11_recognized_digits').mkdir(parents=True, exist_ok=True)
        for index, digit_img, digit in recognized_digits:
            cv2.imwrite(f"{DEBUG_DATA_DIR}/11_recognized_digits/"
                        f"cell_r{(int(index / 9) + 1)}_c{(index % 9) + 1}_digit_{digit}.png", digit_img)

    recognized_digits_hog = [(index, digit_img, _find_digit_hog(digit_img, 'data/digit_templates'))
                             for index, digit_img in cropped_digits]

    if DEBUG:
        Path(f'{DEBUG_DATA_DIR}/11_recognized_digits_hog').mkdir(parents=True, exist_ok=True)
        for index, digit_img, digit in recognized_digits_hog:
            cv2.imwrite(f"{DEBUG_DATA_DIR}/11_recognized_digits_hog/"
                        f"cell_r{(int(index / 9) + 1)}_c{(index % 9) + 1}_digit_{digit}.png", digit_img)

    board = _create_sudoku_board(recognized_digits)

    if DEBUG:
        print_sudoku_board(board)

    return board


def run_test():
    def test(file_name: str):
        print(f"Board for file {file_name}:")
        global DEBUG_DATA_DIR
        DEBUG_DATA_DIR = base_debug_dir + f'_{file_name.split(".")[0]}'
        shutil.rmtree(DEBUG_DATA_DIR, ignore_errors=True)
        get_digits_from_image(f"{DATA_DIR}/{file_name}")

    base_debug_dir = DEBUG_DATA_DIR
    files = ["sudoku1.jpg", "sudoku2.png", "sudoku3.png", "sudoku4.png"]

    for file in files:
        test(file)


if __name__ == "__main__":
    run_test()
