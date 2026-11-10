# 🏏 SupeRR Selector Web Application

A Django web application displaying the **Pressure Reliability Index (PRI)** analytics for the **Rajasthan Royals Hackathon (SupeRR Selector Season 2)**.

---

## 🌟 Features

- **Dashboard (Home)**: High-level metrics (total matches, IPL matches, knockout matches, % pressure balls) and Top 10 Batters & Bowlers.
- **Batters Under Pressure**: Full filterable and searchable table of qualified batters across all seasons (2022–2026) and recent seasons (2025–2026), with an IPL-eligible toggle.
- **Bowlers Under Pressure**: Full filterable and searchable table of qualified bowlers with economy, strike rate, dot ball %, boundary %, and PRI score.
- **IPL Eligible Tab**: Direct view of Top 20 IPL-eligible batters and bowlers (Pakistan players excluded).
- **2025–2026 Rankings**: Top 20 batters and bowlers for the most recent two seasons.
- **Match Explorer**: Browse 880+ matches with stage, venue, format (IPL / T20I), knockout flags, and results.
- **Interactive Methodology**: Detailed mathematical documentation of the PRI scoring formulas, phase baselines, and pressure criteria.
- **Rajasthan Royals Theme**: Styled with RR Royal Blue (`#002D6A`) and Hot Pink (`#E91E8C`).

---

## 🗄️ Database: MySQL & SQLite Dual Support

The application is built to support **MySQL** seamlessly via PyMySQL, and falls back to **SQLite** (pre-seeded with all data) for out-of-the-box zero-setup execution.

### Option 1: Running with Pre-seeded SQLite (Instant Start)

The SQLite database (`db.sqlite3`) is already migrated and seeded with all records. Simply run:

```bash
cd web
python manage.py runserver
```
Visit: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

### Option 2: Running with MySQL

1. **Create the Database and Import Data**:
   You can import the schema and pre-computed pressure data directly into MySQL using `mysql_data_dump.sql`:
   ```bash
   mysql -u root -p < mysql_data_dump.sql
   ```
   *Or* create the database manually:
   ```sql
   CREATE DATABASE superr_selector_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

2. **Configure Environment Variables**:
   Set `USE_MYSQL=True` and configure your credentials:
   - **Windows PowerShell**:
     ```powershell
     $env:USE_MYSQL="True"
     $env:MYSQL_DATABASE="superr_selector_db"
     $env:MYSQL_USER="root"
     $env:MYSQL_PASSWORD="your_password"
     $env:MYSQL_HOST="127.0.0.1"
     $env:MYSQL_PORT="3306"
     ```
   - **Linux/macOS Bash**:
     ```bash
     export USE_MYSQL=True
     export MYSQL_DATABASE=superr_selector_db
     export MYSQL_USER=root
     export MYSQL_PASSWORD=your_password
     export MYSQL_HOST=127.0.0.1
     export MYSQL_PORT=3306
     ```

3. **Run Migrations & Seed (if not imported via SQL dump)**:
   ```bash
   python manage.py makemigrations pressure_app
   python manage.py migrate
   python load_data.py
   ```

4. **Start Django Server**:
   ```bash
   python manage.py runserver
   ```

---

## 📁 Project Directory Layout

```
web/
├── manage.py                  # Django CLI entrypoint
├── db.sqlite3                 # Pre-seeded SQLite database
├── mysql_schema.sql           # MySQL DDL table schema
├── mysql_data_dump.sql        # Complete MySQL database dump (DDL + all data INSERTS)
├── export_mysql_dump.py       # Script to regenerate mysql_data_dump.sql
├── load_data.py               # Database seeder from hackathon CSV files
├── superr_selector/           # Django project configuration
│   ├── settings.py            # App settings (MySQL & SQLite switchable)
│   ├── urls.py                # Main URL router
│   ├── wsgi.py
│   └── asgi.py
├── pressure_app/              # Main analytics application
│   ├── models.py              # BatterRanking, BowlerRanking, MatchSummary
│   ├── views.py               # Views for dashboard, players, matches, methodology
│   ├── urls.py                # App routing
│   ├── admin.py               # Django Admin registration
│   └── templates/pressure_app/
│       ├── base.html          # RR branded base template with navbar
│       ├── index.html         # Dashboard & Top 10 cards
│       ├── batters.html       # Full filterable batters view
│       ├── bowlers.html       # Full filterable bowlers view
│       ├── ipl_eligible.html  # IPL eligible tabs (Pak players excluded)
│       ├── recent_2526.html   # 2025-2026 rankings tab
│       ├── matches.html       # Match list & filter
│       └── methodology.html   # Model & formula breakdown
└── static/
    └── css/
        └── custom.css         # RR custom color scheme & table styling
```

---

## 📊 Summary of Seeded Data

- **Batter Rankings**: All qualified batters (2022–2026 and 2025–2026) with PRI scores, delta SR, boundary %, RSAA.
- **Bowler Rankings**: All qualified bowlers with PRI scores, economy under pressure, dot %, boundary conceded %, runs saved per 6 balls.
- **Matches**: 883 match summaries across IPL and T20Is with knockout indicators.
- **IPL Eligibility**: Flagged in database and UI, excluding Pakistan players.

