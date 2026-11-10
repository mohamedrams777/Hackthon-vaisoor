import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Load our final models
from compute_context_adjusted_rankings import top_bat, top_bowl

# Output directory for plots
out_dir = r'C:\Users\Administrator\OneDrive\Desktop\RR_hackathon\figures'
os.makedirs(out_dir, exist_ok=True)

# 1. Top 10 Batters Plot
fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
bat10 = top_bat.head(10).iloc[::-1] # Reverse for horizontal bar chart

y_pos = np.arange(len(bat10))
ax.barh(y_pos, bat10['pri_bat_score'], color='#E63946', height=0.65, edgecolor='black', alpha=0.9)
ax.set_yticks(y_pos)
ax.set_yticklabels(bat10['striker_name'], fontsize=11, fontweight='bold')
ax.set_xlabel('Pressure Reliability Index (PRI Score)', fontsize=12, fontweight='bold')
ax.set_title('Top 10 Batters Under Pressure (SupeRR Selector)', fontsize=14, fontweight='bold', pad=15)
ax.set_xlim(50, 90)

for i, v in enumerate(bat10['pri_bat_score']):
    sr = bat10['sr_press'].iloc[i]
    avg = bat10['avg_press'].iloc[i]
    ax.text(v + 0.5, i, f"PRI: {v:.1f} | SR: {sr:.1f} | Avg: {avg:.1f}", va='center', fontsize=9, fontweight='semibold')

plt.tight_layout()
fig.savefig(os.path.join(out_dir, 'top_10_batters_pri.png'))
plt.close(fig)

# 2. Top 10 Bowlers Plot
fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
bowl10 = top_bowl.head(10).iloc[::-1]

y_pos = np.arange(len(bowl10))
ax.barh(y_pos, bowl10['pri_bowl_score'], color='#1D3557', height=0.65, edgecolor='black', alpha=0.9)
ax.set_yticks(y_pos)
ax.set_yticklabels(bowl10['bowler_name'], fontsize=11, fontweight='bold')
ax.set_xlabel('Pressure Reliability Index (PRI Score)', fontsize=12, fontweight='bold')
ax.set_title('Top 10 Bowlers Under Pressure (SupeRR Selector)', fontsize=14, fontweight='bold', pad=15)
ax.set_xlim(50, 95)

for i, v in enumerate(bowl10['pri_bowl_score']):
    econ = bowl10['econ_press'].iloc[i]
    wkts = bowl10['wickets_press'].iloc[i]
    ax.text(v + 0.5, i, f"PRI: {v:.1f} | Econ: {econ:.2f} | Wkts: {wkts}", va='center', fontsize=9, fontweight='semibold')

plt.tight_layout()
fig.savefig(os.path.join(out_dir, 'top_10_bowlers_pri.png'))
plt.close(fig)

# 3. Scatter Plot: Batters (Strike Rate vs Average under Pressure)
fig, ax = plt.subplots(figsize=(10, 7), dpi=300)
scatter = ax.scatter(
    top_bat['avg_press'], top_bat['sr_press'],
    s=top_bat['balls_press'] / 3.0,
    c=top_bat['pri_bat_score'],
    cmap='viridis',
    edgecolors='black',
    alpha=0.85
)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('PRI Score', fontsize=11, fontweight='bold')

for idx, r in top_bat.head(10).iterrows():
    ax.annotate(
        f"{r['rank']}. {r['striker_name']}",
        (r['avg_press'], r['sr_press']),
        xytext=(5, 4), textcoords='offset points',
        fontsize=9, fontweight='bold'
    )

ax.set_xlabel('Pressure Batting Average', fontsize=12, fontweight='bold')
ax.set_ylabel('Pressure Strike Rate', fontsize=12, fontweight='bold')
ax.set_title('Batters Under Pressure: Strike Rate vs Average (Bubble Size = Balls Faced)', fontsize=13, fontweight='bold', pad=15)
ax.grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
fig.savefig(os.path.join(out_dir, 'batters_scatter_sr_avg.png'))
plt.close(fig)

# 4. Scatter Plot: Bowlers (Economy vs Strike Rate under Pressure)
fig, ax = plt.subplots(figsize=(10, 7), dpi=300)
scatter = ax.scatter(
    top_bowl['sr_press'], top_bowl['econ_press'],
    s=top_bowl['balls_press'] / 3.0,
    c=top_bowl['pri_bowl_score'],
    cmap='coolwarm_r',
    edgecolors='black',
    alpha=0.85
)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('PRI Score', fontsize=11, fontweight='bold')

for idx, r in top_bowl.head(10).iterrows():
    ax.annotate(
        f"{r['rank']}. {r['bowler_name']}",
        (r['sr_press'], r['econ_press']),
        xytext=(5, 4), textcoords='offset points',
        fontsize=9, fontweight='bold'
    )

ax.set_xlabel('Bowling Strike Rate (Balls / Wicket under Pressure)', fontsize=12, fontweight='bold')
ax.set_ylabel('Pressure Economy Rate (Runs / Over)', fontsize=12, fontweight='bold')
ax.set_title('Bowlers Under Pressure: Economy vs Strike Rate (Bubble Size = Balls Bowled)', fontsize=13, fontweight='bold', pad=15)
ax.grid(True, linestyle='--', alpha=0.5)
ax.invert_xaxis() # Lower strike rate is better
ax.invert_yaxis() # Lower economy is better

plt.tight_layout()
fig.savefig(os.path.join(out_dir, 'bowlers_scatter_econ_sr.png'))
plt.close(fig)

print("All figures successfully saved to figures/ folder!")

