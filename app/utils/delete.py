"""
Utility functions for managing image deletion locally and on AWS S3.
"""
import os
import logging

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")
S3_BUCKET_LINK = os.getenv("AWS_S3_BUCKET_LINK")
s3_folder = os.getenv("AWS_S3_FOLDER")



def delete_local_image(path: str) -> None:
    """Delete an image file from the local filesystem."""
    try:
        os.remove(path)
    except Exception as e:
        logger.warning(f"Failed to delete local image: {e}")


def delete_s3_image(s3_url: str) -> None:
    """Delete an image from S3 given its public URL."""
    s3 = boto3.client('s3')

    try:
        key = s3_url.split(f"{S3_BUCKET_LINK}")[1]
        if not key:
            logger.error(f"Could not extract key from URL: {s3_url}")
            return
        
        logger.info(f"Attempting to delete key: {key} from bucket: {S3_BUCKET_NAME}")
        s3.delete_object(Bucket=S3_BUCKET_NAME, Key=key)
        logger.info(f"Successfully deleted {s3_url}!")

        # Confirm deletion
        s3.head_object(Bucket=S3_BUCKET_NAME, Key=key)
        logger.warning("File still exists after delete attempt!")
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            logger.info("File is confirmed deleted.")
        else:
            logger.error(f"Error checking for deleted file: {e}")
    except Exception as e:
        logger.error(f"Failed to delete from S3: {e}")