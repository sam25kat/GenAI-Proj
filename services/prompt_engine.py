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

    def process_user_message(self, user_id: int, message: str, conversation_id: Optional[int] = None) -> Dict:
        """
        Main processing pipeline for user messages
        Returns: Dict with enhanced_prompt, response, metadata
        """
        try:
            # If no conversation_id provided, create a new conversation
            if conversation_id is None:
                conversation_id = self.db.create_conversation(user_id)
                if not conversation_id:
                    raise Exception("Failed to create conversation")
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
                conversation_id=conversation_id,
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
                conversation_id=conversation_id,
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
                "conversation_id": conversation_id,
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

        # Check for custom instructions first
        custom_instructions = user_preferences.get('custom_instructions', '').strip()

        if custom_instructions:
            # Use custom instructions if provided
            instructions.append(custom_instructions)
        else:
            # Fall back to default instructions based on preferences
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
            elif tone == "casual":
                instructions.append("Use a relaxed, conversational tone")

            if intent == "learning":
                instructions.append("Focus on educational value and understanding")
            elif intent == "problem_solving":
                instructions.append("Provide actionable solutions and steps")
            elif intent == "creative":
                instructions.append("Be creative and offer diverse ideas")

        prompt_parts.append(f"[Instructions: {'. '.join(instructions)}]")

        # Enhance/refine the user query
        refined_query = self.refine_user_query(user_message, domain, intent)

        # Show both original and refined if they differ significantly
        if refined_query.lower() != user_message.lower():
            prompt_parts.append(f"\nOriginal Query: {user_message}")
            prompt_parts.append(f"Refined Query: {refined_query}")
        else:
            prompt_parts.append(f"\nUser Query: {user_message}")

        # Combine all parts
        enhanced_prompt = "\n".join(prompt_parts)

        return enhanced_prompt

    def refine_user_query(self, user_message: str, domain: str, intent: str) -> str:
        """
        Refine and enhance the user's query by:
        - Correcting spelling errors
        - Making the query more specific and clear
        - Adding relevant context based on domain/intent
        """
        try:
            # Use GPT to refine the query
            refinement_prompt = f"""You are a query refinement assistant. Your job is to improve user queries by:
1. Correcting any spelling or grammar errors
2. Making vague questions more specific
3. Adding relevant context when needed
4. Keeping the core intent intact

Domain: {domain}
Intent: {intent}
Original Query: {user_message}

Provide ONLY the refined query, nothing else. If the query is already clear and has no errors, return it as-is."""

            refined = self.openai.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a query refinement expert."},
                    {"role": "user", "content": refinement_prompt}
                ],
                temperature=0.3,
                max_tokens=150
            )

            refined_query = refined.choices[0].message.content.strip()

            # If refinement failed or is too different, return original
            if not refined_query or len(refined_query) > len(user_message) * 2:
                return user_message

            return refined_query

        except Exception as e:
            logger.error(f"Error refining query: {e}")
            # Fall back to original message if refinement fails
            return user_message

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
