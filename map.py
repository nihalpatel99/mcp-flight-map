import os
import sys

import httpx2
from dotenv import load_dotenv
from mcp.server import MCPServer
import os

# Initialize MCPServer
mcp = MCPServer("map")

SERPAPI_BASE = "https://serpapi.com/search"
SERPAPI_KEY = os.environ.get("SERPAPI_API_KEY", "")



TRAVEL_MODES = {
    "best": 6,
    "driving": 0,
    "two-wheeler": 9,
    "transit": 3,
    "walking": 2,
    "cycling": 1,
    "flight": 4,
}


async def make_serpapi_request(params: dict) -> dict | None:
    """Make a request to the SerpApi endpoint with error handling."""
    params["api_key"] = SERPAPI_KEY
    async with httpx2.AsyncClient() as client:
        try:
            response = await client.get(SERPAPI_BASE, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"SerpApi request failed: {e}", file=sys.stderr)
            return None


def format_direction(direction: dict) -> str:
    """Format a single direction/route option into a readable string."""
    return f"""
Travel Mode: {direction.get("travel_mode", "Unknown")}
Distance: {direction.get("formatted_distance", "Unknown")}
Duration: {direction.get("formatted_duration", "Unknown")}
Route: {direction.get("via", "N/A")}
"""


@mcp.tool()
async def get_directions(
    start_addr: str,
    end_addr: str,
    travel_mode: str = "driving",
) -> str:
    """Get directions and route info between two locations using Google Maps.

    Args:
        start_addr: Starting address or place name (e.g. "Dubai Mall, Dubai")
        end_addr: Destination address or place name (e.g. "Burj Khalifa, Dubai")
        travel_mode: One of "best", "driving", "two-wheeler", "transit",
                     "walking", "cycling", "flight". Defaults to "driving".
    """
    if not SERPAPI_KEY:
        return "SERPAPI_API_KEY is not set. Add it to your .env file."

    mode_code = TRAVEL_MODES.get(travel_mode.lower())
    if mode_code is None:
        return f"Unknown travel_mode '{travel_mode}'. Choose from: {', '.join(TRAVEL_MODES)}"

    params = {
        "engine": "google_maps_directions",
        "start_addr": start_addr,
        "end_addr": end_addr,
        "travel_mode": mode_code,
        "hl": "en",
    }

    data = await make_serpapi_request(params)

    if not data:
        return "Unable to fetch directions data."

    directions = data.get("directions", [])

    if not directions:
        return "No routes found between these locations."

    formatted = [format_direction(d) for d in directions[:5]]
    return "\n---\n".join(formatted)


if __name__ == "__main__":
    mcp.run(transport="stdio")