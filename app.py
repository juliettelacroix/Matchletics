# Streamlit App
import streamlit as st
import requests
import pandas as pd 
import os 

def get_all_activities(access_token):
    activities = []
    page = 1
    per_page = 50  # max is 200, but 50 is safe default

    headers = {'Authorization': f'Bearer {access_token}'}

    while True:
        url = f'https://www.strava.com/api/v3/athlete/activities?page={page}&per_page={per_page}'
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            st.error(f"Failed to fetch activities: {response.status_code}")
            break

        data = response.json()
        if not data:
            break  # no more pages

        activities.extend(data)
        page += 1

    return activities

def activities_to_df(activities):
    rows = []
    for act in activities:
        row = {
            'activity_id': act.get('id'),
            'athlete_id': act.get('athlete', {}).get('id'),
            'name': act.get('name'),
            'type': act.get('type'),
            'distance_m': act.get('distance'),
            'elapsed_time_s': act.get('elapsed_time'),
            'start_date': act.get('start_date'),
            'start_latlng': act.get('start_latlng'),  # list like [lat, lng]
            'end_latlng': act.get('end_latlng'),
            'total_elevation_gain': act.get('total_elevation_gain'),
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    return df


CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
REDIRECT_URI = st.secrets["REDIRECT_URI"]

st.title("🔗 Connect to Strava")

# Step 1: Build the Strava OAuth URL
auth_url = (
    f"https://www.strava.com/oauth/authorize"
    f"?client_id={CLIENT_ID}"
    f"&response_type=code"
    f"&redirect_uri={REDIRECT_URI}"
    f"&scope=read,activity:read_all"
    f"&approval_prompt=force"
)

# Step 2: Show login button if no code yet
params = st.query_params
if "code" not in params:
    st.markdown(f"[🔐 Click here to connect your Strava account]({auth_url})")
else:
    # Step 3: Capture the code from URL
    code = params["code"][0]
    st.success("✅ Authorization code received!")
    st.code(code)

    # Step 4: Exchange the code for access token
    response = requests.post("https://www.strava.com/oauth/token", data={
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI
    })

    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        st.success("🔑 Tokens retrieved successfully!")
        st.json(tokens)

        activities = get_all_activities(access_token)
        st.write(f"Fetched {len(activities)} activities")

        df = activities_to_df(activities)

        csv_file = "all_athletes_activities.csv"

        if os.path.exists(csv_file):
            df_existing = pd.read_csv(csv_file)
        else:
            df_existing = pd.DataFrame()

        df_combined = pd.concat([df_existing, df], ignore_index=True)
        df_combined.drop_duplicates(subset=["activity_id"], inplace=True)

        df_combined.to_csv(csv_file, index=False)

        st.success(f"✅ Données sauvegardées. Total : {len(df_combined)} activités.")
        st.dataframe(df_combined)

        csv = df_combined.to_csv(index=False)
        st.download_button(
            label="📥 Télécharger toutes les activités (CSV)",
            data=csv,
            file_name="all_athletes_activities.csv",
            mime="text/csv"
        )

    else:
        st.error("❌ Failed to get tokens")
        st.json(response.json())