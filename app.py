# Streamlit App
import streamlit as st
import requests
import pandas as pd 
import os 

# -------- Loading Secrets --------

CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
REDIRECT_URI = st.secrets["REDIRECT_URI"]
IS_OWNER = st.secrets.get("IS_OWNER", False)

# -------- Loading Internal Data --------

csv_file = "all_athletes_activities.csv"
if os.path.exists(csv_file):
    df_combined_all = pd.read_csv(csv_file)
else:
    df_combined_all = pd.DataFrame()

# -------- Helper Functions --------

def get_all_activities(access_token):
    activities = []
    page = 1
    per_page = 50  # max is 200, but 50 is safer

    headers = {'Authorization': f'Bearer {access_token}'}

    while True:
        url = f'https://www.strava.com/api/v3/athlete/activities?page={page}&per_page={per_page}'
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            st.error(f"Failed to fetch activities: {response.status_code}")
            break

        data = response.json()
        if not data:
            break

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

# -------- Streamlit App UI --------

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

# Step 2: Show login button
params = st.query_params
if "code" not in params:
    st.markdown(f"[🔐 Click here to connect your Strava account]({auth_url})")

# Step 3: Capture the code from URL
else:
    code = params["code"][0]
    st.success("✅ Authentification Successful")

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
        athlete_id = tokens["athlete"]["id"]

        # Step 5: Fetch user's activities
        with st.spinner("⏳ Fetching your Strava activities..."):
            activities = get_all_activities(access_token)
            df_user = activities_to_df(activities)
        
        st.success(f"✅ Data Uploaded. {len(df_user)} activites were stored.")
        st.dataframe(df_user)

        # Step 6: Combine data into one single dataframe
        df_combined_all = pd.concat([df_combined_all, df_user], ignore_index=True)
        df_combined_all.drop_duplicates(subset=["activity_id"], inplace=True)
        df_combined_all.to_csv(csv_file, index=False)

        # Step 7: Owner-only can download combined data
        if IS_OWNER:
            st.subheader("Full Dataset (Owner Only)")
            st.dataframe(df_combined_all)

    else:
        st.error("❌ Failed to get tokens")
        st.json(response.json())

if IS_OWNER and not df_combined_all.empty:
    csv_all = df_combined_all.to_csv(index=False)
    st.download_button(
        label="📥 Load all activities (Owner Only)",
        data=csv_all,
        file_name="all_athletes_activities.csv",
        mime="text/csv"
    )