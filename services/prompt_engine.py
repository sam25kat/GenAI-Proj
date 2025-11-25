from typing import Dict, List, Optional
from services.db_service import DatabaseService
from services.openai_service import OpenAIService
from services.faiss_service import FAISSService
from config import Config
import logging

logger = logging.getLogger(__name__)


class PromptEngine:
    """Core engine for context-aware prompt personalization"""

    def __init__(self):
        self.db = DatabaseService()
        self.openai = OpenAIService()
        self.faiss = FAISSService()

    def process_user_message(self, user_id: int, message: str) -> Dict:
        """
        Main processing pipeline for user messages
        Returns: Dict with enhanced_prompt, response, metadata
        """
        try:
            # Step 1: Get user profile and preferences
            user = self.db.get_user(user_id)
            if not user:
                logger.warning(f"User {user_id} not found")
                user = {"preferences": {}}

            # Step 2: Detect intent and domain
            intent = self.openai.detect_intent(message)
            domain = self.openai.detect_domain(message)

            # Step 3: Get conversation history
            recent_context = self.db.get_recent_context(user_id, limit=5)

            # Step 4: Generate embedding and search similar queries
            embedding = self.openai.generate_embedding(message)
            similar_queries = []
            if embedding:
                similar_queries = self.faiss.search_similar(
                    embedding,
                    k=Config.SIMILAR_QUERIES_LIMIT,
                    user_id=user_id
                )

            # Step 5: Build personalized prompt
            enhanced_prompt = self.build_personalized_prompt(
                user_message=message,
                user_preferences=user.get('preferences', {}),
                intent=intent,
                domain=domain,
                recent_context=recent_context,
                similar_queries=similar_queries
            )

            # Step 6: Generate LLM response
            conversation_messages = self.prepare_conversation_messages(
                enhanced_prompt,
                recent_context
            )
            response = self.openai.generate_response(conversation_messages)

            # Step 7: Save to database
            user_msg_id = self.db.save_message(
                user_id=user_id,
                role="user",
                content=message,
                original_prompt=message,
                enhanced_prompt=enhanced_prompt,
                intent=intent,
                domain=domain,
                metadata={
                    "similar_queries_count": len(similar_queries)
                }
            )

            assistant_msg_id = self.db.save_message(
                user_id=user_id,
                role="assistant",
                content=response,
                intent=intent,
                domain=domain
            )

            # Step 8: Add to FAISS index (async in production)
            if embedding and user_msg_id:
                self.faiss.add_vector(
                    vector=embedding,
                    user_id=user_id,
                    message_id=user_msg_id,
                    text=message,
                    intent=intent,
                    domain=domain
                )
                self.db.mark_vector_saved(user_msg_id)

            return {
                "success": True,
                "response": response,
                "original_prompt": message,
                "enhanced_prompt": enhanced_prompt,
                "metadata": {
                    "intent": intent,
                    "domain": domain,
                    "similar_queries": similar_queries,
                    "context_used": len(recent_context) > 0
                }
            }

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "I encountered an error processing your request. Please try again."
            }

    def build_personalized_prompt(
        self,
        user_message: str,
        user_preferences: Dict,
        intent: str,
        domain: str,
        recent_context: List[Dict],
        similar_queries: List[Dict]
    ) -> str:
        """Build a personalized, context-rich prompt"""

        # Extract preferences
        tone = user_preferences.get('tone', 'professional')
        expertise_level = user_preferences.get('expertise_level', 'intermediate')
        preferred_domains = user_preferences.get('preferred_domains', [])

        # Build context sections
        prompt_parts = []

        # User profile context
        prompt_parts.append(f"[User Profile: {expertise_level} level, prefers {tone} tone]")

        # Domain and intent context
        prompt_parts.append(f"[Detected Domain: {domain}, Intent: {intent}]")

        # Similar past queries context
        if similar_queries:
            similar_texts = [q['text'] for q in similar_queries[:2]]
            prompt_parts.append(
                f"[User previously asked similar questions: {', '.join(similar_texts)}]"
            )

        # Recent conversation context
        if recent_context:
            recent_topics = [ctx.get('domain', 'general') for ctx in recent_context[-3:]]
            unique_topics = list(set(recent_topics))
            if unique_topics:
                prompt_parts.append(f"[Recent conversation topics: {', '.join(unique_topics)}]")

        # Personalization instructions
        instructions = []

        if expertise_level == "beginner":
            instructions.append("Explain concepts in simple terms with examples")
        elif expertise_level == "advanced":
            instructions.append("Provide detailed technical information")
        else:
            instructions.append("Balance detail with clarity")

        if tone == "friendly":
            instructions.append("Use a warm, approachable tone")
        elif tone == "professional":
            instructions.append("Maintain a professional, concise tone")

        if intent == "learning":
            instructions.append("Focus on educational value and understanding")
        elif intent == "problem_solving":
            instructions.append("Provide actionable solutions and steps")
        elif intent == "creative":
            instructions.append("Be creative and offer diverse ideas")

        prompt_parts.append(f"[Instructions: {'. '.join(instructions)}]")

        # Add the actual user message
        prompt_parts.append(f"\nUser Query: {user_message}")

        # Combine all parts
        enhanced_prompt = "\n".join(prompt_parts)

        return enhanced_prompt

    def prepare_conversation_messages(
        self,
        enhanced_prompt: str,
        recent_context: List[Dict]
    ) -> List[Dict[str, str]]:
        """Prepare messages array for OpenAI API"""

        messages = [
            {
                "role": "system",
                "content": "You are PromptSense, an intelligent assistant that provides personalized, context-aware responses. Pay attention to the user profile, intent, and context provided in the enhanced prompt."
            }
        ]

        # Add recent context (last 3 exchanges)
        for ctx in recent_context[-6:]:
            messages.append({
                "role": ctx['role'],
                "content": ctx['content']
            })

        # Add current enhanced prompt
        messages.append({
            "role": "user",
            "content": enhanced_prompt
        })

        return messages

    def get_user_insights(self, user_id: int) -> Dict:
        """Get insights about user's interaction patterns"""
        try:
            history = self.db.get_user_history(user_id, limit=50)
            domains = self.db.get_user_domains(user_id, limit=10)

            intents = {}
            for msg in history:
                if msg.get('intent'):
                    intents[msg['intent']] = intents.get(msg['intent'], 0) + 1

            return {
                "total_messages": len(history),
                "common_domains": domains,
                "common_intents": intents,
                "faiss_vectors": len(self.faiss.get_user_query_history(user_id))
            }
        except Exception as e:
            logger.error(f"Error getting user insights: {e}")
            return {}
