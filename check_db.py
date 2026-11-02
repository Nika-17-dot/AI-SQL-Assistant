import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "ecommerce.db"

connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name;
""")

tables = cursor.fetchall()

print("\nDATABASE TABLES")
print("-" * 40)

for (table_name,) in tables:
    cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
    count = cursor.fetchone()[0]
    print(f"{table_name:<25} {count:>10,} rows")

connection.close()

print("\nDatabase verification completed!")