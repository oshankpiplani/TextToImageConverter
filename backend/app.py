from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.image_generator import generate_image_from_text
from utils.s3_uploader import upload_image_to_s3
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/generate-image', methods=['POST'])
def generate_image():
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400

        data = request.get_json()
        prompt = data.get('prompt')
        
        if not prompt or not isinstance(prompt, str):
            return jsonify({'error': 'Valid prompt string is required'}), 400

        logger.info(f"Generating image for prompt: {prompt}")
        
        image = generate_image_from_text(prompt)
        image_url = upload_image_to_s3(image, prompt)
        
        return jsonify({
            'success': True,
            'image_url': image_url
        })

    except MemoryError as e:
        logger.error(f"Memory error: {str(e)}")
        return jsonify({
            'success': False,
            'error': "Image too large for available memory. Try a simpler prompt.",
            'retry_suggestion': {
                'steps': 10,
                'size': 256
            }
        }), 500
    except Exception as e:
        logger.error(f"Error in generate_image: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)