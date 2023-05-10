# docker-python-helloworld
A Python dockerized hello world app
This repo aims at showing how simple it can be to build a Docker container running a Python (very simple) app.
Once you understand how this simple example works, it's easy to apply it to bigger apps.

### Steps to run directly the python code
It's highly recommended to install the (empty) dependencies in a virtual environment.

- Creating the virtual environment: 
```bash
virtualenv venv
```

- Activatingv the virtual environment:
```bash
source venv/bin/activate
```
- Installing dependencies:
```bash
pip install -r requirements.txt
```

- Running the code:
```bash
python main.py
```


### Steps to run the python code withing a Docker container

- Build the image:
```bash
docker build -t docker-python-helloworld:lastest
```

- Run the container:
```bash
docker run docker-python-helloworld:latest 
```



