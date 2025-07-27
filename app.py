import streamlit as st
import os
from drone_sender import run_mission_by_name  # Import your function
import base64
video_to_mission = {
    "flightVideo1.MP4": "mission_alpha",
    "flightVideo2.MP4": "mission_beta",
    "flightVideo3.MP4": "mission_gamma",
    "flightVideo4.MP4": "mission_delta"
}

def get_base64_image(path):
    with open(path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    return f"data:image/png;base64,{encoded}"

logo_data_uri = get_base64_image("myLogo.png")
# Layout
st.set_page_config(layout="wide")

# Header
st.markdown(f"""
    <div style='text-align: center; display: flex; justify-content: center; align-items: center; gap: 10px; margin-top: 20px;'>
        <h1 style='margin: 0;'>Arc Rescue</h1>
        <img src='{logo_data_uri}' width='60' style='margin-left: 1px;'/>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# List videos
video_folder = "videos"
video_files = [f for f in os.listdir(video_folder) if f.lower().endswith((".mp4", ".mov", ".webm"))]

selected_video = st.selectbox("Select a video to stream:", video_files)

# Run stream sender
if selected_video:
    mission_name = video_to_mission.get(selected_video)
    if mission_name and st.button("Play Stream"):
        video_path = os.path.join(video_folder, selected_video)
        with st.spinner(f"Streaming {selected_video} ({mission_name}) to mock server..."):
            run_mission_by_name(mission_name)
        st.success(f"{mission_name} successfully sent to mock server!")
