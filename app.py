import streamlit as st
import numpy as np
import pandas as pd
import pydeck as pdk
import plotly.express as px


# st.sidebar.selectbox('Change look of the webapp')
st.title("Motor Vehicle Collisions in New York City")
st.markdown("## This application is a streamlit dashboard that can be used to analyze"
             " motor vehicle collsions in NYC 🗽💥")

# using @st.cache makes the data to be loaded only when specified for example if I specify number of accidents to be 6, then it will load only that Data
# this is useful for optimization
@st.cache(persist = True)
def load_data(nrows):
    data = pd.read_csv("D:\Github\Streamlit-nyc\Motor_Vehicle_Collisions.csv", nrows = nrows, parse_dates = [['CRASH_DATE', 'CRASH_TIME']])
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace = True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis = 'columns', inplace = True)
    data.rename(columns={'crash_date_crash_time': 'date/time'}, inplace= True)
    return data

data = load_data(100000)
unfiltered_data = data

st.header("Where are the most people injured in NYC?")
injured_people = st.slider("Number of persons injured in vehicle collsions", 0, 19)
st.map(data.query("injured_persons >= @injured_people")[["latitude", "longitude"]].dropna(how = "any")) # st.map method maps the data to a 2D map using latitude and longitude


st.header("How many collisions occur during a given time of day?")
# hour = st.sidebar.slider("Hour to look at", 0, 23)
hour = st.slider("Hour to look at", 0, 23)
data = data[data['date/time'].dt.hour == hour]

st.markdown("Vehicle collsions between %i:00 and %i:00" % (hour, (hour + 1) % 24))
midpoint = (np.average(data['latitude']), np.average(data['longitude']))

# pydeck enables us to show a 3D interactive map of the vehicle collisions which is easy to visualize
st.write(pdk.Deck(
     map_style = "mapbox://styles/mapbox/light-v9",
     initial_view_state = {
         "latitude":midpoint[0],
         "longitude":midpoint[1],
         "zoom": 11,
         "pitch": 50,
     },
     layers = [
        pdk.Layer(
        "HexagonLayer",
        data = data[['date/time', 'latitude', 'longitude']],
        get_position = ['longitude', 'latitude'],
        radius = 100,
        extruded = True,      # extruded shows us the data in 3D form
        pickable = True,
        elevation_scale = 4,
        elevation_range=[0, 1000],
        ),
     ],
))

st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour + 1) %24))
filtered = data[
     (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour + 1))
]
hist = np.histogram(filtered['date/time'].dt.minute, bins = 60, range = (0, 60))[0]
chart_data = pd.DataFrame({'minute':range(60), 'crashes':hist})
fig = px.bar(chart_data, x = 'minute', y = 'crashes', hover_data = ['minute', 'crashes'], height = 400)
st.write(fig)

st.header("Top 5 most dangerous streets according to data")
select =  st.selectbox('Affected type of people', ['Pedestrians', 'Cyclists', 'Motorists'])

if select == 'Pedestrians':
    st.write(unfiltered_data.query("injured_pedestrians >= 1")[["on_street_name", "injured_pedestrians"]].sort_values(by = ['injured_pedestrians'], ascending = False ).dropna(how = 'any')[:5])
elif select == 'Cyclists':
    st.write(unfiltered_data.query("injured_cyclists >= 1")[["on_street_name", "injured_cyclists"]].sort_values(by = ['injured_cyclists'], ascending = False ).dropna(how = 'any')[:5])
else:
    st.write(unfiltered_data.query("injured_motorists >= 1")[["on_street_name", "injured_motorists"]].sort_values(by = ['injured_motorists'], ascending = False ).dropna(how = 'any')[:5])

if st.checkbox("Show Raw Data", False):
    st.subheader('Raw Data')
    st.write(data)
