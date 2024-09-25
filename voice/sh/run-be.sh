#!/bin/bash

# Start the Uvicorn server using the API_HOST variable
uvicorn app.app:app --host 0.0.0.0 --port 8000 --reload &

# Save the PID to a file
echo $! > .pidfile

