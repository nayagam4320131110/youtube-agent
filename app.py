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

# 3. The Core Execution Logic
def run(url, query):
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return "Error: OPENROUTER_API_KEY not set."
    
    # Initialize OpenRouter client
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
        # Fixed the closing parenthesis and block here
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=messages,
            tools=SCHEMAS,
            tool_choice="auto",
        )
        
        msg = response.choices[0].message
        
        if not msg.tool_calls:
            return msg.content
        
        messages.append(msg)
        for tc in msg.tool_calls:
            # Execute the function
            result = TOOLS[tc.function.name](**json.loads(tc.function.arguments))
            # Append tool result to history
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

# 4. Gradio UI Interface
with gr.Blocks(title="AI Assistant") as app:
    gr.Markdown("## 🤖 AI Assistant — video · math · weather")
    
    with gr.Row():
        url_input = gr.Textbox(label="YouTube URL (optional)", placeholder="https://www.youtube.com/watch?v=...")
        qry_input = gr.Textbox(label="Question", placeholder="Summarize the video / 128 * 37 / Weather in Tokyo", lines=2)
    
    btn = gr.Button("Ask")
    output = gr.Textbox(label="Answer", lines=10)
    
    btn.click(fn=run, inputs=[url_input, qry_input], outputs=output)

if __name__ == "__main__":
    # Launch with dynamic port for Railway
    app.launch(
        server_name="0.0.0.0", 
        server_port=int(os.environ.get("PORT", 7860))
    )
