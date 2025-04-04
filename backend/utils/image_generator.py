from diffusers import StableDiffusionPipeline
import torch
from config import Config

_pipeline = None

def initialize_pipeline():
    global _pipeline
    if _pipeline is None:
        print("Initializing pipeline with MPS fixes...")
        device = Config.get_device()
        
        _pipeline = StableDiffusionPipeline.from_pretrained(
            Config.MODEL_ID,
            torch_dtype=Config.get_torch_dtype(),  # Now using float32
            use_safetensors=True,
            safety_checker=None,
            requires_safety_checker=False
        ).to(device)
        
        # Disable attention slicing for MPS
        if device == "mps":
            _pipeline.enable_attention_slicing(slice_size="max")
        
        # Warmup with explicit float32
        if device == "mps":
            print("Running MPS warmup...")
            with torch.no_grad():
                _pipeline("warmup", 
                         num_inference_steps=1,
                         height=256,
                         width=256,
                         guidance_scale=0)  # Disable CFG for warmup

def generate_image_from_text(prompt):
    try:
        initialize_pipeline()
        
        generator = torch.Generator(Config.get_device()).manual_seed(42)
        
        print(f"Generating image for: {prompt}")
        with torch.no_grad():
            image = _pipeline(
                prompt=prompt,
                negative_prompt="blurry, low quality, black background, dark",
                num_inference_steps=25,
                guidance_scale=7.5,
                width=512,
                height=512,
                generator=generator
            ).images[0]
        
        # Verify image isn't black
        if image.getextrema()[0] == (0, 0) and image.getextrema()[1] == (0, 0):
            raise ValueError("Generated black image - VAE decoding failed")
        
        return image
    
    except Exception as e:
        print(f"Generation error: {str(e)}")
        raise