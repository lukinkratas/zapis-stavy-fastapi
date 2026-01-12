from psycopg import sql

INSERT_QUERY = sql.SQL("""
    INSERT INTO {table} ({columns})
    VALUES ({value_placeholders})
    RETURNING *;
""")

SELECT_BY_ID_QUERY = sql.SQL("""
    SELECT * FROM {table}
    WHERE id = %(id)s;
""")

DELETE_QUERY = sql.SQL("""
    DELETE FROM {table}
    WHERE id = %(id)s;
""")


SELECT_ALL_QUERY = sql.SQL("""
    SELECT * FROM {table}
    OFFSET %(offset)s
    LIMIT %(limit)s;
""")


UPDATE_QUERY = sql.SQL("""
    UPDATE {table}
    SET {set_clause}
    WHERE id = %(id)s RETURNING *;
""")
