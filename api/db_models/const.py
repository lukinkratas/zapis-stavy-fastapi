from psycopg import sql

INSERT_QUERY = sql.SQL("""
    INSERT INTO {table} ({columns})
    VALUES ({value_placeholders})
    RETURNING *;
""")
