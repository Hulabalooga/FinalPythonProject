import requests  # Import the requests module to handle HTTP API requests

# Assign your API keys or tokens to these variables
EVENTBRITE_TOKEN = "YOUR_EVENTBRITE_TOKEN"  # OAuth token from Eventbrite developer account
FACEBOOK_TOKEN = "YOUR_FACEBOOK_TOKEN"      # Access token from Facebook Graph API
TICKETMASTER_KEY = "YOUR_TICKETMASTER_KEY"  # Developer key for Ticketmaster API

# Define a function to ask the user if they want to view internal variables during execution
def get_user_preferences():
    # Prompt user to enable or disable verbose (debugging) mode
    verbose_choice = input("🔎 Would you like to display all internal variables? (y/n): ").strip().lower()
    # Convert input to a boolean for later use
    verbose_mode = verbose_choice == "y"
    # Return user’s choice
    return verbose_mode

# Define a function to gather location info from the user
def get_user_location(verbose):
    # Ask whether the user wants to search by city or ZIP code
    choice = input("🔍 Search by City or ZIP Code? (Enter 'city' or 'zip'): ").strip().lower()

    # Handle ZIP code input
    if choice == "zip":
        # Ask for ZIP code and assign it directly to location
        zip_code = input("📮 Enter ZIP Code (e.g., 37130): ").strip()
        location = zip_code
    else:
        # Ask for city name
        city = input("🏙️ Enter city (e.g., Murfreesboro): ").strip()
        # Default to Tennessee unless you expand to take state input
        state = "TN"
        # Combine city and state for Eventbrite/Ticketmaster
        location = f"{city}, {state}"

    # Ask for radius input from user
    radius = input("📏 Enter radius in miles (e.g., 10): ").strip()

    # If verbose mode is enabled, print the location and radius variables
    if verbose:
        print(f"DEBUG → Location: {location}, Radius: {radius}mi")

    # Return the formatted location and radius to be used in API calls
    return location, f"{radius}mi"

# Define a function to retrieve events from Ticketmaster API
def get_ticketmaster_events(location, radius, verbose, keyword="free"):
    # Notify user that Ticketmaster search is in progress
    print("\n🎫 Searching Ticketmaster...")
    # Ticketmaster API endpoint for event discovery
    url = "https://app.ticketmaster.com/discovery/v2/events.json"

    # Create base request parameters
    params = {
        "apikey": TICKETMASTER_KEY,          # Include API key
        "keyword": keyword,                  # Use keyword like 'free'
        "radius": radius.replace("mi", ""),  # Remove 'mi' for compatibility
        "unit": "miles"                      # Unit for radius measurement
    }

    # Add location filter: ZIP or city
    if location.isdigit():
        params["postalCode"] = location      # Use ZIP code format
    else:
        params["city"] = location.split(",")[0]  # Extract city name from location string

    # Print parameters if verbose mode is enabled
    if verbose:
        print(f"DEBUG → Ticketmaster Params: {params}")

    try:
        # Make the API call with requests
        response = requests.get(url, params=params)
        # Raise exception if the request failed
        response.raise_for_status()
        # Parse the JSON response from the API
        data = response.json()
        # Create a list to hold formatted event results
        events = []

        # Check if any events were returned in the response
        if "_embedded" in data:
            # Loop through the returned events
            for event in data["_embedded"]["events"]:
                # Extract name and date fields
                name = event["name"]
                date = event["dates"]["start"].get("localDate", "TBA")
                # Format and append each event to the list
                events.append(f"🎫 {name} – {date}")
        else:
            # Notify if no events were found
            print("No Ticketmaster events found.")

        # Show the collected events in verbose mode
        if verbose:
            print(f"DEBUG → Ticketmaster Events: {events}")

        # Return the list of events
        return events

    # Catch and handle errors during the API call
    except requests.RequestException as e:
        print(f"⚠️ Ticketmaster Error: {e}")
        return []

