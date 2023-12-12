import setuptools

setuptools.setup(
    name="sudoku_solver",
    package_dir={"": "bin"},
    packages=setuptools.find_packages(where="bin"),
    python_requires=">=3.10",
    install_requires=[
        "argparse ~= 1.4",
        "opencv-python",
        "opencv-stubs",
        "imutils",
        "numpy",
        "flask",
        "flask_cors",
        "scipy",
        "scikit-image"
    ],
    entry_points={'console_scripts':
                  ['start_server = app:run']}
)
