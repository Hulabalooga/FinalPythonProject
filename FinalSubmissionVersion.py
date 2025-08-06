import requests
import json
import time
from datetime import datetime, timedelta

# API Keys
TICKETMASTER_KEY = "OnQ7vSAtVDYw2bOxokuCrHRizQrw4XrD"
OPENWEATHER_KEY = "0788ae937efeb4810c23e7f0a53b52e7"

def safe_ticketmaster_request(url, params, max_retries=3, delay=2):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"⚠️ Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
            else:
                print("❌ Failed to connect to Ticketmaster after several attempts.")
                return None

def get_user_preferences():
    verbose_choice = input("🔎 Would you like to display internal debug info? (y/n): ").strip().lower()
    return verbose_choice == "y"

def get_user_location(verbose):
    choice = input("🔍 Search by City or ZIP Code? (Enter 'city' or 'zip'): ").strip().lower()

    if choice == "zip":
        zip_code = input("📮 Enter ZIP Code (e.g., 37130): ").strip()
        location = zip_code
    else:
        city = input("🏙️ Enter city (e.g., Murfreesboro): ").strip()
        state = "TN"
        location = f"{city}, {state}"

    if verbose:
        print(f"DEBUG → Location: {location}")

    return location

def get_user_date_range(verbose):
    def prompt_date(prompt_text):
        while True:
            date_input = input(prompt_text).strip()
            try:
                return datetime.strptime(date_input, "%Y-%m-%d")
            except ValueError:
                print("⚠️ Invalid format. Please use YYYY-MM-DD.")

    print("📅 Enter the date range you're interested in.")
    start_date = prompt_date("  🔹 Start date (YYYY-MM-DD): ")
    end_date = prompt_date("  🔸 End date (YYYY-MM-DD): ")

    if end_date < start_date:
        print("⚠️ End date cannot be before start date. Please try again.\n")
        return get_user_date_range(verbose)

    start_datetime = start_date.strftime("%Y-%m-%dT00:00:00Z")
    end_datetime = end_date.strftime("%Y-%m-%dT23:59:59Z")

    if verbose:
        print(f"DEBUG → Start DateTime: {start_datetime}")
        print(f"DEBUG → End DateTime: {end_datetime}")

    return start_date.date(), end_date.date(), start_datetime, end_datetime

def get_ticketmaster_events(location, verbose, start_date, end_date, start_datetime, end_datetime):
    base_url = "https://app.ticketmaster.com/discovery/v2/events.json"
    page = 0
    page_size = 100
    events = []

    while True:
        params = {
            "apikey": TICKETMASTER_KEY,
            "unit": "miles",
            "startDateTime": start_datetime,
            "endDateTime": end_datetime,
            "sort": "date,asc",
            "size": page_size,
            "page": page
        }

        if location.isdigit():
            params["postalCode"] = location
        else:
            params["city"] = location.split(",")[0]

        data = safe_ticketmaster_request(base_url, params)
        if data is None:
            break

        if "_embedded" not in data or "events" not in data["_embedded"]:
            break

        for event in data["_embedded"]["events"]:
            start_info = event["dates"]["start"]
            event_local_str = start_info.get("localDate")

            try:
                if not event_local_str:
                    continue

                event_date = datetime.strptime(event_local_str, "%Y-%m-%d").date()
                if not (start_date <= event_date <= end_date):
                    continue

                name = event["name"]
                date = event_local_str
                time = start_info.get("localTime", "TBA")
                venue = event["_embedded"]["venues"][0].get("name", "Unknown Venue")
                events.append(f"🎫 {name} – {date} at {time} 📍 {venue}")

            except Exception as e:
                if verbose:
                    print(f"DEBUG → Skipped one event due to date parsing: {e}")
                continue

        if "page" not in data or page >= data["page"].get("totalPages", 0) - 1:
            break

        page += 1

    if verbose:
        print(f"DEBUG → Total Events Collected: {len(events)}")

    return events

def get_weather_forecast(location, verbose):
    if location.isdigit():
        query = location
    else:
        query = location.split(",")[0]

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": query,
        "appid": OPENWEATHER_KEY,
        "units": "imperial"
    }

    if verbose:
        print(f"DEBUG → Weather Params: {params}")

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        weather = data["weather"][0]["description"].capitalize()
        temp = round(data["main"]["temp"])
        forecast = f"🌡️ {temp}°F and {weather}"

        if verbose:
            print(f"DEBUG → Weather Response: {data}")

        return forecast

    except requests.RequestException as e:
        print(f"⚠️ Weather Error: {e}")
        return "Weather data not available."

def discover_free_events():
    verbose_mode = get_user_preferences()
    location = get_user_location(verbose_mode)
    start_date, end_date, start_datetime, end_datetime = get_user_date_range(verbose_mode)

    weather = get_weather_forecast(location, verbose_mode)
    all_events = get_ticketmaster_events(location, verbose_mode, start_date, end_date, start_datetime, end_datetime)

    print(f"\n🌤️ Weather at {location}: {weather}")
    print("\n🎉 Events Found:")
    if all_events:
        for event in all_events:
            print(event)
    else:
        print("No events found in this date range.")

if __name__ == "__main__":
    discover_free_events()
