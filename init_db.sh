#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 <<-EOSQL
    CREATE USER psql WITH ENCRYPTED PASSWORD 'my_password';
    CREATE DATABASE deals_db OWNER psql;
    \connect psql;
    CREATE SCHEMA deals_schema AUTHORIZATION psql;

    CREATE TABLE deals_schema.deals(
        date DATE DEFAULT CURRENT_DATE,
        platform VARCHAR(4),
        game_name VARCHAR(255),
        game_type VARCHAR(255),
        price NUMERIC(2)
    );

    GRANT ALL PRIVILEGES ON SCHEMA deals_schema TO psql;
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA deals_schema TO psql;
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA deals_schema TO psql;
EQOSQL