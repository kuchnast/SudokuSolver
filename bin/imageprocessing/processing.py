import cv2
import numpy as np
import os
import imutils
import imutils.perspective

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

input_size = 48


def find_board(img):
    """ Take an image as input and find a sudoku board inside the image."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite("data/1_gray.png", gray)
    bfilter = cv2.bilateralFilter(gray, 13, 20, 20)
    cv2.imwrite("data/2_bilateralFilter.png", bfilter)
    edged = cv2.Canny(bfilter, 30, 180)
    cv2.imwrite("data/canny.png", edged)
    keypoints = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # test2 = np.zeros(img.shape, dtype=np.uint8)
    # cv2.drawContours(test2, keypoints, -1, (255,255,255),1)
    # cv2.imwrite("data/test2.png", test2)
    contours = imutils.grab_contours(keypoints)

    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # Finds rectangular contour
    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, peri * 0.01, True)
        if len(approx) == 4:
            location = approx
            result = imutils.perspective.four_point_transform(img, location.reshape(4, 2))
            result = cv2.resize(result, (900, 900), interpolation=cv2.INTER_CUBIC)
            cv2.imwrite("data/result.png", result)
            return result

    return []


# split the board into 81 individual images
def split_boxes(board):
    """
    Take a sudoku board and split it into 81 cells.

    Each cell contains an element of that board either given or an empty cell.
    """
    rows = np.vsplit(board, 9)
    boxes = []
    for r in rows:
        cols = np.hsplit(r, 9)
        for box in cols:
            box = cv2.resize(box, (input_size, input_size)) / 255.0
            boxes.append(box)

    return boxes


def get_digits_from_img(img_file):
    if isinstance(img_file, str):
        img = cv2.imread(img_file, cv2.IMREAD_UNCHANGED)
    else:
        file_bytes = np.frombuffer(img_file.read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_UNCHANGED)

    max_dimension = 1000
    if img.shape[0] > max_dimension or img.shape[1] > max_dimension:
        height = img.shape[0]
        width = img.shape[1]
        proportion = height / width
        height = max_dimension
        width = round(height / proportion)
        img = cv2.resize(img, (width, height))

    board = find_board(img)
    if len(board) == 0:
        return board

    gray = cv2.cvtColor(board, cv2.COLOR_BGR2GRAY)
    rois = split_boxes(gray)
    rois = np.array(rois).reshape(-1, input_size, input_size, 1)

    prediction = model.predict(rois)

    predicted_numbers = []
    for pred in prediction:
        predicted_number = int(pred.argmax())
        predicted_numbers.append(predicted_number)

    return predicted_numbers


if __name__ == "__main__":
    get_digits_from_img("data/sudoku1.jpg")
