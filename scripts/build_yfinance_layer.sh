# builds psycopg2 layer for AWS Lambda
# see: https://medium.com/@bloggeraj392/creating-a-psycopg2-layer-for-aws-lambda-a-step-by-step-guide-a2498c97c11e

# create a directory for the psycopg2 layer
layer_dir="yfinance-layer"
# if [ -d "$layer_dir" ]; then
#     rm -rf "$layer_dir"
# fi
# mkdir -p "$layer_dir"
if [ -d "$layer_dir" ]; then
    rm -rf "$layer_dir"/*
else
    mkdir -p "$layer_dir"
fi
cd "$layer_dir"

# build for for x86_64
pip install --platform manylinux2014_x86_64 --target . --python-version 3.12 --only-binary=:all: yfinance
# build for for arm64
# pip3 install --platform manylinux2014_aarch64 --target . --python-version 3.12 --only-binary=:all: yfinance

cd ..
zip -r yfinance-layer.zip $layer_dir

# clean up
#rm -rf $layer_dir
