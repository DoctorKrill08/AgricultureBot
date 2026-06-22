#!/bin/bash

sleep 30

cd ~/AgricultureBot

/home/jarm/AgricultureBot/venv/bin/uvicorn \
    main:app \
    --host 0.0.0.0 \
    --port 8000 &

cd ~/AgricultureBot/Interface

exec npm run dev -- --webpack