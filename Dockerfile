FROM python:3.9-slim

WORKDIR /usr/src/app

RUN pip install boto3 psycopg2-binary
RUN pip install pymysql

COPY . .

CMD ["python", "app.py"]

