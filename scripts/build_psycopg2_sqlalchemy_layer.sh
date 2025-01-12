# builds psycopg2 with sqlalchemy layer for AWS Lambda

# create a directory for the psycopg2 layer
layer_dir="psycopg2-layer"
if [ -d "$layer_dir" ]; then
    rm -rf "$layer_dir"/*
else
    mkdir -p "$layer_dir"
fi
# store the currently active virtual environment
current_venv="$VIRTUAL_ENV"
echo "current_venv: $current_venv"

# create a temporary virtual environment, to avoid conflicts with the current environment
temp_venv="temp_venv"
python -m venv $temp_venv
source $temp_venv/bin/activate
# build for x86_64
pip install --platform manylinux2014_x86_64 --target $layer_dir --only-binary=:all: psycopg2-binary sqlalchemy

# deactivate and remove the temporary virtual environment
deactivate
rm -rf $temp_venv

# remove unnecessary files to reduce size
find $layer_dir -name "*.dist-info" -exec rm -rf {} +
find $layer_dir -name "*.egg-info" -exec rm -rf {} +
find $layer_dir -type d -name "tests" -exec rm -rf {} +
find $layer_dir -name "__pycache__" -exec rm -rf {} +

# create the necessary directory structure for AWS Lambda
python_dir="python/lib/python3.12/site-packages/"
mkdir -p $python_dir # create the directory if it doesn't exist
rm -rf $python_dir/* # clear the directory
mv $layer_dir/* $python_dir

# create the zip file
rm -f "$layer_dir".zip
zip -r "$layer_dir".zip python

# clean up
rm -rf $python_dir
rm -rf $layer_dir

source $current_venv/bin/activate
