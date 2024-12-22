import boto3
import os
import sys
import logging
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ParamValidationError

logging.basicConfig(level=logging.INFO)

def read_data_from_s3(bucket_name, file_key):
    s3 = boto3.client('s3')
    try:
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        return response['Body'].read().decode('utf-8')
    except ParamValidationError as e:
        logging.error(f"Parameter validation error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error reading data from S3: {e}")
        sys.exit(1)

def push_data_to_rds(data, rds_endpoint, db_name, user, password):
    import psycopg2
    try:
        conn = psycopg2.connect(
            host=rds_endpoint,
            database=db_name,
            user=user,
            password=password
        )
        cursor = conn.cursor()
        cursor.execute("INSERT INTO my_table (data) VALUES (%s)", (data,))
        conn.commit()
        cursor.close()
        conn.close()
        logging.info("Data pushed to RDS successfully.")
    except Exception as e:
        logging.error(f"Error pushing data to RDS: {e}")
        return False
    return True

def push_data_to_glue(data, glue_database, glue_table):
    glue_client = boto3.client('glue')
    try:
        glue_client.put_record(
            DatabaseName=glue_database,
            TableName=glue_table,
            Record={"data": data}
        )
        logging.info("Data pushed to Glue successfully.")
    except Exception as e:
        logging.error(f"Error pushing data to Glue: {e}")
        sys.exit(1)

if __name__ == "__main__":
    BUCKET_NAME = os.getenv("S3_BUCKET")
    FILE_KEY = os.getenv("S3_KEY")
    RDS_ENDPOINT = os.getenv("RDS_ENDPOINT")
    DB_NAME = os.getenv("DB_NAME")
    USER = os.getenv("DB_USER")
    PASSWORD = os.getenv("DB_PASSWORD")
    GLUE_DATABASE = os.getenv("GLUE_DATABASE")
    GLUE_TABLE = os.getenv("GLUE_TABLE")

    if not FILE_KEY:
        logging.error("S3_KEY environment variable is not set or is empty")
        sys.exit(1)

    logging.info(f"Reading data from S3 bucket: {BUCKET_NAME}, key: {FILE_KEY}")
    data = read_data_from_s3(BUCKET_NAME, FILE_KEY)

    if not push_data_to_rds(data, RDS_ENDPOINT, DB_NAME, USER, PASSWORD):
        push_data_to_glue(data, GLUE_DATABASE, GLUE_TABLE)
