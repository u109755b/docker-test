#!/bin/bash

USER=postgres
DB="sample_db"

echo "initializing database";

psql -U postgres -f create_db.sql
psql -U postgres -d $DB -f create_schema.sql;
psql -U postgres -d $DB -f basic_sample.sql;