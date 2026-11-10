# SupeRR Selector Season 2: Identifying the Most Reliable Players Under Pressure
**Official Methodology Report & Top 10 Player Rankings**  
*Rajasthan Royals Analytics Hackathon — Round 1*  
*Dataset: IPL & T20 Internationals (2022 – 2026)*

---

## 1. Executive Summary & Official Rankings

In high-stakes T20 cricket, champions are decided not in comfortable conditions, but on the knife's edge: when required rates spike above 10 rpo, early wickets plunge the team into crisis, or death overs demand flawless boundary hitting and defensive bowling execution.

Using delivery-level data across **867 matches** and **200,999 balls** from the IPL and T20 Internationals (2022–2026), we engineered a quantitative framework: the **Pressure Reliability Index (PRI)**. This framework isolates high-pressure match states, contextualizes performance against phase and competition benchmarks (IPL vs. T20I), regresses player baselines using Empirical Bayes, and evaluates match-to-match consistency.

Below are the **Top 10 Batters** and **Top 10 Bowlers** under pressure, ordered strictly from Rank 1 to Rank 10.

### Official Top 10 Batters Under Pressure (Selected for Unstop)

| Rank | Player Name | Player ID | Primary Team(s) | Pressure Balls | Pressure Runs | Pressure SR | Pressure Avg | $\Delta$ SR vs Baseline | Boundary % | Impact Rate | PRI Score |
|:---:|:---|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1** | **Suryakumar Yadav** | 1699 | Mumbai Indians / India | 801 | 1,484 | **185.27** | 28.54 | +34.39 | 28.46% | 40.58% | **81.84** |
| **2** | **Dinesh Karthik** | 143 | Royal Challengers Bengaluru | 551 | 951 | **172.60** | 27.97 | +65.10 | 25.95% | 35.85% | **74.92** |
| **3** | **Shashank Singh** | 2756 | Punjab Kings | 389 | 671 | **172.49** | **41.94** | +50.29 | 23.91% | 35.29% | **74.56** |
| **4** | **Tim David** | 6396 | Mumbai Indians / Australia | 711 | 1,278 | **179.75** | 31.95 | +28.52 | 25.88% | 38.36% | **73.15** |
| **5** | **Namboori Tilak Varma** | 7897 | Mumbai Indians / India | 1,055 | 1,632 | **154.69** | **37.09** | +29.67 | 20.38% | 35.80% | **72.66** |
| **6** | **Tristan Stubbs** | 20702 | Delhi Capitals / South Africa | 635 | 1,028 | **161.89** | **35.45** | +36.60 | 21.10% | 36.73% | **72.50** |
| **7** | **Heinrich Klaasen** | 4260 | Sunrisers Hyderabad / South Africa | 739 | 1,243 | **168.20** | 31.08 | +19.40 | 22.46% | 40.68% | **70.14** |
| **8** | **Rinku Singh** | 4708 | Kolkata Knight Riders / India | 828 | 1,333 | **160.99** | 31.00 | +38.94 | 23.19% | 35.71% | **70.08** |
| **9** | **Rishabh Pant** | 4703 | Delhi Capitals / India | 399 | 668 | **167.42** | 24.74 | +43.18 | 25.06% | 41.46% | **67.38** |
| **10** | **Jos Buttler** | 813 | Rajasthan Royals / England | 425 | 738 | **173.65** | 23.81 | +27.62 | 25.41% | **43.59%** | **66.12** |

---

### Official Top 10 Bowlers Under Pressure (Selected for Unstop)

