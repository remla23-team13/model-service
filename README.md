# model-service
This repository contains the wrapper code for a machine learning model that performs sentiment analysis on restaurants review. 
The service is built using [fastAPI](https://fastapi.tiangolo.com/).
For the full project see the [operation repository](https://github.com/remla23-team13/operation).

## Running the service
[Docker](https://www.docker.com/) is required to run the service. 
First, build the docker image, then run the container forwarding the docker container port to that of your localhost.
```bash
docker build -t model-service .
docker run -p 8000:8000 model-service
```
The service will be available at `http://localhost:8000` to be queried.
To test if the service is working properly run the following command:
```bash
curl -X 'POST' \
  'http://localhost:8000/predict/1' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "data": "A great touch!"
}'
```
This command will query the model-service to return a sentiment of the review "A great touch!".
It sends a POST request to the specified URL with the expected headers and some appropriate data.
If everything is working properly, you should get `{"prediction":"Positive"}` as a response.

## Experimenting with the service
FastAPI generates automatically an OpenAPI specification for the available endpoints. 
The exposed APIs can be tested using the [Swagger UI](https://swagger.io/tools/swagger-ui/) at `http://localhost:8000/docs`.

## Tracked Metrics
You can inspect these metrics using either the Grafana dashboard or Prometheus dashboard, see the [operation repository](https://github.com/remla23-team13/operation) for more details.
* num_requests - The number of requests that have been served
* positive_prediction_ratio - Ratio of positive predictions over all predictions (per version of the webapp)
* wrong_prediction_ratio - Ratio of wrong predictions over all predictions (per version of the webapp)
* review_size - A histogram of the review sizes (characters)
* prediction_time - A summary of the time it takes to process the input and do a prediction
