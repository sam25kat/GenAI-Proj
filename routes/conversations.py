from flask import Blueprint, request, jsonify
from services.db_service import DatabaseService
from services.openai_service import OpenAIService
import logging

logger = logging.getLogger(__name__)

conversations_bp = Blueprint('conversations', __name__)
db_service = DatabaseService()
openai_service = OpenAIService()


@conversations_bp.route('/api/conversations/new', methods=['POST'])
def create_conversation():
    """Create a new conversation"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 1)
        title = data.get('title', 'New Conversation')

        conversation_id = db_service.create_conversation(user_id, title)

        if conversation_id:
            return jsonify({
                "success": True,
                "conversation_id": conversation_id,
                "title": title
            }), 201
        else:
            return jsonify({
                "success": False,
                "error": "Failed to create conversation"
            }), 500

    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@conversations_bp.route('/api/conversations/<int:user_id>', methods=['GET'])
def get_conversations(user_id):
    """Get all conversations for a user"""
    try:
        conversations = db_service.get_user_conversations(user_id)

        return jsonify({
            "success": True,
            "conversations": conversations
        }), 200

    except Exception as e:
        logger.error(f"Error fetching conversations: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@conversations_bp.route('/api/conversations/<int:conversation_id>/messages', methods=['GET'])
def get_conversation_messages(conversation_id):
    """Get all messages in a conversation"""
    try:
        messages = db_service.get_conversation_messages(conversation_id)

        return jsonify({
            "success": True,
            "messages": messages,
            "count": len(messages)
        }), 200

    except Exception as e:
        logger.error(f"Error fetching conversation messages: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@conversations_bp.route('/api/conversations/<int:conversation_id>/title', methods=['PUT'])
def update_conversation_title(conversation_id):
    """Update conversation title"""
    try:
        data = request.get_json()
        title = data.get('title')

        if not title or not title.strip():
            return jsonify({
                "success": False,
                "error": "Title is required"
            }), 400

        success = db_service.update_conversation_title(conversation_id, title)

        if success:
            return jsonify({
                "success": True,
                "conversation_id": conversation_id,
                "title": title
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Failed to update title"
            }), 500

    except Exception as e:
        logger.error(f"Error updating conversation title: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@conversations_bp.route('/api/conversations/<int:conversation_id>/generate-title', methods=['POST'])
def generate_conversation_title(conversation_id):
    """Auto-generate a title for the conversation based on its messages"""
    try:
        # Get first few messages
        messages = db_service.get_conversation_messages(conversation_id)

        if not messages:
            return jsonify({
                "success": False,
                "error": "No messages found in conversation"
            }), 404

        # Get first user message
        first_user_message = next((m for m in messages if m['role'] == 'user'), None)

        if not first_user_message:
            return jsonify({
                "success": False,
                "error": "No user messages found"
            }), 404

        # Generate title using OpenAI
        try:
            response = openai_service.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Generate a short, concise title (3-6 words max) for a conversation based on the first message. Return ONLY the title, nothing else."
                    },
                    {
                        "role": "user",
                        "content": first_user_message['content']
                    }
                ],
                temperature=0.7,
                max_tokens=20
            )
            content = response.choices[0].message.content
            if content:
                title = content.strip().strip('"\'')
            else:
                title = first_user_message['content'][:50] + ('...' if len(first_user_message['content']) > 50 else '')
        except:
            # Fallback: use first 50 chars of message
            title = first_user_message['content'][:50] + ('...' if len(first_user_message['content']) > 50 else '')

        # Update the conversation title
        success = db_service.update_conversation_title(conversation_id, title)

        if success:
            return jsonify({
                "success": True,
                "conversation_id": conversation_id,
                "title": title
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Failed to update title"
            }), 500

    except Exception as e:
        logger.error(f"Error generating conversation title: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@conversations_bp.route('/api/conversations/<int:conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """Delete a conversation"""
    try:
        success = db_service.delete_conversation(conversation_id)

        if success:
            return jsonify({
                "success": True,
                "message": "Conversation deleted"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Failed to delete conversation"
            }), 500

    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500
