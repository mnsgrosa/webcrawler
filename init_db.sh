#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 <<-EOSQL
    DROP DATABASE IF EXISTS deals_db;

    CREATE DATABASE deals_db OWNER postgres;

    \connect deals_db;
    
    CREATE SCHEMA deals_schema AUTHORIZATION postgres;

    CREATE TABLE deals_schema.deals(
        date DATE DEFAULT CURRENT_DATE,
        platform VARCHAR(20),
        game_name VARCHAR(255),
        game_type VARCHAR(255),
        price NUMERIC(10, 2) -- Increased precision for price
    );

    GRANT ALL PRIVILEGES ON SCHEMA deals_schema TO postgres;
    GRANT ALL ON ALL TABLES IN SCHEMA deals_schema TO postgres;
    GRANT ALL ON ALL SEQUENCES IN SCHEMA deals_schema TO postgres;
EOSQL

echo "done"