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


# Example usage
#if __name__ == "__main__":
    # Sample player data
   # players = [
        {'name': 'Alice', 'gender': 'F', 'rating': 4.5},
        {'name': 'Bob', 'gender': 'M', 'rating': 4.0},
        {'name': 'Carol', 'gender': 'F', 'rating': 3.5},
        {'name': 'Dave', 'gender': 'M', 'rating': 4.5},
        {'name': 'Eve', 'gender': 'F', 'rating': 4.0},
        {'name': 'Frank', 'gender': 'M', 'rating': 3.0},
        {'name': 'Grace', 'gender': 'F', 'rating': 3.5},
        {'name': 'Henry', 'gender': 'M', 'rating': 4.0},
        {'name': 'Iris', 'gender': 'F', 'rating': 4.5},
        {'name': 'Jack', 'gender': 'M', 'rating': 3.5},
 #   ]

print("Ready")