# Define a function to retrieve events from Eventbrite API
def get_eventbrite_events(location, radius, verbose):
    # Notify user that Eventbrite search is starting
    print("\n🟢 Searching Eventbrite...")
    # Define the API endpoint
    url = "https://www.eventbriteapi.com/v3/events/search/"
    # Include authorization header with Bearer token
    headers = {"Authorization": f"Bearer {EVENTBRITE_TOKEN}"}

    # Create API request parameters
    params = {
        "q": "free",                          # Search for free events
        "location.address": location,         # Use location string
        "location.within": radius,            # Use provided radius
        "price": "free",                      # Filter only free events
        "sort_by": "date"                     # Sort results chronologically
    }

    # Display parameters if verbose mode is on
    if verbose:
        print(f"DEBUG → Eventbrite Params: {params}")

    try:
        # Make API request to Eventbrite
        response = requests.get(url, headers=headers, params=params)
        # Raise exception for failed requests
        response.raise_for_status()
        # Parse the response JSON
        data = response.json()
        # Create list to store events
        events = []

        # Loop through all returned events
        for event in data.get("events", []):
            name = event["name"]["text"]     # Extract event name
            start = event["start"]["local"]  # Extract start time
            events.append(f"🟢 {name} – {start}")  # Format and add to list

        # Notify if no results found
        if not events:
            print("No Eventbrite events found.")
        # Show formatted events in verbose mode
        if verbose:
            print(f"DEBUG → Eventbrite Events: {events}")

        # Return the list of formatted event strings
        return events

    # Handle request exceptions gracefully
    except requests.RequestException as e:
        print(f"⚠️ Eventbrite Error: {e}")
        return []

# Define a function to retrieve events from Facebook Graph API
def get_facebook_events(location, verbose):
    # Notify user that Facebook search is beginning
    print("\n🔵 Searching Facebook...")
    # Facebook Graph API endpoint
    url = "https://graph.facebook.com/v18.0/search"
    # Fallback to city if ZIP was entered
    city = location if not location.isdigit() else "Murfreesboro"

    # Build request parameters for the API
    params = {
        "type": "event",                         # We're searching for events
        "q": city.split(",")[0],                 # Use city name for query
        "access_token": FACEBOOK_TOKEN           # Use your access token
    }

    # Print parameters in verbose mode
    if verbose:
        print(f"DEBUG → Facebook Params: {params}")

    try:
        # Make the GET request
        response = requests.get(url, params=params)
        # Raise exception on error
        response.raise_for_status()
        # Parse the JSON response
        data = response.json()
        # List to hold formatted events
        events = []

        # Loop through each returned event
        for event in data.get("data", []):
            name = event.get("name", "Unnamed Event")  # Extract name or default
            event_id = event.get("id")                 # Extract event ID
            events.append(f"🔵 {name} (Event ID: {event_id})")  # Format and store

        # Notify user if no events were returned
        if not events:
            print("No Facebook events found.")
        # Print debug info if enabled
        if verbose:
            print(f"DEBUG → Facebook Events: {events}")

        # Return the event list
        return events

    # Catch exceptions if API request fails
    except requests.RequestException as e:
        print(f"⚠️ Facebook Error: {e}")
        return []

# Define the master function to run the discovery process
def discover_free_events():
    # Ask user whether to enable verbose mode
    verbose_mode = get_user_preferences()

    # Get location and radius input from the user
    location, radius = get_user_location(verbose_mode)

    # Create an empty list to hold all events from all APIs
    all_events = []

    # Call each API function and collect their events
    all_events.extend(get_ticketmaster_events(location, radius, verbose_mode))
    all_events.extend(get_eventbrite_events(location, radius, verbose_mode))
    all_events.extend(get_facebook_events(location, verbose_mode))

    # Display final results to the user
    print("\n🎉 Events Found:")
    if all_events:
        # Print each event
        for event in all_events:
            print(event)
