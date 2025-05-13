# Copyright (C) Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# lib/s3.py
import boto3
import base64
from io import BytesIO
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv
import logging
from botocore.exceptions import ClientError
from botocore.config import Config


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class S3Service:
    def __init__(self):
        self.bucket_name = os.getenv('FDP_S3_BUCKET')
        if not self.bucket_name:
            raise ValueError("FDP_S3_BUCKET environment variable is not set")

        # Initialize S3 client with config
        self.s3 = boto3.client('s3', 
            config=Config(
                retries = dict(
                    max_attempts = 3
                )
            )
        )
        
        # Cache the region
        self.region = self.s3.meta.region_name if hasattr(self.s3, 'meta') else 'us-east-1'

        # Ensure bucket exists
        self.ensure_bucket_exists()

    def ensure_bucket_exists(self) -> None:
        """
        Create the S3 bucket if it doesn't exist

        Raises:
            ClientError: If there's an error checking or creating the bucket
        """
        try:
            self.s3.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Bucket exists: {self.bucket_name}")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                try:
                    if self.region == 'us-east-1':
                        # Create bucket without LocationConstraint for us-east-1
                        self.s3.create_bucket(Bucket=self.bucket_name)
                    else:
                        # Create bucket with LocationConstraint for other regions
                        self.s3.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={
                                'LocationConstraint': self.region
                            }
                        )

                    # Set bucket encryption
                    self.s3.put_bucket_encryption(
                        Bucket=self.bucket_name,
                        ServerSideEncryptionConfiguration={
                            'Rules': [
                                {
                                    'ApplyServerSideEncryptionByDefault': {
                                        'SSEAlgorithm': 'AES256'
                                    }
                                }
                            ]
                        }
                    )

                    # Enable versioning
                    self.s3.put_bucket_versioning(
                        Bucket=self.bucket_name,
                        VersioningConfiguration={'Status': 'Enabled'}
                    )

                    logger.info(f"Created new bucket: {self.bucket_name} with encryption and versioning")
                except ClientError as create_error:
                    logger.error(f"Error creating bucket: {repr(create_error)}")
                    raise
            else:
                logger.error(f"Error checking bucket: {repr(e)}")
                raise

    def upload_base64_image(self, base64_string: str) -> str:
        """
        Upload a base64 encoded image to S3

        Args:
            base64_string: Base64 encoded image string

        Returns:
            str: The S3 file key of the uploaded image

        Raises:
            ValueError: If the base64 string is invalid
            ClientError: If there's an error uploading to S3
        """
        try:
            # Remove the base64 prefix if it exists
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]

            # Remove any whitespace
            base64_string = base64_string.strip()

            try:
                # Decode base64 string
                image_data = base64.b64decode(base64_string)
                logger.info("Successfully decoded base64 image data")
            except Exception as e:
                logger.error(f"Base64 decode error: {repr(e)}")
                raise ValueError("Invalid base64 image data")

            # Generate a unique file name with timestamp
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            file_name = f"documents/{timestamp}-{str(uuid.uuid4())}.jpg"

            try:
                # Upload to S3 with server-side encryption
                self.s3.upload_fileobj(
                    BytesIO(image_data),
                    self.bucket_name,
                    file_name,
                    ExtraArgs={
                        'ContentType': 'image/jpeg',
                        'ServerSideEncryption': 'AES256'
                    }
                )
                logger.info(f"Successfully uploaded file to S3: {file_name}")
                return file_name

            except ClientError as e:
                logger.error(f"S3 upload error: {repr(e)}")
                raise

        except Exception as e:
            logger.error(f"Error in upload_base64_image: {repr(e)}")
            raise

    def get_presigned_url(self, file_key: str, expiry: int = 3600) -> str:
        """
        Generate a presigned URL for an existing S3 object

        Args:
            file_key: The S3 object key
            expiry: URL expiration time in seconds (default: 1 hour)

        Returns:
            str: Presigned URL for the S3 object

        Raises:
            ValueError: If the file key is empty
            ClientError: If there's an error generating the URL
        """
        try:
            if not file_key:
                logger.error("File key is empty")
                raise ValueError("File key cannot be empty")

            logger.info(f"Generating presigned URL for file key: {repr(file_key)}")

            try:
                # Check if object exists before generating URL
                self.s3.head_object(Bucket=self.bucket_name, Key=file_key)

                presigned_url = self.s3.generate_presigned_url(
                    ClientMethod='get_object',
                    Params={
                        'Bucket': self.bucket_name,
                        'Key': file_key
                    },
                    ExpiresIn=expiry
                )

                logger.info(f"Successfully generated presigned URL for {repr(file_key)}")
                return presigned_url

            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    raise ValueError(f"File not found: {repr(file_key)}")
                logger.error(f"ClientError generating presigned URL: {repr(e)}")
                raise

        except Exception as e:
            logger.error(f"Error generating presigned URL: {repr(e)}")
            raise
