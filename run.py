from flask import Flask, render_template, request, jsonify

import solver

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/solve', methods=['POST'])
def solve():
    sudoku_table = request.get_json()
    if solver.solve(sudoku_table):
        return jsonify({"solution": sudoku_table})
    else:
        return jsonify({"solution": "fail"})


if __name__ == "__main__":
    app.run(debug=False)
