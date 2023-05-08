FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

WORKDIR /root
COPY requirements.txt /root/
RUN pip install -r requirements.txt

COPY c1_BoW_Sentiment_Model.pkl /root/
COPY c2_Classifier_Sentiment_Model /root/
COPY main.py /root/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
