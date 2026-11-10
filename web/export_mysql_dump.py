import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_DB = os.path.join(BASE_DIR, 'db.sqlite3')
OUTPUT_SQL = os.path.join(BASE_DIR, 'mysql_data_dump.sql')
SCHEMA_SQL = os.path.join(BASE_DIR, 'mysql_schema.sql')

def escape_sql_val(val):
    if val is None:
        return 'NULL'
    if isinstance(val, (int, float)):
        return str(val)
    # String or boolean
    if isinstance(val, bool):
        return '1' if val else '0'
    s = str(val).replace('\\', '\\\\').replace("'", "''")
    return f"'{s}'"

def main():
    if not os.path.exists(SQLITE_DB):
        print(f"Error: {SQLITE_DB} does not exist.")
        return

    with open(SCHEMA_SQL, 'r', encoding='utf-8') as f:
        schema_content = f.read()

    conn = sqlite3.connect(SQLITE_DB)
    cursor = conn.cursor()

    tables = ['batter_rankings', 'bowler_rankings', 'matches_summary']

    with open(OUTPUT_SQL, 'w', encoding='utf-8') as f:
        f.write(schema_content)
        f.write("\n\n-- ==============================================================\n")
        f.write("-- Data Inserts\n")
        f.write("-- ==============================================================\n\n")

        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]
            cols_str = ", ".join([f"`{c}`" for c in columns])

            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            if not rows:
                continue

            f.write(f"-- Data for table `{table}` ({len(rows)} records)\n")
            f.write(f"LOCK TABLES `{table}` WRITE;\n")
            
            # Batch inserts in chunks of 50
            chunk_size = 50
            for i in range(0, len(rows), chunk_size):
                chunk = rows[i:i + chunk_size]
                values_list = []
                for row in chunk:
                    row_vals = ", ".join([escape_sql_val(val) for val in row])
                    values_list.append(f"({row_vals})")
                values_str = ",\n".join(values_list)
                f.write(f"INSERT INTO `{table}` ({cols_str}) VALUES\n{values_str};\n")
            
            f.write(f"UNLOCK TABLES;\n\n")

    conn.close()
    print(f"Exported MySQL schema and data to: {OUTPUT_SQL}")

if __name__ == '__main__':
    main()

