import setuptools

setuptools.setup(
    name="sudoku_solver",
    package_dir={"": "bin"},
    packages=setuptools.find_packages(where="bin"),
    python_requires=">=3.10",
    install_requires=[
        "opencv-python",
        "opencv-stubs",
        "numpy",
        "flask",
        "flask_cors",
        "scikit-image"
    ],
    entry_points={'console_scripts':
                  ['start_server = app:run',
                   'run_test = imageprocessing.processing:run_test']}
)
