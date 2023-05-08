from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import joblib
import pickle

cvFile='c1_BoW_Sentiment_Model.pkl'
cv = pickle.load(open(cvFile, "rb"))
model = joblib.load('c2_Classifier_Sentiment_Model')


class InputText(BaseModel):
    data: str


app = FastAPI(swagger_ui_oauth2_redirect_url=None)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post('/predict')
async def predict(input_text: InputText):
    """
    Predicts the sentiment of a given text
    """
    data = input_text.data
    processed_input = cv.transform([data]).toarray()[0]
    prediction = model.predict([processed_input])[0]
    return {'prediction': "Positive" if prediction == 1 else "Negative"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

