from fastapi import FastAPI, Response, Request
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import joblib
import os
import gdown
import restaurant_db
import time
from input_form import InputText
from remlalib.preprocess import Preprocess
from urllib.request import urlopen

preprocessor = Preprocess()
preprocessor.load_from_url(os.getenv("PREPROCESSOR_URL"))

model = None
with (urlopen(os.getenv("MODEL_URL"))) as file:
    model = joblib.load(file)

app = FastAPI(swagger_ui_oauth2_redirect_url=None)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.nPredictions = 0
app.state.nPredictions_v1 = 0
app.state.nPredictions_v2 = 0

app.state.nWrongPredictions = 0
app.state.nWrongPredictions_v1 = 0
app.state.nWrongPredictions_v2 = 0

app.state.nPositivePredictions = 0
app.state.nPositivePredictions_v1 = 0
app.state.nPositivePredictions_v2 = 0

app.state.reviewSize50Counter = 0
app.state.reviewSize100Counter = 0
app.state.reviewSize150Counter = 0
app.state.reviewSize200Counter = 0
app.state.reviewSize250Counter = 0
app.state.reviewSizeInfCounter = 0
app.state.reviewSizeSum = 0
app.state.predictionTimeSum = 0
app.state.predictionTimeCount = 0
app.state.predictionTime1MicroSecond = 0
app.state.predictionTime10MicroSecond = 0
app.state.predictionTime100MicroSecond = 0
app.state.predictionTime1000MicroSecond = 0
app.state.predictionTime10000MicroSecond = 0


@app.get('/restaurants')
async def restaurants():
    """
    Returns a list of restaurants
    """
    # return the list as json
    restaurants = restaurant_db.get_restaurants()
    return restaurants


@app.get('/reviews/{restaurant_id}')
async def reviews(restaurant_id: int):
    """
    Returns a list of reviews for a given restaurant
    """
    # return the list as json
    reviews = restaurant_db.get_reviews(restaurant_id)
    return reviews


@app.get('/restaurant/{restaurant_id}')
async def restaurant(restaurant_id: int):
    restaurant = restaurant_db.get_restaurant(restaurant_id)
    return restaurant


@app.post('/predict/{restaurant_id}')
async def predict(input_text: InputText, restaurant_id: int, request: Request):
    """
    Predicts the sentiment of a given text
    """

    cookies = request.cookies
    app_version_cookie = cookies.get("AppVersion")

    if app_version_cookie == "v1":
        app.state.nPredictions_v1 += 1
    elif app_version_cookie == "v2":
        app.state.nPredictions_v2 += 1
    
    app.state.nPredictions += 1
    
    before = time.time()
    data = input_text.data
    processed_input = preprocessor.preprocess_sample(data)
    prediction = model.predict([processed_input])[0]
    after = time.time()
    prediction_time = before - after

    restaurant_db.insert_review(restaurant_id, data)

    app.state.predictionTimeCount += 1
    if prediction_time <= 0.000001:
        app.state.predictionTime1MicroSecond += 1
    elif size <= 0.00001:
        app.state.predictionTime10MicroSecond += 1
    elif size <= 0.0001:
        app.state.predictionTime100MicroSecond += 1
    elif prediction_time <= 0.001:
        app.state.predictionTime1000MicroSecond += 1
    else:
        app.state.predictionTime10000MicroSecond += 1
    app.state.predictionTimeSum += prediction_time
    
    if (prediction == 1):
        if app_version_cookie == "v1":
            app.state.nPositivePredictions_v1 += 1
        elif app_version_cookie == "v2":
            app.state.nPositivePredictions_v2 += 1
        
        app.state.nPositivePredictions += 1

    size = len(data)
    if size <= 50:
        app.state.reviewSize50Counter += 1
    elif size <= 100:
        app.state.reviewSize100Counter += 1
    elif size <= 150:
        app.state.reviewSize150Counter += 1
    elif size <= 200:
        app.state.reviewSize200Counter += 1
    elif size <= 250:
        app.state.reviewSize250Counter += 1
    else:
        app.state.reviewSizeInfCounter += 1
    app.state.reviewSizeSum += size

    return {'prediction': "Positive" if prediction == 1 else "Negative"}


@app.post('/wrong')
async def wrong(request: Request):
    """
    Increments the wrong prediction counter
    """

    cookies = request.cookies
    app_version_cookie = cookies.get("AppVersion")

    if app_version_cookie == "v1":
        app.state.nWrongPredictions_v1 += 1
    elif app_version_cookie == "v2":
        app.state.nWrongPredictions_v2 += 1
    
    app.state.nWrongPredictions += 1