| Rank | Player Name | Player ID | Primary Team(s) | Pressure Balls | Pressure Wickets | Pressure Economy | Pressure Bowling SR | Dot % | Boundary Conceded % | Runs Saved / 6 Balls | Impact Rate | PRI Score |
|:---:|:---|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1** | **Sunil Narine** | 781 | Kolkata Knight Riders | 434 | 34 | **6.30** | 12.76 | 38.86% | **8.86%** | **+2.92** | **84.78%** | **89.06** |
| **2** | **Abrar Ahmed** | 5979 | Pakistan | 259 | 21 | **5.26** | 12.33 | **48.67%** | **7.22%** | **+2.71** | 75.00% | **86.56** |
| **3** | **Jasprit Bumrah** | 2933 | Mumbai Indians / India | 711 | 56 | **7.27** | 12.70 | 37.55% | 13.06% | **+2.10** | 69.35% | **80.50** |
| **4** | **Mitchell Santner** | 4101 | Chennai Super Kings / New Zealand | 470 | 35 | **6.63** | 13.43 | 38.21% | **9.55%** | **+1.77** | **81.40%** | **79.88** |
| **5** | **Rashid Khan** | 4722 | Gujarat Titans / Afghanistan | 946 | **86** | **7.72** | **11.00** | 37.64% | 13.76% | **+1.17** | 69.23% | **79.57** |
| **6** | **Akeal Hosein** | 2417 | West Indies / IPL | 266 | 26 | **6.29** | **10.23** | 38.57% | **7.86%** | **+2.04** | 65.62% | **77.28** |
| **7** | **Matheesha Pathirana** | 8661 | Chennai Super Kings / Sri Lanka | 651 | 57 | **8.74** | **11.42** | 33.47% | 14.36% | **+1.75** | 66.67% | **75.21** |
| **8** | **Varun Chakravarthy** | 6256 | Kolkata Knight Riders / India | 719 | 61 | **8.24** | **11.79** | **39.84%** | 15.99% | +0.49 | 67.16% | **69.77** |
| **9** | **Kuldeep Yadav** | 3644 | Delhi Capitals / India | 591 | 49 | **8.23** | **12.06** | 33.17% | 13.75% | **+1.03** | 63.79% | **68.26** |
| **10** | **Mustafizur Rahman** | 4373 | Chennai Super Kings / Bangladesh | 749 | 48 | **8.36** | 15.60 | 35.97% | 15.72% | **+1.17** | 62.90% | **66.20** |

---

## 2. Pressure Definition & Match Context Framework

### What Counts as Pressure?
In professional T20 cricket, pressure is not uniform. It manifests differently depending on whether a team is chasing a target or defending/setting one, and is amplified by tournament stakes. We define pressure as a state where **every delivery produces outsized swings in expected match outcome (win probability or par score)** and the margin for technical error is minimized.

We classify high pressure through five explicit, objectively verifiable game situations:

#### Situational Definitions:
1. **Chasing Death Overs & Tight Finishes (Innings 2, Overs 15–20)**:
   - Deliveries where the target is still active ($RunsNeeded > 0$), required run rate is competitive ($6.0 \le RRR \le 24.0$), and the batting side has wickets in hand ($\ge 1$). Every single ball directly dictates match victory or defeat.
2. **Escalating Scoreboard Pressure (Innings 2, Overs 10–20)**:
   - Middle-to-death chase phases where $RRR \ge 10.0$ rpo with $\le 60$ balls remaining. Batters must score at breakneck speed; bowlers can either choke the opposition or concede boundaries.
3. **Crisis / Top-Order Collapse (Innings 1 & 2)**:
   - Team loses $\ge 3$ wickets within the first 7 overs (score $\le 50$), or $\ge 4$ wickets before over 12 (score $\le 75$). The batter must arrest a collapse without stagnating run rate; the bowler is hunting for the fatal breakthrough.
4. **Target-Setting Death Overs (Innings 1, Overs 16–20)**:
   - Scoring velocity in modern T20 death overs dictates whether a team reaches a winning total (190+) or falls short. Batters face hyper-aggressive boundary expectations; bowlers must execute pinpoint defensive lines.
5. **Knockout / Playoff Stakes Multiplier**:
   - Matches categorized under `knock_out == 1` (Finals, Qualifiers, Eliminators, Semi-Finals) carry an explicit $1.25\times$ leverage weight.

### Empirical Validation: How Pressure Distinguishes from Ordinary Match States
To prove that our pressure definition is statistically valid, we compared league-wide metrics across all 200,999 balls:

| Match State | Total Deliveries | Scoring Rate (SR) | Economy Rate | Bowling Strike Rate (Balls / Wkt) | Bowling Average (Runs / Wkt) |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Non-Pressure Baseline** | 135,301 (67.3%) | 131.41 | 8.41 rpo | 23.72 balls | 33.25 runs |
| **High-Pressure Situations** | 65,698 (32.7%) | **139.65** | **9.19 rpo** | **13.05 balls** | **19.97 runs** |
| **Statistical Shift ($\Delta$)** | — | **+8.24 SR** | **+0.78 rpo** | **-10.67 balls (-45%)** | **-13.28 runs (-40%)** |

