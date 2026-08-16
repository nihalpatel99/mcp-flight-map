from typing import Any

import httpx2
from mcp.server import MCPServer
import os

# Initialize MCPServer
mcp = MCPServer("flight")

# Constants
SERPAPI_BASE = "https://serpapi.com/search"
SERPAPI_KEY = os.environ.get("SERPAPI_API_KEY", "")  # set this in your env, don't hardcode

async def make_serpapi_request(params: dict) -> dict | None:
    """Make a request to the SerpApi endpoint with error handling."""
    params["api_key"] = SERPAPI_KEY
    async with httpx.AsyncClient() as client:
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
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)


@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return "Unable to fetch forecast data for this location."

    # Get the forecast URL from the points response
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return "Unable to fetch detailed forecast."

    # Format the periods into a readable forecast
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # Only show next 5 periods
        forecast = f"""
{period["name"]}:
Temperature: {period["temperature"]}°{period["temperatureUnit"]}
Wind: {period["windSpeed"]} {period["windDirection"]}
Forecast: {period["detailedForecast"]}
"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)
  
if __name__ == "__main__":
    mcp.run(transport="stdio")