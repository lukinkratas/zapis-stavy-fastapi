#!/bin/bash
set -e

for file in common.sql users.sql locations.sql; do
  psql -U $POSTGRES_USER -d $POSTGRES_DB -f /docker-entrypoint-initdb.d/sql/$file
done
