import os
import pandas as pd
import numpy as np

data_dir = r'C:\Users\Administrator\OneDrive\Desktop\RR_hackathon\data'
df = pd.read_csv(os.path.join(data_dir, 'ball_by_ball.csv'))
matches = pd.read_csv(os.path.join(data_dir, 'matches.csv'))
comps = pd.read_csv(os.path.join(data_dir, 'competitions.csv'))

print(f"Total balls: {len(df)}")
print(f"Total matches: {df['match_id'].nunique()}")

# Check unique batters and bowlers
print(f"Unique strikers: {df['striker_id'].nunique()}")
print(f"Unique bowlers: {df['bowler_id'].nunique()}")

# Check balls faced distribution for batters
batter_balls = df.groupby('striker_name').size().sort_values(ascending=False)
print("\nTop 15 batters by balls faced:")
print(batter_balls.head(15))

# Check balls bowled distribution for bowlers
bowler_balls = df.groupby('bowler_name').size().sort_values(ascending=False)
print("\nTop 15 bowlers by balls bowled:")
print(bowler_balls.head(15))

