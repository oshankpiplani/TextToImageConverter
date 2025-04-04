import boto3
from config import Config
from io import BytesIO
from PIL import Image
import logging

logger = logging.getLogger(__name__)

s3_client = boto3.client(
    's3',
    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
    region_name=Config.AWS_REGION
)

def upload_image_to_s3(image, prompt):
    try:
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        filename = f"generated_images/{prompt[:50].replace(' ', '_')}.png"
        
        s3_client.put_object(
            Bucket=Config.S3_BUCKET_NAME,
            Key=filename,
            Body=img_byte_arr,
            ContentType='image/png'
        )
        
        # Generate pre-signed URL
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': Config.S3_BUCKET_NAME, 'Key': filename},
            ExpiresIn=3600
        )
        
        return url
        
    except Exception as e:
        logger.error(f"S3 Upload Error: {str(e)}")
        raise