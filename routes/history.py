from flask import Blueprint, request, jsonify
from services.db_service import DatabaseService
import logging

logger = logging.getLogger(__name__)

history_bp = Blueprint('history', __name__)
db_service = DatabaseService()


@history_bp.route('/api/history/<int:user_id>', methods=['GET'])
def get_history(user_id):
    """Get user's message history"""
    try:
        # Get pagination parameters
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)

        # Validate parameters
        if limit > 100:
            limit = 100
        if offset < 0:
            offset = 0

        # Fetch history
        messages = db_service.get_user_history(user_id, limit, offset)

        return jsonify({
            "success": True,
            "user_id": user_id,
            "messages": messages,
            "count": len(messages)
        }), 200

    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@history_bp.route('/api/history/<int:user_id>/recent', methods=['GET'])
def get_recent_context(user_id):
    """Get recent conversation context"""
    try:
        limit = request.args.get('limit', 5, type=int)
        context = db_service.get_recent_context(user_id, limit)

        return jsonify({
            "success": True,
            "user_id": user_id,
            "context": context
        }), 200

    except Exception as e:
        logger.error(f"Error fetching recent context: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@history_bp.route('/api/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user profile"""
    try:
        user = db_service.get_user(user_id)

        if not user:
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404

        return jsonify({
            "success": True,
            "user": user
        }), 200

    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@history_bp.route('/api/users', methods=['GET'])
def get_users():
    """Get all demo users"""
    try:
        with db_service.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, email, name, preferences FROM users ORDER BY id")
                users = cur.fetchall()

                user_list = []
                for user in users:
                    user_list.append({
                        "id": user[0],
                        "email": user[1],
                        "name": user[2],
                        "preferences": user[3]
                    })

                return jsonify({
                    "success": True,
                    "users": user_list
                }), 200

    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500
