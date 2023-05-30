from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import joblib
import pickle
import os
import urllib.request
import gdown 
from input_form import InputText

gdown.download(os.getenv("MODEL_URL"), os.getenv("MODEL_FILE"), quiet=False)
gdown.download(os.getenv("PREPROCESSOR_URL"), os.getenv("PREPROCESSOR_FILE"), quiet=False)

model = joblib.load(os.getenv("MODEL_FILE"))
preprocessor = joblib.load(os.getenv("PREPROCESSOR_FILE"))

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
app.state.nWrongPredictions = 0
app.state.reviewSize50Counter = 0
app.state.reviewSize100Counter = 0
app.state.reviewSize150Counter = 0
app.state.reviewSize200Counter = 0
app.state.reviewSize250Counter = 0
app.state.reviewSizeInfCounter = 0
app.state.reviewSizeSum = 0

@app.post(os.getenv("MODEL_PATH") + '/predict')
async def predict(input_text: InputText):
    """
    Predicts the sentiment of a given text
    """
    app.state.nPredictions += 1
    data = input_text.data
    processed_input = preprocessor.transform([data]).toarray()[0]
    prediction = model.predict([processed_input])[0]

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

@app.post(os.getenv("MODEL_PATH") + '/wrong')
async def wrong():
    """
    Increments the wrong prediction counter
    """
    app.state.nWrongPredictions += 1

@app.get('/metrics')
async def metrics():
    """
    Enables monitoring with Prometheus
    """

    global countIdx, countSub

    version = os.getenv("VERSION")

    m = "# HELP wrong_prediction_ratio Ratio of wrong predictions over all predictions.\n"
    m+= "# TYPE wrong_prediction_ratio gauge\n"
    m+= "wrong_prediction_ratio "
    
    if app.state.nPredictions == 0:
        m += "0\n\n"
    else:
        m += str(app.state.nWrongPredictions / app.state.nPredictions) + "\n\n"


    m+= "# HELP num_requests The number of requests that have been served.\n"
    m+= "# TYPE num_requests counter\n"
    m+= "num_requests{version=\"" + version + "\"} " + str(app.state.nPredictions) + "\n\n" # TODO get version 

    m+= "# HELP review_size A histogram of the review sizes (characters)\n"
    m+= "# TYPE review_size histogram\n"
    m+= "review_size_bucket{le=\"50\"}  " + str(app.state.reviewSize50Counter) + "\n"
    m+= "review_size_bucket{le=\"100\"} " + str(app.state.reviewSize100Counter) + "\n"
    m+= "review_size_bucket{le=\"150\"} " + str(app.state.reviewSize150Counter) + "\n"
    m+= "review_size_bucket{le=\"200\"} " + str(app.state.reviewSize200Counter) + "\n"
    m+= "review_size_bucket{le=\"250\"} " + str(app.state.reviewSize250Counter) + "\n"
    m+= "review_size_bucket{le=\"+Inf\"} " + str(app.state.reviewSizeInfCounter) + "\n"
    m+= "review_size_sum " + str(app.state.reviewSizeSum) + "\n"
    m+= "review_size_count " + str(app.state.nPredictions) + "\n\n"

    return Response(content=m, media_type="text/plain")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

