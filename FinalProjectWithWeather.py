import requests  # Import the requests module to handle HTTP API requests

# Ticketmaster API Key
TICKETMASTER_KEY = "OnQ7vSAtVDYw2bOxokuCrHRizQrw4XrD"  # Developer key for Ticketmaster API
OPENWEATHER_KEY = "0788ae937efeb4810c23e7f0a53b52e7"  #Dev key for open weather API

def get_user_preferences():
    verbose_choice = input("🔎 Would you like to display all internal variables? (y/n): ").strip().lower()
    return verbose_choice == "y"

# Get location and radius info from the user
def get_user_location(verbose):
    choice = input("🔍 Search by City or ZIP Code? (Enter 'city' or 'zip'): ").strip().lower()

    if choice == "zip":
        zip_code = input("📮 Enter ZIP Code (e.g., 37130): ").strip()
        location = zip_code
    else:
        city = input("🏙️ Enter city (e.g., Murfreesboro): ").strip()
        state = "TN"
        location = f"{city}, {state}"

    radius = input("📏 Enter radius in miles (e.g., 10): ").strip()

    if verbose:
        print(f"DEBUG → Location: {location}, Radius: {radius}mi")

    return location, f"{radius}mi"

# Retrieve events from Ticketmaster API
def get_ticketmaster_events(location, radius, verbose, keyword="free"):
    print("\n🎫 Searching Ticketmaster...")
    url = "https://app.ticketmaster.com/discovery/v2/events.json"

    params = {
        "apikey": TICKETMASTER_KEY,
        "keyword": keyword,
        "radius": radius.replace("mi", ""),
        "unit": "miles"
    }

    if location.isdigit():
        params["postalCode"] = location
    else:
        params["city"] = location.split(",")[0]

    if verbose:
        print(f"DEBUG → Ticketmaster Params: {params}")

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        events = []

        if "_embedded" in data:
            for event in data["_embedded"]["events"]:
                name = event["name"]
                date = event["dates"]["start"].get("localDate", "TBA")
                events.append(f"🎫 {name} – {date}")
        else:
            print("No Ticketmaster events found.")

        if verbose:
            print(f"DEBUG → Ticketmaster Events: {events}")

        return events

    except requests.RequestException as e:
        print(f"⚠️ Ticketmaster Error: {e}")
        return []

def get_weather_forecast(location, verbose): #Start of open weather integration
    print("\n🌤️ Checking Weather Forecast...")

    # Use city if location is not a ZIP
    if location.isdigit():
        query = location
    else:
        city = location.split(",")[0]
        query = city

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": query,
        "appid": OPENWEATHER_KEY,
        "units": "imperial"  # Fahrenheit
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
        

# Main discovery function
def discover_free_events():
    verbose_mode = get_user_preferences()
    location, radius = get_user_location(verbose_mode)

    weather = get_weather_forecast(location, verbose_mode)
    print(F"\n Weather at {location}: {weather}")
    
    all_events = []
    all_events.extend(get_ticketmaster_events(location, radius, verbose_mode))

    print("\n🎉 Events Found:")
    if all_events:
        for event in all_events:
            print(event)

# Run the app if script is executed directly
if __name__ == "__main__":
    discover_free_events()
