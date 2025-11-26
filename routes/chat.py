from flask import Blueprint, request, jsonify
from services.prompt_engine import PromptEngine
import logging

logger = logging.getLogger(__name__)

chat_bp = Blueprint('chat', __name__)
prompt_engine = PromptEngine()


@chat_bp.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    try:
        data = request.get_json()

        # Validate input
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": "Message is required"
            }), 400

        message = data['message']
        user_id = data.get('user_id', 1)  # Default to demo user
        conversation_id = data.get('conversation_id')  # Optional conversation ID

        # Validate message
        if not message or not message.strip():
            return jsonify({
                "success": False,
                "error": "Message cannot be empty"
            }), 400

        # Process message through prompt engine
        result = prompt_engine.process_user_message(user_id, message, conversation_id)

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@chat_bp.route('/api/chat/insights/<int:user_id>', methods=['GET'])
def get_insights(user_id):
    """Get user insights and analytics"""
    try:
        insights = prompt_engine.get_user_insights(user_id)
        return jsonify({
            "success": True,
            "insights": insights
        }), 200

    except Exception as e:
        logger.error(f"Error getting insights: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@chat_bp.route('/api/chat/faiss-stats', methods=['GET'])
def faiss_stats():
    """Get FAISS index statistics"""
    try:
        stats = prompt_engine.faiss.get_index_stats()
        return jsonify({
            "success": True,
            "stats": stats
        }), 200

    except Exception as e:
        logger.error(f"Error getting FAISS stats: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500
