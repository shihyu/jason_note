ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim

RUN echo "Using Python version: ${PYTHON_VERSION}"

# Add requirements file in the container
COPY requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# Add source code in the container
COPY main.py ./main.py

# Define container entry point
ENTRYPOINT ["python", "main.py"]
