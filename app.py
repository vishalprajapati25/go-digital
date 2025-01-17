import boto3
import os
import pymysql
from uuid import uuid4

def lambda_handler(event, context):
    # Debugging: Print the incoming event
    print(f"Received event: {event}")

    # Validate 'Records' key in the event
    if 'Records' not in event:
        print("No 'Records' key found in the event")
        return {
            'statusCode': 400,
            'body': "Invalid event format: 'Records' key missing."
        }

    # Get RDS connection details from environment variables
    rds_host = os.environ.get('RDS_HOST')
    rds_user = os.environ.get('RDS_USER')
    rds_password = os.environ.get('RDS_PASSWORD')
    rds_db_name = os.environ.get('RDS_DB_NAME')

    # Establish connection to the RDS database
    try:
        conn = pymysql.connect(
            host=rds_host,
            user=rds_user,
            password=rds_password,
            database=rds_db_name,
            connect_timeout=10
        )
        print("Successfully connected to RDS")
    except pymysql.MySQLError as e:
        print(f"Error connecting to RDS: {e}")
        return {
            'statusCode': 500,
            'body': "Failed to connect to RDS."
        }

    # Process each record in the event
    with conn.cursor() as cursor:
        for record in event['Records']:
            try:
                # Extract required fields
                bucket_name = record['s3']['bucket']['name']
                object_key = record['s3']['object']['key']
                size = record['s3']['object'].get('size', 0)
                event_name = record['eventName']
                event_time = record['eventTime']

                # Prepare SQL query
                insert_query = """
                    INSERT INTO my_table (id, bucket_name, object_key, size, event_name, event_time)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                record_id = str(uuid4())
                query_params = (record_id, bucket_name, object_key, size, event_name, event_time)

                # Execute the query
                cursor.execute(insert_query, query_params)
                print(f"Successfully inserted: {object_key}")

            except Exception as e:
                print(f"Error processing record: {e}")
                continue

        # Commit the transaction
        conn.commit()

    # Close the connection
    conn.close()

    return {
        'statusCode': 200,
        'body': "Processing complete."
    }
