# AI Crop & Farm Advisory System

A student project: an AI-assisted crop and farm advisory tool for Nigerian farmers, combining
live Open-Meteo weather data with Gemini AI recommendations.

## What it does

- Enter a crop and coordinates, or create a saved farm plot.
- Pull live weather (current conditions, 24-hour hourly forecast, 16-day daily forecast) from
  Open-Meteo — no API key required.
- Detect crop-specific weather threats: heavy rain, heatwaves, and dry spells, each using
  per-crop thresholds defined in `models/crop.py`.
- Get a rule-based planting suitability verdict, a recommended planting window, and an
  irrigation-need estimate for the next few days.
- Get an AI-generated narrative summary from Gemini, built strictly from the rule-based data
  above (Gemini is instructed not to invent weather data).
- Create farm plots, log farming activities against a specific plot, and automatically get a
  season calendar (planting → weeding → fertilizing → irrigation reminder → harvest) generated
  from the plot's planting date and crop.
- View everything on one Dashboard, or browse raw saved data (plots / logs / calendars) as
  three tabs.

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and add your real Gemini API key:
   ```
   cp .env.example .env
   ```
   Edit `.env` and replace the placeholder with your key. Never commit `.env`.

3. Run the app:
   ```
   streamlit run app.py
   ```

## Project structure

```
project/
├── app.py                       Streamlit UI (8 sections)
├── models/
│   └── crop.py                  Crop class, supported crops, per-crop thresholds
├── services/
│   ├── weather_client.py        Open-Meteo integration
│   ├── planting_advisor.py      Rule-based suitability, threats, season calendar logic
│   └── gemini_client.py         Gemini AI integration
├── storage/
│   └── farm_log_store.py        JSON storage for plots, logs, calendars
├── utils/
│   ├── validators.py            Regex + range validation
│   └── exceptions.py            Custom exception classes
├── data/                        JSON storage (created automatically)
├── requirements.txt
└── .env.example
```

## Known limitations / assumptions

- Crop temperature/rainfall ranges, growth durations, weather-threat thresholds, and
  season-calendar event offsets are placeholder agronomic values (flagged in code comments in
  `models/crop.py` and `services/planting_advisor.py`) and should be reviewed against a real
  agricultural reference before being relied on for actual farming decisions.
- Location is entered as latitude/longitude directly. Name-based geocoding is not yet
  implemented.
- Irrigation guidance is intentionally a category (unnecessary/low/moderate/high), not a
  precise quantity, since the underlying data doesn't support that level of precision.
- This is an advisory tool, not a substitute for professional agricultural expertise.

## Testing notes

Core logic (validators, weather threat detection, planting suitability, storage, and Gemini
error handling) has been tested against: valid input, invalid input (bad coordinates, bad
dates, unsupported crops), simulated API failures (connection error, timeout, bad status,
malformed response, missing data), storage edge cases (missing file, empty file, corrupted
file, save/reload), and AI failure modes (missing key, failed request, empty response).
Live network calls to Open-Meteo and Gemini could not be tested from the development sandbox
used to build this project (network restrictions) — run the app locally with real credentials
to confirm live behavior end-to-end.
