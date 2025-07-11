import os
import chainlit as cl
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import json
import re
from typing import Optional, Dict
from inject_org_auth import add_org_oauth_provider
from org_oauth_provider import OrgOAuthProvider

# Load environment variables
load_dotenv()

# Add custom OAuth provider to Chainlit's providers list
add_org_oauth_provider("org-openid", OrgOAuthProvider())

class PerformAssistant:
    def __init__(self):
        """Initialize Perform Assistant with LLM"""
        #self.llm_client = OpenAI(api_key=os.getenv("LLM_API_KEY"), base_url="")
        self.llm_client = OpenAI(api_key=os.getenv("LLM_API_KEY"))

    def generate_response(self, query: str) -> str:
        """Parse mode from query, select prompt/model, and generate response."""
        # Default mode
        mode = 'goals'
        match = re.match(r"\[(GOALS|FEEDBACK|SELF)\] (.*)", query.strip(), re.IGNORECASE)
        if match:
            mode = match.group(1).lower()
            user_query = match.group(2)
        else:
            user_query = query

        # Select prompt and model
        if mode == 'goals':
            system_prompt = (
                "You are Perform Assistant, a helpful AI assistant focused on helping users write and achieve their work goals. "
                "etc."
            )
            model = os.getenv("LLM_MODEL")
        elif mode == 'feedback':
            system_prompt = (
                "You are Perform Assistant, an expert in giving and receiving professional feedback. "
                "etc."
            )
            model = os.getenv("LLM_MODEL")
        elif mode == 'self':
            system_prompt = (
                "You are Perform Assistant, an expert in self-assessment and reflection. "
                "etc."
            )
            model = os.getenv("LLM_MODEL")
        else:
            system_prompt = (
                "You are Perform Assistant, a helpful AI assistant for professional development."
            )
            model = os.getenv("LLM_MODEL")

        try:
            response = self.llm_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"

# Initialize assistant globally
assistant = None

@cl.oauth_callback
def oauth_callback(
    provider_id: str,
    token: str,
    raw_user_data: Dict[str, str],
    default_user: cl.User,
) -> Optional[cl.User]:
    """Handle OAuth callback - group validation already done in provider"""
    print(f"OAuth callback for provider: {provider_id}")
    print(f"User data: {json.dumps(raw_user_data, indent=2)}")
    
    # If we get here, the user has already passed group validation in the custom provider
    # Just return the user object that was created by the provider
    return default_user

@cl.on_chat_start
async def start():
    """Initialize the Perform Assistant when chat starts"""
    global assistant
    
    # Check environment variables
    required_vars = ["LLM_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        await cl.Message(
            content=f"Missing environment variables: {', '.join(missing_vars)}\n\nPlease add these to your .env file and restart the app."
        ).send()
        return
    
    try:
        assistant = PerformAssistant()
        
        # Check if user is authenticated via OAuth
        user = cl.user_session.get("user")
        if user and user.metadata:
            user_name = user.metadata.get("name", "there")
            await cl.Message(
                content=f"Welcome, {user_name}! How can I help you today?"
            ).send()
        # If no authenticated user, keep the clean landing page without automatic message
        
    except Exception as e:
        await cl.Message(
            content=f"Error initializing Perform Assistant: {e}"
        ).send()

@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages"""
    global assistant
    
    if assistant is None:
        await cl.Message(
            content="Perform Assistant is not initialized. Please check your environment variables and restart the app."
        ).send()
        return
    
    # Check if message contains files
    if message.elements:
        await cl.Message(
            content="File upload is currently disabled."
        ).send()
        return
    
    try:
        # Get IP address from the session
        ip_address = "unknown"
        try:
            # Try to get IP from session metadata
            if hasattr(message, 'session') and message.session:
                ip_address = getattr(message.session, 'client_ip', 'unknown')
        except:
            pass
        
        # Generate response using the assistant
        response = assistant.generate_response(message.content)
        
        await cl.Message(content=response).send()
        
    except Exception as e:
        await cl.Message(
            content=f"Error processing your message: {e}"
        ).send()

@cl.on_settings_update
async def setup_agent(settings):
    """Handle settings updates if needed"""
    pass 