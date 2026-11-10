import pandas as pd
from compute_context_adjusted_rankings import top_bat, top_bowl

# Save CSVs
top_bat.head(10).to_csv('top_10_batters_under_pressure.csv', index=False)
top_bowl.head(10).to_csv('top_10_bowlers_under_pressure.csv', index=False)
top_bat.to_csv('all_qualified_batters_pressure_rankings.csv', index=False)
top_bowl.to_csv('all_qualified_bowlers_pressure_rankings.csv', index=False)

print("CSVs successfully exported to workspace root!")

