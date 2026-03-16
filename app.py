import streamlit as st
import pandas as pd

st.set_page_config(page_title="Tennis Rotations", layout="wide")
st.title("Tennis Rotations (4 rounds)")

st.write("Enter players (name, gender, rating), then click **Generate rotations**.")

# Editable input table
starter = pd.DataFrame(
    [
        {"name": "Alex", "gender": "M", "rating": 3.5},
        {"name": "Blair", "gender": "F", "rating": 3.0},
        {"name": "Casey", "gender": "M", "rating": 4.0},
        {"name": "Devon", "gender": "F", "rating": 2.5},
    ]
)

if "players_df" not in st.session_state:
    st.session_state.players_df = starter

players_df = st.data_editor(
    st.session_state.players_df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "name": st.column_config.TextColumn("Name", required=True),
        "gender": st.column_config.SelectboxColumn("Gender", options=["F", "M"], required=True),
        "rating": st.column_config.NumberColumn("Rating", min_value=0.0, max_value=10.0, step=0.5, required=True),
    },
)

def clean_players(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["name"] = df["name"].astype(str).str.strip()
    df = df[df["name"] != ""]
    df["gender"] = df["gender"].astype(str).str.strip().str.upper()
    df = df[df["gender"].isin(["F", "M"])]
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df = df.dropna(subset=["rating"])
    df = df.drop_duplicates(subset=["name"], keep="first")
    return df.reset_index(drop=True)

# ---- Replace this import + function with your real package call ----
import itertools
from collections import defaultdict
import random

class TennisScheduler:
    def __init__(self, players):
        """
        players: list of dicts with keys 'name', 'gender' ('M'/'F'), 'rating' (float)
        Example: [{'name': 'John', 'gender': 'M', 'rating': 4.5}, ...]
        """
        self.players = players
        self.men = [p for p in players if p['gender'] == 'M']
        self.women = [p for p in players if p['gender'] == 'F']
        self.team_history = defaultdict(int)  # Track team pairings
        self.court_history = defaultdict(int)  # Track court appearances together

    def calculate_team_rating(self, player1, player2):
        """Calculate average team rating"""
        return (player1['rating'] + player2['rating']) / 2

    def get_substitutes(self):
        """Determine which players can substitute for opposite gender"""
        substitutes = {'M_as_F': [], 'F_as_M': []}

        if len(self.men) > len(self.women):
            # Weaker men can substitute for women
            sorted_men = sorted(self.men, key=lambda x: x['rating'])
            n_subs_needed = (len(self.men) - len(self.women)) // 2
            substitutes['M_as_F'] = sorted_men[:n_subs_needed]
        elif len(self.women) > len(self.men):
            # Stronger women can substitute for men
            sorted_women = sorted(self.women, key=lambda x: x['rating'], reverse=True)
            n_subs_needed = (len(self.women) - len(self.men)) // 2
            substitutes['F_as_M'] = sorted_women[:n_subs_needed]

        return substitutes

    def create_pools(self):
        """Create gender-balanced pools accounting for substitutions"""
        subs = self.get_substitutes()

        pool_m = [p for p in self.men if p not in subs['M_as_F']]
        pool_f = [p for p in self.women if p not in subs['F_as_M']]
        pool_m.extend(subs['F_as_M'])  # Strong women play as "men"
        pool_f.extend(subs['M_as_F'])  # Weak men play as "women"

        return pool_m, pool_f

    def generate_teams(self, pool_m, pool_f):
        """Generate all possible teams"""
        teams = []
        for m in pool_m:
            for f in pool_f:
                teams.append({
                    'players': (m, f),
                    'rating': self.calculate_team_rating(m, f),
                    'names': f"{m['name']}/{f['name']}"
                })
        return teams

    def rate_matchup(self, team1, team2):
        """Rate how good a matchup is (lower is better)"""
        # Rating difference (want teams close in skill)
        rating_diff = abs(team1['rating'] - team2['rating'])

        # Penalty for repeat team pairings
        team1_key = tuple(sorted([p['name'] for p in team1['players']]))
        team2_key = tuple(sorted([p['name'] for p in team2['players']]))
        team_repeat_penalty = self.team_history[team1_key] + self.team_history[team2_key]

        # Penalty for players being on same court before
        court_players = [p['name'] for p in team1['players']] + [p['name'] for p in team2['players']]
        court_repeat_penalty = sum(self.court_history[tuple(sorted([p1, p2]))]
                                   for p1, p2 in itertools.combinations(court_players, 2))

        # Weighted score (adjust weights as needed)
        score = (rating_diff * 10) + (team_repeat_penalty * 5) + (court_repeat_penalty * 3)
        return score

    def find_best_match(self, available_teams, used_players):
        """Find the best match from available teams"""
        best_score = float('inf')
        best_match = None

        # Filter teams that don't use already-used players
        valid_teams = [t for t in available_teams
                       if all(p['name'] not in used_players for p in t['players'])]

        # Try all combinations
        for i, team1 in enumerate(valid_teams):
            for team2 in valid_teams[i+1:]:
                # Check no player overlap
                players1 = {p['name'] for p in team1['players']}
                players2 = {p['name'] for p in team2['players']}
                if players1.isdisjoint(players2):
                    score = self.rate_matchup(team1, team2)
                    if score < best_score:
                        best_score = score
                        best_match = (team1, team2)

        return best_match

    def update_history(self, team1, team2):
        """Update pairing and court history"""
        # Update team history
        team1_key = tuple(sorted([p['name'] for p in team1['players']]))
        team2_key = tuple(sorted([p['name'] for p in team2['players']]))
        self.team_history[team1_key] += 1
        self.team_history[team2_key] += 1

        # Update court history (all 4 players were on same court)
        court_players = [p['name'] for p in team1['players']] + [p['name'] for p in team2['players']]
        for p1, p2 in itertools.combinations(court_players, 2):
            self.court_history[tuple(sorted([p1, p2]))] += 1

    def schedule_round(self, pool_m, pool_f):
        """Schedule one round of matches"""
        teams = self.generate_teams(pool_m, pool_f)
        matches = []
        used_players = set()

        # Generate matches until we can't make more
        while True:
            match = self.find_best_match(teams, used_players)
            if match is None:
                break

            team1, team2 = match
            matches.append({
                'court': len(matches) + 1,
                'team1': team1,
                'team2': team2,
                'rating_diff': abs(team1['rating'] - team2['rating'])
            })

            # Mark players as used
            for p in team1['players'] + team2['players']:
                used_players.add(p['name'])

            # Update history
            self.update_history(team1, team2)

        return matches

    def schedule_tournament(self, num_rounds=4):
        """Schedule multiple rounds"""
        pool_m, pool_f = self.create_pools()

        print(f"Scheduling {num_rounds} rounds of mixed doubles")
        print(f"Pool sizes: {len(pool_m)} 'men', {len(pool_f)} 'women'")
        print("=" * 80)

        all_rounds = []
        for round_num in range(1, num_rounds + 1):
            print(f"\n### ROUND {round_num} ###")
            matches = self.schedule_round(pool_m, pool_f)
            all_rounds.append(matches)

            for match in matches:
                print(f"\nCourt {match['court']}:")
                print(f"  {match['team1']['names']} (avg: {match['team1']['rating']:.2f})")
                print(f"    vs")
                print(f"  {match['team2']['names']} (avg: {match['team2']['rating']:.2f})")
                print(f"  Rating difference: {match['rating_diff']:.2f}")

        self.print_statistics()
        return all_rounds

    def print_statistics(self):
        """Print pairing statistics"""
        print("\n" + "=" * 80)
        print("STATISTICS")
        print("=" * 80)

        print("\nTeam Pairings (count):")
        sorted_teams = sorted(self.team_history.items(), key=lambda x: x[1], reverse=True)
        for team, count in sorted_teams[:10]:  # Top 10
            print(f"  {team[0]} & {team[1]}: {count} times")

        print("\nMost Common Court Pairings (players on same court):")
        sorted_courts = sorted(self.court_history.items(), key=lambda x: x[1], reverse=True)
        for pair, count in sorted_courts[:10]:  # Top 10
            print(f"  {pair[0]} & {pair[1]}: {count} times")

scheduler = TennisScheduler(players_list)
rounds = scheduler.schedule_tournament(num_rounds=4)
# -------------------------------------------------------------------

col1, col2 = st.columns([1, 3])
with col1:
    generate = st.button("Generate rotations", type="primary")

with col2:
    st.caption("Tip: You can add/remove rows. Names must be unique.")

if generate:
    st.session_state.players_df = players_df

    cleaned = clean_players(players_df)

    if len(cleaned) == 0:
        st.error("Please enter at least one valid player.")
        st.stop()

    # If your rules require a multiple of 4, enforce it here:
    if len(cleaned) % 4 != 0:
        st.error(f"You entered {len(cleaned)} players. This scheduler requires a multiple of 4.")
        st.stop()

    try:
        rotations = generate_rotations(cleaned)  # <-- connect your real code here
    except Exception as e:
        st.exception(e)
        st.stop()

    if not isinstance(rotations, (list, tuple)) or len(rotations) != 4:
        st.error("Your generator must return a list of 4 rotation tables.")
        st.stop()

    st.divider()
    st.subheader("Rotations")

    for i, rot in enumerate(rotations, start=1):
        st.markdown(f"### Rotation {i}")
        st.dataframe(rot, use_container_width=True, hide_index=True)

    # Optional: download all rotations as a single CSV file
    st.divider()
    all_rows = []
    for i, rot in enumerate(rotations, start=1):
        temp = rot.copy()
        temp.insert(0, "rotation", i)
        all_rows.append(temp)
    all_df = pd.concat(all_rows, ignore_index=True)

    st.download_button(
        "Download all rotations (CSV)",
        data=all_df.to_csv(index=False).encode("utf-8"),
        file_name="tennis_rotations.csv",
        mime="text/csv",
    )
