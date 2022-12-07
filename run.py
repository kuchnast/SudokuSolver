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
    else:
        return jsonify({"solution": "fail"})

@app.route('/scan_image', methods=['POST'])
def scan_image():
    board = processing.get_digits_from_img("imageprocessing/sudoku1.jpg")
    return jsonify({"board": board})


if __name__ == "__main__":
    app.run(debug=False)
