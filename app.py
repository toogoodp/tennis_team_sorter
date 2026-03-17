import streamlit as st
import pandas as pd
import itertools
from collections import defaultdict

st.set_page_config(page_title="Tennis Rotations", layout="wide")
st.title("Tennis Rotations (4 rounds)")

# Initialize session state
if 'rotations' not in st.session_state:
    st.session_state.rotations = None

st.write("Enter players (name, gender, rating), then click **Generate rotations**.")

# Player input section
st.subheader("Step 1: Enter Players")
players_df = st.data_editor(
    pd.DataFrame(columns=['Name', 'Gender', 'Rating']),
    num_rows="dynamic",
    use_container_width=True,
    key="players_table"
)

# Validation and generation button
col1, col2 = st.columns([1, 3])
with col1:
    generate = st.button("Generate rotations", type="primary")

with col2:
    st.caption("Tip: You can add/remove rows. Names must be unique.")

if generate:
    # Validate input
    if players_df.empty or players_df.isna().any().any():
        st.error("Please enter at least one complete player entry (Name, Gender, Rating).")
        st.stop()
    
    # Convert to list format
    players_list = []
    for _, row in players_df.iterrows():
        players_list.append({
            'name': row['Name'],
            'gender': row['Gender'].upper(),
            'rating': float(row['Rating'])
        })
    
    # Run scheduler
    try:
        scheduler = TennisScheduler(players_list)
        st.session_state.rotations = scheduler.schedule_tournament(num_rounds=4)
        st.success("Rotations generated successfully!")
    except Exception as e:
        st.error(f"Error generating rotations: {e}")
        st.stop()

# Display results
if st.session_state.rotations:
    st.divider()
    st.subheader("Rotations")
    
    for i, matches in enumerate(st.session_state.rotations, start=1):
        st.markdown(f"### Round {i}")
        # Format matches for display
        round_data = []
        for match in matches:
            round_data.append({
                'Court': match['court'],
                'Team 1': match['team1']['names'],
                'Team 1 Rating': f"{match['team1']['rating']:.2f}",
                'Team 2': match['team2']['names'],
                'Team 2 Rating': f"{match['team2']['rating']:.2f}",
                'Rating Diff': f"{match['rating_diff']:.2f}"
            })
        st.dataframe(pd.DataFrame(round_data), use_container_width=True, hide_index=True)
