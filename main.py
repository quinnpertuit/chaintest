import os
import chainlit as cl
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import json
import re

# Load environment variables
load_dotenv()

def log_user_interaction(ip_address: str, question: str, timestamp: str = None):
    """Log user interactions to a JSON file"""
    if timestamp is None:
        timestamp = datetime.now().isoformat()
    
    log_entry = {
        "ip_address": ip_address,
        "question": question,
        "timestamp": timestamp
    }
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Append to log file
    log_file = "logs/user_interactions.json"
    
    try:
        # Read existing logs
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        # Add new entry
        logs.append(log_entry)
        
        # Write back to file
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
            
    except Exception as e:
        print(f"Error logging interaction: {e}")

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
            model = "llama-3.3-70b-instruct"
        elif mode == 'feedback':
            system_prompt = (
                "You are Perform Assistant, an expert in giving and receiving professional feedback. "
                "etc."
            )
            model = "llama-3.3-70b-instruct"
        elif mode == 'self':
            system_prompt = (
                "You are Perform Assistant, an expert in self-assessment and reflection. "
                "etc."
            )
            model = "llama-3.3-70b-instruct"
        else:
            system_prompt = (
                "You are Perform Assistant, a helpful AI assistant for professional development."
            )
            model = "llama-3.3-70b-instruct"

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
        # Remove the automatic welcome message to keep the clean landing page with logo
        # await cl.Message(
        #     content="Hi! I'm Perform Assistant. I'm here to help you write and achieve your work goals. What would you like to work on today?"
        # ).send()
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
        
        # Log the user interaction
        log_user_interaction(ip_address, message.content)
        
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