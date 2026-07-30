#!/bin/bash


./venv/bin/python -u -m uvicorn \
    main:app \
    --host 0.0.0.0 \
    --port 8000 &

cd Interface

exec npm run dev -- --webpack
