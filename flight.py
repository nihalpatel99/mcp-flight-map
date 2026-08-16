from typing import Any

import httpx2
from mcp.server import MCPServer
import os

# Initialize MCPServer
mcp = MCPServer("flight")

# Constants
SERPAPI_BASE = "https://serpapi.com/search"
SERPAPI_KEY = os.environ.get("SERPAPI_API_KEY", "")  

async def make_serpapi_request(params: dict) -> dict | None:
    """Make a request to the SerpApi endpoint with error handling."""
    params["api_key"] = SERPAPI_KEY
    async with httpx2.AsyncClient() as client:
        try:
            response = await client.get(SERPAPI_BASE, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


def format_flight(flight: dict) -> str:
    """Format a flight offer into a readable string."""
    segments = flight.get("flights",[])
    first_leg = segments[0] if segments else {}
    last_leg = segments[1] if segments else {}
    dep = first_leg.get("departure airport", {})
    arr = last_leg.get("arrival_airport", {})
    return f"""
Airline: {first_leg.get("airline", "Unknown")}
Flight: {first_leg.get("flight_number", "Unknown")}
From: {dep.get("name", "Unknown")} ({dep.get("id", "?")}) at {dep.get("time", "Unknown")}
To: {arr.get("name", "Unknown")} ({arr.get("id", "?")}) at {arr.get("time", "Unknown")}
Duration: {flight.get("total_duration", "Unknown")} min
Price: ${flight.get("price", "Unknown")}
Class: {first_leg.get("travel_class", "Unknown")}
"""

@mcp.tool()
async def search_flights(
    departure_id: str,
    arrival_id: str,
    outbound_date: str,
    return_date: str | None = None,
    currency: str = "USD",
) -> str:
    """Search for flights using Google Flights via SerpApi.

    Args:
        departure_id: 3-letter departure airport code (e.g. AUS)
        arrival_id: 3-letter arrival airport code (e.g. JFK)
        outbound_date: departure date in YYYY-MM-DD format
        return_date: return date in YYYY-MM-DD format (omit for one-way)
        currency: currency code, defaults to USD
    """
    params = {
        "engine": "google_flights",
        "departure_id": departure_id,
        "arrival_id": arrival_id,
        "outbound_date": outbound_date,
        "currency": currency,
        "hl": "en",
        "type": "1" if return_date else "2",
    }
    if return_date:
        params["return_date"] = return_date

    data = await make_serpapi_request(params)

    if not data:
        return "Unable to fetch flight data."

    flights = data.get("best_flights") or data.get("other_flights") or []

    if not flights:
        return "No flights found for this route/date."

    formatted = [format_flight(f) for f in flights[:5]]
    return "\n---\n".join(formatted)
  
if __name__ == "__main__":
    mcp.run(transport="stdio")