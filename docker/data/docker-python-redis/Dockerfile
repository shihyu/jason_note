FROM python:3.11-slim

# Add requirements file in the container
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# Add source code in the container
COPY redis_test_script.py ./redis_test_script.py

# Define container entry point (could also work with CMD python main.py)
ENTRYPOINT ["python", "redis_test_script.py"]
