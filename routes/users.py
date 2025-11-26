from flask import Blueprint, request, jsonify
from services.db_service import DatabaseService
import logging

logger = logging.getLogger(__name__)

users_bp = Blueprint('users', __name__)
db_service = DatabaseService()


@users_bp.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user information and preferences"""
    try:
        user = db_service.get_user(user_id)

        if user:
            return jsonify({
                "success": True,
                "user": user
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404

    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@users_bp.route('/api/users/<int:user_id>/preferences', methods=['PUT'])
def update_preferences(user_id):
    """Update user preferences"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400

        # Validate preferences
        preferences = {}

        if 'expertise_level' in data:
            if data['expertise_level'] not in ['beginner', 'intermediate', 'advanced']:
                return jsonify({
                    "success": False,
                    "error": "Invalid expertise level"
                }), 400
            preferences['expertise_level'] = data['expertise_level']

        if 'tone' in data:
            if data['tone'] not in ['friendly', 'professional', 'casual']:
                return jsonify({
                    "success": False,
                    "error": "Invalid tone"
                }), 400
            preferences['tone'] = data['tone']

        if 'custom_instructions' in data:
            preferences['custom_instructions'] = data['custom_instructions']

        if 'preferred_domains' in data:
            preferences['preferred_domains'] = data['preferred_domains']

        # Get current preferences and merge
        user = db_service.get_user(user_id)
        if not user:
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404

        current_prefs = user.get('preferences', {})
        current_prefs.update(preferences)

        # Update in database
        success = db_service.update_user_preferences(user_id, current_prefs)

        if success:
            return jsonify({
                "success": True,
                "preferences": current_prefs
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Failed to update preferences"
            }), 500

    except Exception as e:
        logger.error(f"Error updating preferences: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500
