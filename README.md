# Bin packing 2D
### Main informations if you would like to run this project

### 1. Clone
> git clone **<GIT_REPO_PATH>**

### 2. Preparing local workspace
Make sure you have installed python in version 3.10 or higher by typing:
> python --version

To start building package first download 'virtualenv' and create new virtual environment.
> pip install virtualenv
> 
> python -m virtualenv venv

Now activate it.
### Linux
> source venv/bin/activate
### Windows
>.\venv\Scripts\activate.bat

Install required packages:
> pip install -r dev-requirements.txt

### 3. Run application

To run script just type command:
> bin_packing_2d -i [input file or directory]

By default, all algorithms are launched. To run only specific algorithm type:
> bin_packing_2d -i [input file or directory] -a [algorithm_name]
 
Algorithm names can be found by typing ***bin_packing_2d -h***

To run script with plotting type command:
> bin_packing_2d -i [input file or directory] -p

To generate random input data run:
> generate_input_data
> 
 or
> 
> generate_plotting_data
> 
 or
> 
> generate_summary_data

Files will be saved to data/in, data/plot or data/summary directory.
