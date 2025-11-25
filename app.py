from flask import Flask, render_template, jsonify
from flask_cors import CORS
from routes.chat import chat_bp
from routes.history import history_bp
from config import Config
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('promptsense.log')
    ]
)

logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS
CORS(app)

# Register blueprints
app.register_blueprint(chat_bp)
app.register_blueprint(history_bp)


@app.route('/')
def index():
    """Serve the main chat interface"""
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "PromptSense",
        "version": "1.0.0"
    }), 200


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get client-safe configuration"""
    return jsonify({
        "embedding_model": Config.EMBEDDING_MODEL,
        "llm_model": Config.LLM_MODEL,
        "similar_queries_limit": Config.SIMILAR_QUERIES_LIMIT
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


if __name__ == '__main__':
    logger.info("Starting PromptSense server...")

    # Validate configuration
    if not Config.OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY not set. Please configure it in .env file")

    if not Config.DATABASE_URL:
        logger.warning("DATABASE_URL not set. Please configure it in .env file")

    # Run the app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=Config.FLASK_DEBUG
    )
