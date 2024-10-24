!pip install streamlit pandas numpy geopy
!pip install streamlit
!pip install streamlit-folium


streamlit_code = """
import streamlit as st
import pandas as pd
import numpy as np
from geopy.distance import geodesic
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap

# Load synthetic contamination data
data = pd.read_csv('bangalore_food_contamination_data.csv')

# Helper function to classify contamination level
def classify_contamination(level):
    if level >= 7:
        return 'High'
    elif 4 <= level < 7:
        return 'Medium'
    else:
        return 'Low'

# Function to find nearest contamination point based on user's latitude/longitude
def get_nearest_contamination(user_lat, user_lon, data):
    user_location = (user_lat, user_lon)
    distances = data.apply(lambda row: geodesic(user_location, (row['latitude'], row['longitude'])).meters, axis=1)
    nearest_index = distances.idxmin()
    return data.iloc[nearest_index]

# Function to generate a map with a marker and heatmap
def generate_map(user_lat=None, user_lon=None, data=None):
    # Create a map centered around Bangalore
    bangalore_center = [12.9716, 77.5946]
    m = folium.Map(location=bangalore_center, zoom_start=12)

    # Add heatmap
    heat_data = [[row['latitude'], row['longitude'], row['contamination_level']] for index, row in data.iterrows()]
    HeatMap(heat_data, radius=12).add_to(m)

    # If user coordinates are provided, add a marker for the user
    if user_lat and user_lon:
        folium.Marker(
            [user_lat, user_lon],
            popup=f"User Location: {user_lat}, {user_lon}",
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(m)

    return m

# Streamlit web app
st.title('Food Safety Contamination Level in Bangalore')

# Initialize session state for user location
if 'user_lat' not in st.session_state:
    st.session_state['user_lat'] = None
if 'user_lon' not in st.session_state:
    st.session_state['user_lon'] = None

# Option for user to input latitude/longitude or use current location
option = st.selectbox(
    'How would you like to provide your location?',
    ('Manual Latitude/Longitude Input', 'Use GPS (if available on mobile)')
)

if option == 'Manual Latitude/Longitude Input':
    user_lat = st.number_input('Enter Latitude', value=12.9716)
    user_lon = st.number_input('Enter Longitude', value=77.5946)

    if st.button('Get Contamination Level'):
        st.session_state['user_lat'] = user_lat
        st.session_state['user_lon'] = user_lon

# Use GPS option
elif option == 'Use GPS (if available on mobile)':
    st.write('Attempting to get your location...')
    
    st.markdown(location_js, unsafe_allow_html=True)

    # Capture latitude and longitude from JavaScript
    user_location = st.query_params

    if 'lat' in user_location and 'lon' in user_location:
        st.session_state['user_lat'] = float(user_location['lat'][0])
        st.session_state['user_lon'] = float(user_location['lon'][0])

# Check if location is available in session_state
if st.session_state['user_lat'] is not None and st.session_state['user_lon'] is not None:
    user_lat = st.session_state['user_lat']
    user_lon = st.session_state['user_lon']

    # Find the nearest contamination point
    nearest_data = get_nearest_contamination(user_lat, user_lon, data)
    contamination_level = nearest_data['contamination_level']
    contamination_category = classify_contamination(contamination_level)
    contamination_percentage = (contamination_level / 10) * 100
    
    # Display results
    st.write(f'Nearest Contamination Level: {contamination_level}/10')
    st.write(f'Contamination Level Percentage: {contamination_percentage:.2f}%')
    st.write(f'Risk Category: {contamination_category}')

    # Provide theoretical information based on risk category
    if contamination_category == 'High':
        st.write('High Risk: This area has a high contamination level. Factors such as poor water quality, poor hygiene, and proximity to garbage disposal areas may contribute to higher risks of foodborne diseases.')
    elif contamination_category == 'Medium':
        st.write('Medium Risk: This area has a moderate contamination level. While conditions are relatively safe, some factors like air contamination or temperature may increase food safety risks.')
    else:
        st.write('Low Risk: This area has a low contamination level. The area has generally favorable environmental conditions for food safety.')

    # Generate and display the map with the user's location marker
    m = generate_map(user_lat=user_lat, user_lon=user_lon, data=data)
    st_folium(m, width=700, height=500)
"""

# Step 2: Save the Streamlit code to a file
with open("app.py", "w") as f:
    f.write(streamlit_code)



