# mcp-flight-map

Demo Recording:- https://drive.google.com/file/d/1qRNfk_p79G89ST9OaEnpr1A2N-u7doKy/view?usp=sharing

An [MCP](https://modelcontextprotocol.io) server that exposes flight search and Google Maps directions as tools, powered by [SerpApi](https://serpapi.com/).

## Tools

### `search_flights` (flight.py)
Search for flights via Google Flights.

| Argument | Type | Description |
|---|---|---|
| `departure_id` | str | 3-letter departure airport code (e.g. `AUS`) |
| `arrival_id` | str | 3-letter arrival airport code (e.g. `JFK`) |
| `outbound_date` | str | Departure date, `YYYY-MM-DD` |
| `return_date` | str \| None | Return date, `YYYY-MM-DD` (omit for one-way) |
| `currency` | str | Currency code, defaults to `USD` |

### `get_directions` (map.py)
Get directions and route info between two locations via Google Maps.

| Argument | Type | Description |
|---|---|---|
| `start_addr` | str | Starting address or place name |
| `end_addr` | str | Destination address or place name |
| `travel_mode` | str | One of `best`, `driving`, `two-wheeler`, `transit`, `walking`, `cycling`, `flight`. Defaults to `driving` |

## Setup

Requires Python 3.13+ and a [SerpApi](https://serpapi.com/) API key.

```bash
uv sync
```

Add your API key to `.env`:

```
SERPAPI_API_KEY="your-key-here"
```

## Running

Each tool is its own MCP server, run over stdio:

```bash
uv run flight.py
uv run map.py
```

Point an MCP-compatible client (e.g. Claude Desktop) at these scripts to use the tools.
