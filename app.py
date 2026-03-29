def run(url, query):
    # Use the OpenRouter API key variable
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return "Error: OPENROUTER_API_KEY not set in environment variables."
    
    # Initialize the client to point to OpenRouter
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        # Optional: OpenRouter likes these headers for their rankings
        default_headers={
            "HTTP-Referer": "http://localhost:7860", # Site URL
            "X-Title": "AI Assistant",              # Site Name
        }
    )
    
    user_content = (f"URL: {url}\n\n" if url.strip() else "") + query
    messages = [
        {"role": "system", "content": "You are a helpful assistant. When a tool returns a result, always use that result."},
        {"role": "user", "content": user_content},
    ]
    
    while True:
        msg = client.chat.completions.create(
            # Ensure you use an OpenRouter model string (e.g., "openai/gpt-4o-mini")
            model="openai/gpt-4o-mini", 
            messages=messages,
            tools=SCHEMAS,
            tool_choice="auto",
        ).choices[0].message
        
        if not msg.tool_calls:
            return msg.content
        
        messages.append(msg)
        for tc in msg.tool_calls:
            # Execute the function from TOOLS dictionary
            result = TOOLS[tc.function.name](**json.loads(tc.function.arguments))
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
