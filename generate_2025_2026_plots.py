import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Load 2025-2026 rankings
target_dir = r'C:\Users\Administrator\OneDrive\Desktop\RR_hackathon\2025-2026'
top_bat = pd.read_csv(os.path.join(target_dir, 'top_20_batters_2025_2026.csv'))
top_bowl = pd.read_csv(os.path.join(target_dir, 'top_20_bowlers_2025_2026.csv'))

# 1. Top 20 Batters Horizontal Bar Chart
fig, ax = plt.subplots(figsize=(12, 10), dpi=300)
bat20 = top_bat.iloc[::-1] # Reverse so Rank 1 is on top

y_pos = np.arange(len(bat20))
colors = plt.cm.plasma(np.linspace(0.2, 0.85, len(bat20)))

bars = ax.barh(y_pos, bat20['pri_bat_score'], color=colors, height=0.7, edgecolor='black', alpha=0.9)
ax.set_yticks(y_pos)
ax.set_yticklabels([f"{r['rank']}. {r['striker_name']}" for _, r in bat20.iterrows()], fontsize=10, fontweight='bold')
ax.set_xlabel('Pressure Reliability Index (PRI Score)', fontsize=12, fontweight='bold')
ax.set_title('Top 20 Batters Under Pressure (2025–2026 Season)', fontsize=14, fontweight='bold', pad=15)
ax.set_xlim(50, 85)

for i, (_, r) in enumerate(bat20.iterrows()):
    ax.text(r['pri_bat_score'] + 0.4, i, f"PRI: {r['pri_bat_score']:.1f} | SR: {r['sr_press']:.1f} | Avg: {r['avg_press']:.1f}", va='center', fontsize=8.5, fontweight='semibold')

plt.tight_layout()
fig.savefig(os.path.join(target_dir, 'top_20_batters_2025_2026.png'))
plt.close(fig)

# 2. Top 20 Bowlers Horizontal Bar Chart
fig, ax = plt.subplots(figsize=(12, 10), dpi=300)
bowl20 = top_bowl.iloc[::-1]

y_pos = np.arange(len(bowl20))
colors = plt.cm.viridis(np.linspace(0.2, 0.85, len(bowl20)))

bars = ax.barh(y_pos, bowl20['pri_bowl_score'], color=colors, height=0.7, edgecolor='black', alpha=0.9)
ax.set_yticks(y_pos)
ax.set_yticklabels([f"{r['rank']}. {r['bowler_name']}" for _, r in bowl20.iterrows()], fontsize=10, fontweight='bold')
ax.set_xlabel('Pressure Reliability Index (PRI Score)', fontsize=12, fontweight='bold')
ax.set_title('Top 20 Bowlers Under Pressure (2025–2026 Season)', fontsize=14, fontweight='bold', pad=15)
ax.set_xlim(50, 90)

for i, (_, r) in enumerate(bowl20.iterrows()):
    ax.text(r['pri_bowl_score'] + 0.4, i, f"PRI: {r['pri_bowl_score']:.1f} | Econ: {r['econ_press']:.2f} | Wkts: {r['wickets_press']}", va='center', fontsize=8.5, fontweight='semibold')

plt.tight_layout()
fig.savefig(os.path.join(target_dir, 'top_20_bowlers_2025_2026.png'))
plt.close(fig)

# 3. Batters Scatter Plot 2025-2026
fig, ax = plt.subplots(figsize=(11, 7), dpi=300)
scatter = ax.scatter(
    top_bat['avg_press'], top_bat['sr_press'],
    s=top_bat['balls_press'] * 1.2,
    c=top_bat['pri_bat_score'],
    cmap='magma',
    edgecolors='black',
    alpha=0.85
)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('PRI Score (2025-2026)', fontsize=11, fontweight='bold')

for idx, r in top_bat.head(10).iterrows():
    ax.annotate(
        f"{r['rank']}. {r['striker_name']}",
        (r['avg_press'], r['sr_press']),
        xytext=(5, 4), textcoords='offset points',
        fontsize=9, fontweight='bold'
    )

ax.set_xlabel('Pressure Batting Average', fontsize=12, fontweight='bold')
ax.set_ylabel('Pressure Strike Rate', fontsize=12, fontweight='bold')
ax.set_title('2025–2026 Batters: Strike Rate vs Average Under Pressure (Bubble Size = Balls Faced)', fontsize=13, fontweight='bold', pad=15)
ax.grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
fig.savefig(os.path.join(target_dir, 'batters_scatter_2025_2026.png'))
plt.close(fig)

# 4. Bowlers Scatter Plot 2025-2026
fig, ax = plt.subplots(figsize=(11, 7), dpi=300)
scatter = ax.scatter(
    top_bowl['sr_press'], top_bowl['econ_press'],
    s=top_bowl['balls_press'] * 1.2,
    c=top_bowl['pri_bowl_score'],
    cmap='cividis',
    edgecolors='black',
    alpha=0.85
)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('PRI Score (2025-2026)', fontsize=11, fontweight='bold')

for idx, r in top_bowl.head(10).iterrows():
    ax.annotate(
        f"{r['rank']}. {r['bowler_name']}",
        (r['sr_press'], r['econ_press']),
        xytext=(5, 4), textcoords='offset points',
        fontsize=9, fontweight='bold'
    )

ax.set_xlabel('Bowling Strike Rate (Balls / Wicket under Pressure)', fontsize=12, fontweight='bold')
ax.set_ylabel('Pressure Economy Rate (Runs / Over)', fontsize=12, fontweight='bold')
ax.set_title('2025–2026 Bowlers: Economy vs Strike Rate Under Pressure (Bubble Size = Balls Bowled)', fontsize=13, fontweight='bold', pad=15)
ax.grid(True, linestyle='--', alpha=0.5)
ax.invert_xaxis()
ax.invert_yaxis()

plt.tight_layout()
fig.savefig(os.path.join(target_dir, 'bowlers_scatter_2025_2026.png'))
plt.close(fig)

print("2025-2026 visual charts successfully generated!")

