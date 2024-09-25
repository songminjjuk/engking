#!/bin/bash

# PID 파일이 존재하는 경우
if [ -f .pidfile ]; then
    # 저장된 PID로 프로세스 종료
    kill $(cat .pidfile)
    echo "Backend server stopped."
    rm .pidfile  # PID 파일 삭제
else
    echo "No PID file found. Backend server may not be running."
fi

