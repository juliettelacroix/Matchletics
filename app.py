# Streamlit App
import streamlit as st
import requests

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
        'grant_type': 'authorization_code'
    })

    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        st.success("🔑 Tokens retrieved successfully!")
        st.json(tokens)
    else:
        st.error("❌ Failed to get tokens")
        st.json(response.json())