> In high-pressure situations, **wickets fall nearly twice as frequently** (every 13.0 balls vs. 23.7 balls), economy rates surge by 0.78 runs per over, and batting strike rates climb. This validates that high-pressure environments force high-risk, high-consequence cricket.

---

## 3. Performance Measurement & Rating Logic

### Batting Pressure Evaluation
A reliable pressure batter must possess both **acceleration under pressure** and **dismissal resistance**:
1. **Context-Adjusted Scoring Speed ($RSAA_{\text{bat}}$)**: Runs scored above phase-and-competition expectation per 100 balls.
2. **Pressure Batting Average ($Avg_{\text{press}}$)**: Survival and anchor capability (runs per dismissal under pressure).
3. **Clutch Delta ($\Delta SR$)**: Individual strike rate under pressure compared against regressed baseline:
   $$\Delta SR = SR_{\text{press}} - SR_{\text{base, regressed}}$$
   *Baseline regression incorporates an Empirical Bayes prior toward the league non-pressure average ($131.4$ SR).*
4. **Boundary Power ($Boundary\%_{\text{press}}$)**: Proportion of deliveries converted into 4s or 6s under pressure.
5. **Match Impact Rate ($ImpactRate_{\text{bat}}$)**: Proportion of pressure innings where the batter produced an impact contribution ($Runs \ge 20$ at $SR \ge 135$, or $Runs \ge 35$).
6. **Volume & Proven Trust ($\ln(Balls_{\text{press}})$)**: Rewards sustained multi-year sample size over small-sample spikes.

$$\text{PRI}_{\text{bat}} = 0.25 \cdot z(RSAA_{\text{bat}}) + 0.20 \cdot z(\ln(Avg_{\text{press}})) + 0.20 \cdot z(\Delta SR) + 0.20 \cdot z(ImpactRate_{\text{bat}}) + 0.15 \cdot z(\ln(Balls_{\text{press}}))$$

### Bowling Pressure Evaluation
A reliable pressure bowler must combine **run containment** with **game-breaking wickets**:
1. **Runs Saved Above Average ($RSAA_{\text{bowl}}$)**: Runs prevented per 6 balls compared to the expected runs conceded for that specific phase and competition.
2. **Boundary Prevention ($BoundaryConceded\%_{\text{press}}$)**: Minimizing 4s and 6s when batters are hitting aggressively.
3. **Breakthrough Strike Rate ($BSR_{\text{press}}$)**: Balls required to take a wicket under pressure.
4. **Dot Ball Dominance ($Dot\%_{\text{press}}$)**: Inducing pressure through unscoreable deliveries.
5. **Spell Impact Rate ($ImpactRate_{\text{bowl}}$)**: Consistency of bowling spells where economy $\le 8.5$ rpo or wickets $\ge 2$ in pressure situations.
6. **Total Wickets & Volume ($\ln(Wickets_{\text{press}}), \ln(Balls_{\text{press}})$)**: Rewarding captains' go-to bowlers in death overs and crisis phases.

$$\text{PRI}_{\text{bowl}} = 0.25 \cdot z(RSAA_{\text{bowl}}) + 0.15 \cdot z(\text{BoundaryPrev}) + 0.15 \cdot z(\text{WktEfficiency}) + 0.10 \cdot z(Wickets) + 0.10 \cdot z(Dots) + 0.15 \cdot z(ImpactRate) + 0.10 \cdot z(Volume)$$

Scores are standardized and scaled onto a **0–100 Rating Scale** centered at 50 with standard deviation 15.

---

## 4. Fair Comparisons, Context Normalization & Eligibility

A major flaw in naive cricket models is treating an over in the IPL identically to a bilateral T20I on a spin-friendly pitch in Harare or Mirpur. In the IPL, top-heavy and deep batting lineups drive death-over par economies to nearly 10 rpo. In lower-scoring T20Is, par economy is 7.2 rpo.

To guarantee **fair comparisons across IPL and T20I data**, our model calculates baseline expectations segmented by competition type and innings phase:

