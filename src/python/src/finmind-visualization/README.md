# finmind-visualization

# create services
    make create-network
    make mysql-up
    make rabbitmq-up
    make redash-up

# create finmind sync data api
### if your have token
    FINMIND_API_TOKEN=your_token make finmind-up

### if your have no token
    make finmind-up

# services

* mysql: http://localhost:8080/
    * user : finmind
    * password : test
* flower: http://localhost:5555/
* rabbitmq: http://localhost:15672/
    * user : worker
    * password : worker
* visualization: http://localhost:5000/
* finmind-visualization-api: http://localhost:8888/docs
