terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
provider "aws" {
  region = "ap-south-1"
 # access_key = <provide key>
  #secret_key = <provide key>

}
resource "aws_s3_bucket" "data_bucket" {
  bucket = var.bucketname
}

variable "bucketname" {
# add a random bucket name 
default = "dfisfisdfdddhfid"
}
resource "aws_db_instance" "db_instance" {
  identifier              = "my-db-instance"
  allocated_storage       = 10
  engine                  = "mysql"
  engine_version          = "8.0"
  instance_class          = "db.t3.micro"
  db_name                 = "mydatabase"
  username                = "admin"
  password                = "password123"
  publicly_accessible     = true
  skip_final_snapshot     = true
}

resource "aws_glue_catalog_database" "glue_database" {
  name = "my-glue-database"
}

resource "aws_iam_role" "lambda_exec_role" {
  name = "lambda_exec_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_exec_policy" {
  name = "lambda_exec_policy"
  role = aws_iam_role.lambda_exec_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:*",
          "rds:*",
          "glue:*",
          "logs:*"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_lambda_function" "lambda_function" {
  function_name    = "data_processor"
  role             = aws_iam_role.lambda_exec_role.arn
  package_type     = "Image" # Specify that this Lambda uses a container image
  image_uri        = 794038231266.dkr.ecr.ap-south-1.amazonaws.com/jenkins/mylambda:latest # Reference your ECR image URI  environment {
    variables = {
      S3_BUCKET     = aws_s3_bucket.data_bucket.bucket
      RDS_ENDPOINT  = aws_db_instance.db_instance.endpoint
      DB_NAME       = aws_db_instance.db_instance.db_name
      DB_USER       = aws_db_instance.db_instance.username
      DB_PASSWORD   = aws_db_instance.db_instance.password
      GLUE_DATABASE = aws_glue_catalog_database.glue_database.name
    }
  }
}

