# model-service
This repository contains the wrapper code for a machine learning model that performs sentiment analysis on restaurants review. The service is built using [fastAPI](https://fastapi.tiangolo.com/).

## Running the service
[Docker](https://www.docker.com/) is required to run the service. First, build the docker image:
```
docker build -t model-service .
```
Then, run the container:
```
docker run -p 8000:8000 model-service
```
The service will be available at `http://localhost:8000` to be queried.
To test if the service is working properly run the following command:
```
curl -X 'POST' \
  'http://localhost:8000/predict/1' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "data": "A great touch!"
}'
```
if everything is working properly, you should get the following response:
```
{"prediction":"Positive"}
```

## Experimenting with the service
FastAPI generates automatically an OpenAPI specification for the available endpoints. The exposed APIs can be tested using the [Swagger UI](https://swagger.io/tools/swagger-ui/) at `http://localhost:8000/docs`.