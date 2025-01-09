import os
import pickle
import streamlit as st
import glob
import re

# Directories for uploaded content
MUSIC_FOLDER = "/tmp/music"  # Use a folder relative to the app container
DATA_FILE = "tmp/quiz_data.pkl"

# Ensure the directory for quiz data exists
quiz_data_dir = os.path.dirname(DATA_FILE)
if not os.path.exists(quiz_data_dir):
    os.makedirs(quiz_data_dir)


# Ensure the music folder exists
if not os.path.exists(MUSIC_FOLDER):
    os.makedirs(MUSIC_FOLDER)

# Load quiz data if it exists
def load_quiz_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "rb") as f:
            return pickle.load(f)
    return {
        "team_names": {},
        "team_scores": {},
        "num_teams": 1,
        "num_rounds": 5
    }

# Save quiz data to a file
def save_quiz_data():
    with open(DATA_FILE, "wb") as f:
        pickle.dump(st.session_state.quiz_data, f)

# Initialize session state for quiz data
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = load_quiz_data()

# Reset the quiz data and music tracks when the reset button is pressed
if st.button("Reset Quiz"):
    st.session_state.quiz_data = {
        "team_names": {},
        "team_scores": {},
        "num_teams": 1,
        "num_rounds": 5
    }
    # Delete all music files in the MUSIC_FOLDER
    for music_file in glob.glob(f"{MUSIC_FOLDER}/*"):
        os.remove(music_file)
    st.success("Quiz reset and music files cleared!")

# App title
st.title("Pub Quiz App")

# Tabs for the quiz sections
tabs = st.tabs(["Music Round", "Team Setup", "Team Scores", "Summary"])

# Music Round tab
with tabs[0]:
    st.header("Music Round")

    # Upload music files
    uploaded_music = st.file_uploader("Upload music tracks", type=["mp3", "wav"], accept_multiple_files=True, key="music_upload")
    if uploaded_music:
        # Save the uploaded music files
        for music_file in uploaded_music:
            file_path = os.path.join(MUSIC_FOLDER, music_file.name)
            with open(file_path, "wb") as f:
                f.write(music_file.read())
        st.success("Music files uploaded successfully!")

    # Get a list of music files in the folder
    music_files = glob.glob(f"{MUSIC_FOLDER}/*")

    # Sort and display uploaded music files in numerical order
    music_files_sorted = sorted(music_files, key=lambda x: int(re.search(r'(\d+)', os.path.basename(x)).group(1) if re.search(r'(\d+)', os.path.basename(x)) else float('inf')))
    if music_files_sorted:
        st.write("### Uploaded Music Tracks (Sorted Numerically)")
        for music_file in music_files_sorted:
            file_name = os.path.basename(music_file)
            st.write(f"{file_name}")  # Show the filename
            st.audio(str(music_file), format="audio/mp3")  # Pass file path as string

# Team Setup tab
with tabs[1]:
    st.header("Team Setup")
    num_teams = st.number_input("Number of Teams", min_value=1, value=st.session_state.quiz_data["num_teams"], step=1, key="num_teams")
    st.session_state.quiz_data["num_teams"] = num_teams  # Update the number of teams

    # Collect team names
    for i in range(1, num_teams + 1):
        team_name = st.text_input(f"Enter name for Team {i}", value=st.session_state.quiz_data["team_names"].get(i, f"Team {i}"), key=f"team_name_{i}")
        st.session_state.quiz_data["team_names"][i] = team_name  # Store team names

    save_quiz_data()  # Save the quiz data to file whenever it changes

# Team Scores tab
with tabs[2]:
    st.header("Team Scores")
    num_rounds = st.number_input("Number of Rounds", min_value=1, value=st.session_state.quiz_data["num_rounds"], step=1, key="num_rounds")
    st.session_state.quiz_data["num_rounds"] = num_rounds  # Update the number of rounds

    # Initialize team scores
    for team_id in st.session_state.quiz_data["team_names"].keys():
        if team_id not in st.session_state.quiz_data["team_scores"]:
            st.session_state.quiz_data["team_scores"][team_id] = {}

    for round_num in range(1, num_rounds + 1):
        st.subheader(f"Scores for Round {round_num}")
        for team_id, team_name in st.session_state.quiz_data["team_names"].items():
            score_key = f"team_{team_id}_round_{round_num}_score"
            score = st.number_input(f"Score for {team_name} in Round {round_num}", min_value=0, value=st.session_state.quiz_data["team_scores"].get(team_id, {}).get(round_num, 0), step=1, key=score_key)
            st.session_state.quiz_data["team_scores"][team_id][round_num] = score  # Update scores

    save_quiz_data()  # Save the quiz data to file whenever it changes

# Summary tab
with tabs[3]:
    st.header("Quiz Summary")

    # Calculate total scores
    total_scores = {}
    for team_id, scores in st.session_state.quiz_data["team_scores"].items():
        total_scores[team_id] = sum(scores.values())

    # Display scores
    sorted_scores = sorted(total_scores.items(), key=lambda x: x[1], reverse=True)
    for team_id, score in sorted_scores:
        st.write(f"{st.session_state.quiz_data['team_names'][team_id]}: {score} points")

    # Highlight the winner
    if sorted_scores:
        winner = st.session_state.quiz_data["team_names"][sorted_scores[0][0]]
        st.success(f"The winner is: {winner}!")
