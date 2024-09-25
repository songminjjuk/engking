#!/bin/bash

# 백그라운드에서 run-be.sh 실행
nohup ./sh/run-be.sh > run-be.log 2>&1 &

# PID 출력
echo "Backend server started with PID: $!"

