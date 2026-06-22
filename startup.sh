#!/bin/bash

sleep 30

nmcli connection up robot

cd ~/AgricultureBot

/home/jarm/AgricultureBot/venv/bin/uvicorn \
    main:app \
    --host 0.0.0.0 \
    --port 8000 \
    > uvicorn.log 2>&1 &

cd Interface

npm run dev -- --webpack \
    > frontend.log 2>&1 &