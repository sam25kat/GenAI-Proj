from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from typing import List, Optional, Dict, Iterable
from config import Config
import logging
import json

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for OpenAI API interactions"""

    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.embedding_model = Config.EMBEDDING_MODEL
        self.llm_model = Config.LLM_MODEL

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding vector for text"""
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.embedding_model
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None

    def detect_intent(self, text: str) -> str:
        """Detect user intent from the message"""
        try:
            response = self.client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {
                        "role": "system",
                        "content": """Analyze the user message and classify the intent into ONE of these categories:
- learning: User wants to learn or understand something
- problem_solving: User needs help solving a specific problem
- creative: User wants to create, write, or generate something
- analysis: User wants analysis or insights on data/topic
- conversation: General conversation or chitchat
- clarification: User is asking for clarification

Respond with ONLY the category name, nothing else."""
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                temperature=0.3,
                max_tokens=20
            )
            content = response.choices[0].message.content
            if not content:
                return "conversation"
            intent = content.strip().lower()
            return intent
        except Exception as e:
            logger.error(f"Error detecting intent: {e}")
            return "conversation"

    def detect_domain(self, text: str) -> str:
        """Detect domain/topic from the message"""
        try:
            response = self.client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {
                        "role": "system",
                        "content": """Analyze the user message and classify it into ONE primary domain:
- technology: Programming, software, hardware, IT
- science: Physics, chemistry, biology, research
- business: Finance, marketing, management, entrepreneurship
- creative: Writing, art, design, music
- education: Learning, teaching, academic topics
- health: Medical, fitness, wellness
- travel: Tourism, geography, culture
- general: Everyday topics, chitchat

Respond with ONLY the domain name, nothing else."""
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                temperature=0.3,
                max_tokens=20
            )
            content = response.choices[0].message.content
            if not content:
                return "general"
            domain = content.strip().lower()
            return domain
        except Exception as e:
            logger.error(f"Error detecting domain: {e}")
            return "general"

    def generate_response(self, messages: Iterable[ChatCompletionMessageParam]) -> Optional[str]:
        """Generate LLM response given conversation messages"""
        try:
            response = self.client.chat.completions.create(
                model=self.llm_model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            content = response.choices[0].message.content
            if not content:
                return None
            return content
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return None

    def analyze_user_style(self, recent_messages: List[str]) -> Dict[str, str]:
        """Analyze user's communication style from recent messages"""
        if not recent_messages:
            return {"tone": "neutral", "complexity": "medium"}

        try:
            sample_text = "\n".join(recent_messages[-5:])
            response = self.client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {
                        "role": "system",
                        "content": """Analyze these user messages and determine:
1. Tone: formal, casual, friendly, or professional
2. Complexity preference: simple, medium, or advanced

Return ONLY a JSON object with 'tone' and 'complexity' keys."""
                    },
                    {
                        "role": "user",
                        "content": sample_text
                    }
                ],
                temperature=0.3,
                max_tokens=50
            )

            content = response.choices[0].message.content
            if not content:
                return {"tone": "neutral", "complexity": "medium"}
            result = json.loads(content)
            return result
        except Exception as e:
            logger.error(f"Error analyzing user style: {e}")
            return {"tone": "neutral", "complexity": "medium"}
