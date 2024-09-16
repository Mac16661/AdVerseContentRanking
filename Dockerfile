# Stage 1
FROM python:3.10.10 as runner

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

EXPOSE 5000

CMD [ "python", "./app.py" ]












