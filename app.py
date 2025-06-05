# Streamlit App
import streamlit as st
import requests

# Strava app credentials
CLIENT_ID = "163006"
CLIENT_SECRET = "7d4bcfed7f9e6300c2e23daca31376245e514fb7"
REDIRECT_URI = "https://juliettelacroix.streamlit.app"


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
if "code" not in st.experimental_get_query_params():
    st.markdown(f"[🔐 Click here to connect your Strava account]({auth_url})")

# Step 3: After redirect, capture the `code`
params = st.experimental_get_query_params()
if "code" in params:
    code = params["code"][0]
    st.success("✅ Authorization code received!")
    st.code(code)

    # Step 4: Exchange the code for an access token
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
