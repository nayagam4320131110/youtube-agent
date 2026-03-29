import os, json
import gradio as gr
from openai import OpenAI
from mcp_server import get_transcript, calculate, get_weather

# 1. Mapping tool names to their actual Python functions
TOOLS = {
    "get_transcript": get_transcript, 
    "calculate": calculate, 
    "get_weather": get_weather
}

# 2. OpenAI Function Calling Schemas
SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_transcript",
            "description": "Get YouTube video transcript.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "YouTube video URL"}
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a math expression.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "The math expression to evaluate"}
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "The name of the city"}
                },
                "required": ["city"],
            },
        },
    }
]

# 3. The Core Execution Logic (Fixed for OpenRouter)
def run(url, query):
    # Use the OpenRouter API key variable
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return "Error: OPENROUTER_API_KEY not set in Railway environment variables."
    
    # Initialize the client pointing to OpenRouter
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        default_headers={
            "HTTP-Referer": "https://railway.app",
            "X-Title": "AI Assistant",
        }
    )
    
    user_content = (f"URL: {url}\n\n" if url.strip() else "") + query
    messages = [
        {"role": "system", "content": "You are a helpful assistant. When a tool returns a result, always use that result."},
        {"role": "user", "content": user_content},
    ]
    
    while True:
        msg = client.chat.completions.create(
            model="openai/gpt-4o-mini", # Use OpenRouter model format
            messages=messages,
            tools=SCHEMAS,
