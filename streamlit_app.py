import streamlit as st
import requests
import json
from typing import Optional
import uuid

class ChatbotUI:
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        
        # Initialize session state
        if 'user_id' not in st.session_state:
            st.session_state.user_id = None
        if 'conversation_id' not in st.session_state:
            st.session_state.conversation_id = None
        if 'messages' not in st.session_state:
            st.session_state.messages = []

    def login(self):
        st.title("E-Commerce Support Chatbot")
        
        with st.form("login_form"):
            email = st.text_input("Email")
            submit = st.form_submit_button("Login")
            
            if submit and email:
                # Generate a unique user ID for this session
                st.session_state.user_id = str(uuid.uuid4())
                st.success(f"Logged in as {email}")
                return True
        return False

    def display_chat_interface(self):
        st.title("Chat with Support")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        # Chat input
        user_input = st.chat_input("Type your message here...")
        
        if user_input:
            # Add user message to chat
            with st.chat_message("user"):
                st.write(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Send message to API
            response = self.send_message(user_input)
            
            if response:
                # Add assistant response to chat
                with st.chat_message("assistant"):
                    st.write(response["response"])
                st.session_state.messages.append({"role": "assistant", "content": response["response"]})
                
                # Show similar content
                if response.get("similar_content"):
                    with st.expander("Similar FAQs"):
                        for item in response["similar_content"]:
                            st.write(f"- {item['content']}")

    def send_message(self, message: str) -> Optional[dict]:
        try:
            payload = {
                "user_identifier": st.session_state.user_id,
                "message": message,
                "conversation_id": st.session_state.conversation_id
            }
            
            response = requests.post(
                f"{self.api_url}/chat",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                st.session_state.conversation_id = data["conversation_id"]
                return data
            else:
                st.error(f"Error: {response.text}")
                return None
                
        except Exception as e:
            st.error(f"Error sending message: {str(e)}")
            return None

def main():
    st.set_page_config(
        page_title="E-Commerce Support Chatbot",
        page_icon="💬",
        layout="wide"
    )
    
    chatbot = ChatbotUI()
    
    if not st.session_state.user_id:
        if chatbot.login():
            st.rerun()
    else:
        chatbot.display_chat_interface()

if __name__ == "__main__":
    main()