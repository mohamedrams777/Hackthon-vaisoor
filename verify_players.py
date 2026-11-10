import pandas as pd

ctpm = pd.read_csv('data/competition_team_player_mapping.csv')
bbb = pd.read_csv('data/ball_by_ball.csv')

batters = ['Suryakumar Yadav', 'Dinesh Karthik', 'Shashank Singh', 'Tim David', 'Namboori Tilak Varma', 'Tristan Stubbs', 'Heinrich Klaasen', 'Rinku Singh', 'Rishabh Pant', 'Jos Buttler']
bowlers = ['Sunil Narine', 'Abrar Ahmed', 'Jasprit Bumrah', 'Mitchell Santner', 'Rashid Khan', 'Akeal Hosein', 'Matheesha Pathirana', 'Varun Chakravarthy', 'Kuldeep Yadav', 'Mustafizur Rahman']

print('--- Batters in mapping & BBB ---')
for b in batters:
    m = ctpm[ctpm['player_name'].str.lower() == b.lower()]
    b_match = bbb[bbb['striker_name'].str.lower() == b.lower()]
    pid = b_match['striker_id'].iloc[0] if len(b_match) > 0 else 'N/A'
    pname = b_match['striker_name'].iloc[0] if len(b_match) > 0 else 'N/A'
    print(f"{b:22s} -> ID: {pid} | Match Name: {pname} | Found in mapping: {len(m) > 0}")

print('\n--- Bowlers in mapping & BBB ---')
for b in bowlers:
    m = ctpm[ctpm['player_name'].str.lower() == b.lower()]
    b_match = bbb[bbb['bowler_name'].str.lower() == b.lower()]
    pid = b_match['bowler_id'].iloc[0] if len(b_match) > 0 else 'N/A'
    pname = b_match['bowler_name'].iloc[0] if len(b_match) > 0 else 'N/A'
    print(f"{b:22s} -> ID: {pid} | Match Name: {pname} | Found in mapping: {len(m) > 0}")

