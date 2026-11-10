import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score

data_dir = r'C:\Users\Administrator\OneDrive\Desktop\RR_hackathon\data'
df = pd.read_csv(os.path.join(data_dir, 'ball_by_ball.csv'))
matches = pd.read_csv(os.path.join(data_dir, 'matches.csv'))
comps = pd.read_csv(os.path.join(data_dir, 'competitions.csv'))

# Match metadata
matches_info = matches[['match_id', 'comp_id', 'stage', 'knock_out', 'win_team_id', 'result', 'revised_target', 'first_inn_revised_overs', 'second_inn_revised_overs']]
matches_info = matches_info.merge(comps[['comp_id', 'comp_name', 'match_format', 'season']], on='comp_id', how='left')

df = df.merge(matches_info, on='match_id', how='left')
df['is_legal_ball'] = ~df['extras_type'].isin(['wide', 'Overstep'])

def get_ball_team_runs(row):
    r = row['runs']
    ext_type = row['extras_type']
    ext2 = row['extras_2_runs'] if pd.notna(row['extras_2_runs']) else 0
    extras = 1 if ext_type in ['wide', 'legbyes', 'byes', 'Overstep', 'other'] else 0
    return r + extras + ext2

df['ball_team_runs'] = df.apply(get_ball_team_runs, axis=1)
df['cum_team_runs'] = df.groupby(['match_id', 'innings'])['ball_team_runs'].cumsum()
df['cum_wickets'] = df.groupby(['match_id', 'innings'])['is_wicket'].cumsum()
df['legal_balls_bowled'] = df.groupby(['match_id', 'innings'])['is_legal_ball'].cumsum()

# 1st innings total
inn1_totals = df[df['innings'] == 1].groupby('match_id')['cum_team_runs'].max().reset_index()
inn1_totals.rename(columns={'cum_team_runs': 'inn1_final_runs'}, inplace=True)
df = df.merge(inn1_totals, on='match_id', how='left')

df['target'] = np.where(df['revised_target'].notna(), df['revised_target'], df['inn1_final_runs'] + 1)
df['runs_needed'] = df['target'] - df['cum_team_runs'] + df['ball_team_runs']
df['max_legal_balls'] = np.where(df['second_inn_revised_overs'].notna(), df['second_inn_revised_overs'] * 6, 120)
df['balls_remaining'] = np.maximum(0, df['max_legal_balls'] - df['legal_balls_bowled'] + df['is_legal_ball'].astype(int))
df['wickets_in_hand'] = 10 - (df['cum_wickets'] - df['is_wicket'].astype(int))
df['rrr'] = np.where(df['balls_remaining'] > 0, df['runs_needed'] / (df['balls_remaining'] / 6.0), np.nan)

# Target for logistic regression: did batting team win?
chase_df = df[(df['innings'] == 2) & (df['balls_remaining'] > 0) & (df['runs_needed'] > 0) & (df['wickets_in_hand'] > 0)].copy()
chase_df['batting_won'] = (chase_df['win_team_id'] == chase_df['batting_team_id']).astype(int)

features = ['runs_needed', 'balls_remaining', 'wickets_in_hand', 'rrr']
chase_df = chase_df.dropna(subset=features + ['batting_won'])

model = LogisticRegression(max_iter=1000)
model.fit(chase_df[features], chase_df['batting_won'])

preds = model.predict_proba(chase_df[features])[:, 1]
print("AUC of 2nd innings Win Probability Model:", roc_auc_score(chase_df['batting_won'], preds))
print("Log Loss:", log_loss(chase_df['batting_won'], preds))
print("Coefficients:", dict(zip(features, model.coef_[0])))
print("Intercept:", model.intercept_[0])

