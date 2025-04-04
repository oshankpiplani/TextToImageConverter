import os
from dotenv import load_dotenv
import torch

load_dotenv()

class Config:
    # AWS Configuration
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '').strip()
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '').strip()
    AWS_REGION = os.getenv('AWS_REGION', 'ap-south-1').strip()
    S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', '').strip()
    
    # Model configuration
    MODEL_ID = "runwayml/stable-diffusion-v1-5"
    DEVICE = None

    @classmethod
    def get_device(cls):
        """Initialize and return the best available device"""
        if cls.DEVICE is None:
            if torch.backends.mps.is_available():
                cls.DEVICE = "mps"
                # Critical MPS fixes
                torch.mps.empty_cache()
                os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
            elif torch.cuda.is_available():
                cls.DEVICE = "cuda"
            else:
                cls.DEVICE = "cpu"
            print(f"Using device: {cls.DEVICE}")
        return cls.DEVICE

    @classmethod
    def get_torch_dtype(cls):
        """Force float32 for MPS to prevent black images"""
        return torch.float32  # Changed from float16 for MPS stability