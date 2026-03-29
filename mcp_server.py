from mcp.server.fastmcp import FastMCP
import requests, re, os

# Initialize FastMCP server
mcp = FastMCP("tools")

@mcp.tool()
def get_transcript(url: str) -> str:
    """Get YouTube video transcript via Supadata API."""
    key = os.environ.get("SUPADATA_API_KEY", "")
    resp = requests.get(
        "https://api.supadata.ai/v1/youtube/transcript",
        params={"url": url, "text": True},
        headers={"x-api-key": key},
        timeout=15,
    )
    data = resp.json()
    if not resp.ok or "content" not in data:
        return f"Transcript error: {data}"
    raw = data["content"]
    if isinstance(raw, list):
        text = " ".join(item["text"].replace("\n", " ") for item in raw)
    else:
        text = raw
    return text[:6000]

@mcp.tool()
def calculate(expression: str) -> str:
    """Evaluate a math expression."""
    return f"{expression} = {eval(expression)}"

@mcp.tool()
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    # Step 1: Geocoding - Get lat/long for the city name
    geo = requests.get("https://geocoding-api.open-meteo.com/v1/search", params={"name": city, "count": 1}).json()
    if not geo.get("results"):
        return f"City '{city}' not found."
    
    loc = geo["results"][0]
    
    # Step 2: Forecast - Get weather data using coordinates
    w = requests.get("https://api.open-meteo.com/v1/forecast", params={
        "latitude": loc["latitude"], 
        "longitude": loc["longitude"],
        "current_weather": True
    }).json()
    
    curr = w["current_weather"]
    return f"{loc['name']}: {curr['temperature']}°C, wind {curr['windspeed']} km/h"

if __name__ == "__main__":
    # Run the server using stdio transport
    mcp.run(transport="stdio")