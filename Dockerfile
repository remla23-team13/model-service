FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

WORKDIR /app
COPY . /app/
RUN pip install -r requirements.txt

EXPOSE 8000

ENV MODEL_URL="https://drive.google.com/uc?id=1Ykfy1Eq_k3jZgLjGuzt5QI5_1T6NYrDO&export=download"
ENV PREPROCESSOR_URL="https://drive.google.com/uc?id=1Ud_w0xAmpg6xfUX30DO6cGFSWX5hU3Qr&export=download"
ENV MODEL_PATH="/model-s-service"
ENV MODEL_FILE="model.joblib"
ENV PREPROCESSOR_FILE="preprocessor.joblib"
ENV VERSION=${version}

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
