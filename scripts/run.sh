#!/usr/bin/bash

source .venv/bin/activate
set -a
source .env
set +a
uvicorn src.main:app --reload