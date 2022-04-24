# pytago

## onlone

- https://pytago.dev/

https://pypi.org/project/pytago/

### Web application

#### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)

#### Installation

```
git clone https://github.com/nottheswimmer/pytago/
cd pytago
docker build -t pytago .
```

#### Usage

```
docker run -p 8080:8080 -e PORT=8080 -it pytago

# User interface
open http://127.0.0.1:8080/

# API
curl --request POST 'http://127.0.0.1:8080/' \
  --header 'Content-Type: application/json'  \
  --data-raw '{"py": "print(\"Hello World\")"}'
```