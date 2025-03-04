#!/usr/bin/env bash
/scripts/wait-for-it.sh auth_postgres:30001 -s -t 60 &&
/scripts/wait-for-it.sh auth_redis:6379 -s -t 60 &&
alembic upgrade head