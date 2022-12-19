from flask import Flask, render_template, request, jsonify

from solver import Solver
from imageprocessing import processing

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/solve', methods=['POST'])
def solve():
    solv = Solver(request.get_json())
    if solv.solve():
        return jsonify({"solution": solv.sudoku_table})

    return jsonify({"solution": "fail"})

@app.route('/process_image', methods=['POST'])
def scan_image():
    img_file = request.files.get("image")
    board = processing.get_digits_from_img(img_file)
    if len(board) > 0:
        return jsonify({"result": board})

    return jsonify({"result": "fail"})


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
