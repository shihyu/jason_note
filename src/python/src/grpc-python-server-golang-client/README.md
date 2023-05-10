### [Understanding gRPC: A practical application in Go and Python](https://medium.com/@apbetahouse45/understanding-grpc-a-practical-application-in-go-and-python-f3003c9158ef)

This repo contains code for my blog post explaining how to use gRPC in Go and Python. Do check it out.

### License:

The code in this repo is released under the terms of MIT License

# How to run

Terminal 1 (python server):
```
brew install python
pip3 install virtualenv
virtualenv -p python3 venv
pip install -r requirements.txt
source venv/bin/activate
python python/server.py
```

Terminal 2 (Go client):
```
cd golang
go get google.golang.org/protobuf
go run client.go
```
