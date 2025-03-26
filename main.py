from fastapi import FastAPI, File, UploadFile
import boto3
from botocore.client import Config
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# DigitalOcean Spaces config
DO_SPACES_KEY = os.getenv("DO_SPACES_KEY")
DO_SPACES_SECRET = os.getenv("DO_SPACES_SECRET")
DO_SPACES_REGION = os.getenv("DO_SPACES_REGION")
DO_SPACES_BUCKET = os.getenv("DO_SPACES_BUCKET")
DO_SPACES_ENDPOINT = f"https://{DO_SPACES_REGION}.digitaloceanspaces.com"

# Set up boto3 client
s3 = boto3.client(
    's3',
    region_name=DO_SPACES_REGION,
    endpoint_url=DO_SPACES_ENDPOINT,
    aws_access_key_id=DO_SPACES_KEY,
    aws_secret_access_key=DO_SPACES_SECRET,
    config=Config(signature_version='s3v4')
)

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    # Generate unique filename
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"

    # Read file contents
    file_content = await file.read()

    # Upload to DigitalOcean Spaces
    s3.put_object(
        Bucket=DO_SPACES_BUCKET,
        Key=unique_filename,
        Body=file_content,
        ACL='public-read',  # so the file is accessible publicly
        ContentType=file.content_type
    )

    # Construct URL
    image_url = f"https://{DO_SPACES_BUCKET}.{DO_SPACES_REGION}.cdn.digitaloceanspaces.com/{unique_filename}"

    # Print to terminal
    print(f"Uploaded image URL: {image_url}")

    # Return URL (optional)
    return {"url": image_url}
