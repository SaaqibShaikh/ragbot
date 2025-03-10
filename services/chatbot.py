from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Optional
from supabase import create_client
from config import get_settings
import logging

logger = logging.getLogger(__name__)

class ChatbotService:
    def __init__(self):
        self.settings = get_settings()
        self.model = SentenceTransformer(self.settings.model_name)
        self.supabase = create_client(
            self.settings.supabase_url, 
            self.settings.supabase_key
        )
        
    def create_conversation(self, user_identifier: str) -> Dict:
        """Create a new conversation"""
        try:
            response = self.supabase.table("conversations").insert({
                "user_identifier": user_identifier
            }).execute()
            return response.data[0]
        except Exception as e:
            logger.error(f"Error creating conversation: {str(e)}")
            raise

    def generate_embedding(self, text: str) -> List[float]:
        try:
            embedding = self.model.encode(text, normalize_embeddings=True)
            logger.info(f"Generated embedding with shape: {embedding.shape}")
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise

    def search_similar_content(self, query: str, threshold: float = 0.5) -> List[Dict]:
        try:
            query_embedding = self.generate_embedding(query)
            response = self.supabase.rpc(
                'match_documents',
                {
                    'query_embedding': query_embedding,
                    'match_threshold': threshold,
                    'match_count': 5
                }
            ).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error searching content: {str(e)}")
            raise

    def save_message(self, conversation_id: str, role: str, content: str) -> Dict:
        try:
            response = self.supabase.table("messages").insert({
                "conversation_id": conversation_id,
                "role": role,
                "content": content
            }).execute()
            return response.data[0]
        except Exception as e:
            logger.error(f"Error saving message: {str(e)}")
            raise

    def get_conversation_history(self, conversation_id: str) -> List[Dict]:
        try:
            response = self.supabase.table("messages")\
                .select("*")\
                .eq("conversation_id", conversation_id)\
                .order("created_at")\
                .execute()
            return response.data
        except Exception as e:
            logger.error(f"Error retrieving conversation: {str(e)}")
            raise