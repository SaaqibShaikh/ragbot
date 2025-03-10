from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, UUID4
from typing import List, Optional
from services.chatbot import ChatbotService
from config import get_settings

app = FastAPI()
settings = get_settings()

class Message(BaseModel):
    content: str
    role: str

class Conversation(BaseModel):
    id: UUID4
    user_identifier: str
    messages: List[Message]

class ChatRequest(BaseModel):
    user_identifier: str
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    similar_content: List[dict]

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    chatbot = ChatbotService()
    
    try:
        # Create or get conversation
        if not request.conversation_id:
            conversation = chatbot.create_conversation(request.user_identifier)
            conversation_id = conversation['id']
        else:
            conversation_id = request.conversation_id

        # Save user message
        chatbot.save_message(conversation_id, 'user', request.message)
        
        # Search for similar content
        similar_content = chatbot.search_similar_content(request.message)
        
        # Generate response based on similar content
        if similar_content:
            response = similar_content[0]['content']
        else:
            response = "I'm sorry, I couldn't find a relevant answer to your question."
        
        # Save assistant response
        chatbot.save_message(conversation_id, 'assistant', response)
        
        return ChatResponse(
            conversation_id=conversation_id,
            response=response,
            similar_content=similar_content
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: str):
    chatbot = ChatbotService()
    try:
        messages = chatbot.get_conversation_history(conversation_id)
        return {
            "id": conversation_id,
            "user_identifier": messages[0]["user_identifier"] if messages else "",
            "messages": messages
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))