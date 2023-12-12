from solver import Solver
from imageprocessing import processing
import mimetypes

mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__, template_folder="../templates", static_folder="../static/")
# app = Flask(__name__)
CORS(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/solve", methods=["POST"])
def solve():
    solv = Solver(request.get_json())
    if solv.solve():
        return jsonify({"solution": solv.sudoku_table})

    return jsonify({"solution": "fail"})


@app.route("/process_image", methods=["POST"])
def scan_image():
    img_file = request.files.get("image")
    board = processing.get_digits_from_image(img_file)
    if board is not None:
        flat_board = [cell for row in board for cell in row]
        return jsonify({"result": flat_board})

    return jsonify({"result": "fail"})


def run():
    app.run(debug=False, host="0.0.0.0")


if __name__ == "__main__":
    run()