@app.get('/metrics')
async def metrics():
    """
    Enables monitoring with Prometheus
    """

    global countIdx, countSub

    version = os.getenv("VERSION")

    m = "# HELP wrong_prediction_ratio Ratio of wrong predictions over all predictions.\n"
    m += "# TYPE wrong_prediction_ratio gauge\n"
    m += "wrong_prediction_ratio "

    if app.state.nPredictions == 0:
        m += "0\n"
    else:
        m += str(app.state.nWrongPredictions / app.state.nPredictions) + "\n"

    m+= "wrong_prediction_ratio{webapp=\"v1\"} "

    if app.state.nPredictions_v1 == 0:
        m += "0\n"
    else:
        m += str(app.state.nWrongPredictions_v1 / app.state.nPredictions_v1) + "\n"

    m+= "wrong_prediction_ratio{webapp=\"v2\"} "

    if app.state.nPredictions_v2 == 0:
        m += "0\n\n"
    else:
        m += str(app.state.nWrongPredictions_v2 / app.state.nPredictions_v2) + "\n\n"


    m+= "# HELP positive_prediction_ratio Ratio of positive predictions over all predictions.\n"
    m+= "# TYPE positive_prediction_ratio gauge\n"
    m+= "positive_prediction_ratio "
    
    if app.state.nPredictions == 0:
        m += "0\n"
    else:
        m += str(app.state.nPositivePredictions / app.state.nPredictions) + "\n"

    m+= "positive_prediction_ratio{webapp=\"v1\"} "

    if app.state.nPredictions_v1 == 0:
        m += "0\n"
    else:
        m += str(app.state.nPositivePredictions_v1 / app.state.nPredictions_v1) + "\n"

    m+= "positive_prediction_ratio{webapp=\"v2\"} "

    if app.state.nPredictions_v2 == 0:
        m += "0\n\n"
    else:
        m += str(app.state.nPositivePredictions_v2 / app.state.nPredictions_v2) + "\n\n"

    m += "# HELP num_requests The number of requests that have been served.\n"
    m += "# TYPE num_requests counter\n"
    m += "num_requests{version=\"" + version + "\"} " + \
        str(app.state.nPredictions) + "\n\n"  # TODO get version

    m += "# HELP review_size A histogram of the review sizes (characters)\n"
    m += "# TYPE review_size histogram\n"
    m += "review_size_bucket{le=\"50\"}  " + \
        str(app.state.reviewSize50Counter) + "\n"
    m += "review_size_bucket{le=\"100\"} " + \
        str(app.state.reviewSize100Counter) + "\n"
    m += "review_size_bucket{le=\"150\"} " + \
        str(app.state.reviewSize150Counter) + "\n"
    m += "review_size_bucket{le=\"200\"} " + \
        str(app.state.reviewSize200Counter) + "\n"
    m += "review_size_bucket{le=\"250\"} " + \
        str(app.state.reviewSize250Counter) + "\n"
    m += "review_size_bucket{le=\"+Inf\"} " + \
        str(app.state.reviewSizeInfCounter) + "\n"
    m += "review_size_sum " + str(app.state.reviewSizeSum) + "\n"
    m += "review_size_count " + str(app.state.nPredictions) + "\n\n"

    m += "# HELP prediction_time A summary of the time it takes to process the input and do a prediction\n"
    m += "# TYPE prediction_time summary\n"
    m += "prediction_time{quantile=\"0.00001\"}  " + \
        str(app.state.predictionTime1MicroSecond) + "\n"
    m += "prediction_time{quantile=\"0.0001\"} " + \
        str(app.state.predictionTime10MicroSecond) + "\n"
    m += "prediction_time{quantile=\"0.001\"} " + \
        str(app.state.predictionTime100MicroSecond) + "\n"
    m += "prediction_time{quantile=\"0.1\"} " + \
        str(app.state.predictionTime1000MicroSecond) + "\n"
    m += "prediction_time{quantile=\"1\"} " + \
        str(app.state.predictionTime10000MicroSecond) + "\n"
    m += "prediction_time_sum " + str(app.state.predictionTimeSum) + "\n"
    m += "prediction_time_count " + str(app.state.predictionTimeCount) + "\n\n"

    return Response(content=m, media_type="text/plain")


@app.get('/version')
async def health():
    """
    Returns the version of the model
    """
    return {'version': "2"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