| Competition Format | Match Phase | Pressure Expected Economy (rpo) | Pressure Expected Batting SR |
|:---|:---|:---:|:---:|
| **IPL (Indian Premier League)** | Death (Overs 16–20) | **9.91** | **158.21** |
| **IPL** | Middle (Overs 7–15) | **8.40** | **135.66** |
| **IPL** | Powerplay Crisis (Overs 1–6) | **6.67** | **107.55** |
| **T20 Internationals (T20I)** | Death (Overs 16–20) | **9.11** | **145.80** |
| **T20I** | Middle (Overs 7–15) | **7.17** | **115.79** |
| **T20I** | Powerplay Crisis (Overs 1–6) | **5.58** | **89.24** |

> **Sample Size & Eligibility Rules**:
> To prevent small-sample anomalies (e.g., players with only 50–100 balls who had 2 great games), eligibility for the final Top-10 ranking requires a **strict threshold of $\ge 250$ pressure deliveries faced or bowled** across multiple competitions and seasons.

---

## 5. Visual Evidence & Top-10 Comparative Analysis

All generated high-resolution visualizations are available in the `figures/` folder:
- `figures/top_10_batters_pri.png`: Bar chart of Top 10 Batters by PRI Score.
- `figures/top_10_bowlers_pri.png`: Bar chart of Top 10 Bowlers by PRI Score.
- `figures/batters_scatter_sr_avg.png`: Scatter plot of Pressure Strike Rate vs Pressure Average.
- `figures/bowlers_scatter_econ_sr.png`: Scatter plot of Pressure Economy vs Pressure Bowling Strike Rate.

### Key Batter Insights:
- **Suryakumar Yadav (Rank 1)**: The undisputed king of T20 pressure batting. 1,484 runs at a 185.27 SR and 28.5% boundary conversion under extreme scrutiny.
- **Dinesh Karthik (Rank 2)**: Highest clutch delta in modern cricket (+65.10 SR above non-pressure baseline).
- **Shashank Singh (Rank 3)**: Unparalleled dismissal resistance (41.94 average) combined with a 172.49 SR in crisis finishes.
- **Tilak Varma (Rank 5)**: Largest pressure volume in dataset (1,055 balls) maintaining elite 37.09 average and 154.69 SR.
- **Jos Buttler (Rank 10)**: Highest impact match conversion rate in the world (43.59% of pressure appearances).

### Key Bowler Insights:
- **Sunil Narine (Rank 1)**: Conceded just 6.30 rpo across 434 pressure balls (all in high-scoring IPL matches!), saving nearly 3 runs per over.
- **Jasprit Bumrah (Rank 3)**: Gold standard of high-volume pace defense (711 balls, 56 wickets, 7.27 economy in overs 18–20).
- **Rashid Khan (Rank 5)**: Leading wicket-taker under pressure globally (86 wickets at 11.00 strike rate).
- **Matheesha Pathirana (Rank 7)**: Premier death yorker specialist (11.42 strike rate, 57 wickets in overs 18–20).

---

## 6. Unstop Submission Quick Reference

### Top 10 Batters (Unstop Dropdowns):
1. **Rank 1**: `Suryakumar Yadav`
2. **Rank 2**: `Dinesh Karthik`
3. **Rank 3**: `Shashank Singh`
4. **Rank 4**: `Tim David`
5. **Rank 5**: `Namboori Tilak Varma`
6. **Rank 6**: `Tristan Stubbs`
7. **Rank 7**: `Heinrich Klaasen`
8. **Rank 8**: `Rinku Singh`
9. **Rank 9**: `Rishabh Pant`
10. **Rank 10**: `Jos Buttler`

### Top 10 Bowlers (Unstop Dropdowns):
1. **Rank 1**: `Sunil Narine`
2. **Rank 2**: `Abrar Ahmed`
3. **Rank 3**: `Jasprit Bumrah`
4. **Rank 4**: `Mitchell Santner`
5. **Rank 5**: `Rashid Khan`
6. **Rank 6**: `Akeal Hosein`
7. **Rank 7**: `Matheesha Pathirana`
8. **Rank 8**: `Varun Chakravarthy`
9. **Rank 9**: `Kuldeep Yadav`
10. **Rank 10**: `Mustafizur Rahman`

