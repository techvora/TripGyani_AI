
#======================================autocomplete destination====================================================

import requests
import uuid
import streamlit as st

api_key = "YOUR_API_KEY"

# # Generate a session token
# session_token = str(uuid.uuid4())
# destination = "ahmedabad"
#
# # url = "https://maps.gomaps.pro/maps/api/place/autocomplete/json?input=ahmedabad&sessiontoken=<string>&components=country:us|country:pr&strictbounds=<boolean>&offset=3&origin=40,-110&location=40,-110&radius=1000&types=<string>&language=en&region=en&key=YOUR_API_KEY"
# url = f"https://maps.gomaps.pro/maps/api/place/autocomplete/json?input={destination}&sessiontoken={session_token}&offset=3&origin=40,-110&location=40,-110&radius=1000&&language=en&region=en&key={api}"
#
# payload={}
# headers = {}
#
# response = requests.request("GET", url, headers=headers, data=payload)
#
# print(response.text)

#======================================query autocomplete destination====================================================


# import requests
# destination = input("Enter a destination: ")
# url = f"https://maps.gomaps.pro/maps/api/place/queryautocomplete/json?input={destination}&offset=3&location=40,-110&radius=1000&language=en&key={api}"
#ss
# payload={}
# headers = {}
#
# response = requests.request("GET", url, headers=headers, data=payload)
#
# print(response.text)



#==========================================================================================


def get_place_suggestions(query):
    session_token = str(uuid.uuid4())  # Generate a new session token for each request
    url = f"https://maps.gomaps.pro/maps/api/place/autocomplete/json"
    params = {
        "input": query,
        "sessiontoken": session_token,
        "key": api_key
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        predictions = response.json().get('predictions', [])
        return [place['description'] for place in predictions]
    else:
        return []


# Streamlit UI
st.title("Destination Autocomplete")

# User input
user_input = st.text_input("Type your destination:")

# Fetch suggestions based on user input
if user_input:
    suggestions = get_place_suggestions(user_input)
else:
    suggestions = []

# Create a placeholder for suggestions
suggestions_placeholder = st.empty()

# If there are suggestions, display them in a selectbox
if suggestions:
    # Combine the suggestions and the current input
    options = suggestions + [user_input]  # Allow user to select their input if it's not in the suggestions
    selected_suggestion = st.selectbox("Suggestions:", options, index=len(suggestions))  # Default to user's input
else:
    selected_suggestion = None

# Display the selected suggestion
if selected_suggestion:
    st.write(f"You selected: {selected_suggestion}")
