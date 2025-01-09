# For more information, please refer to https://aka.ms/vscode-docker-python
FROM public.ecr.aws/lambda/python:3.12

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

COPY lambdas/cef_data_clean_lambda.py .
COPY src/stock_data_clean.py .
COPY src/utils.py .
COPY src/rds_functions.py .

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD [ "cef_data_clean_lambda.lambda_handler" ]