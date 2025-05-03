#!/bin/bash

set -ex

# 프로덕션 설정으로 실행
uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --proxy-headers \
    --forwarded-allow-ips='*' \
    --log-level info
