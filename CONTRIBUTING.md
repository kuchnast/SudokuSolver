# Contributing guide
### Main informations if you would like to help in this project

### 1. Fork
> git clone **<FORK_GIT_REPO_PATH>**

### 2. Preparing local workspace
Make sure you have instaled python in version 3.10 or higher by typing:
> python --version

To start developing first download 'virtualenv' and create new virtual environment.
> pip install virtualenv
> 
> python -m virtualenv venv

Now activate it.
### Linux
> source venv/bin/activate
### Windows
>.\venv\Scripts\activate.bat

### Tips
Especially for Windows I recommend using PyCharm to be able easily run tests. Also, linux subsystem is a bit tricky so cmd is better option imo. In this case, you need to install python and git for windows to be able to build package. 

In PyCharm on Windows by default PowerShell is started as local terminal. I don't recommend using it. 

### What next
Install development packages.
> pip install -r dev-requirements.txt

In order to run pytest tests:
> pytest

In order to run formatting and syntax tests **(not necessary)**:
> tox -e black-check,mypy,flake8

To run script just type command:
> sudoku_solver 

Before submitting automatically format source files:
>tox -e black
