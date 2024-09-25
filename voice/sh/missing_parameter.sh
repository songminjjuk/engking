#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Function to test the API with missing parameters
test_missing_parameter() {
    local missing_param=$1
    local request_body=$2
    local expected_error_message=$3

    # Create a temporary JSON body with the missing parameter
    modified_body=$(echo "$request_body" | jq "del(.\"$missing_param\")")

    # Send the request
    response=$(curl -s -X POST "http://${API_HOST}:8000/api/next-question/" \
    -H "Content-Type: application/json" \
    -d "$modified_body")

    # Check for expected error message in the response
    if echo "$response" | jq -e ".detail[] | select(.msg == \"$expected_error_message\")" > /dev/null; then
        echo "Test passed: Missing $missing_param handled correctly."
    else
        echo "Test failed: Missing $missing_param did not return expected error."
        echo "Response: $response"
    fi
}

# Test cases
echo "Testing missing parameters for next-question..."

# Test for missing memberId
test_missing_parameter "memberId" '{
  "topic": "coffee",
  "difficulty": "easy",
  "chatRoomId": "room1",
  "messageId": "msg123",
  "filename": "file.txt"
}' "Field required"

# Test for missing topic
test_missing_parameter "topic" '{
  "memberId": "1234",
  "difficulty": "easy",
  "chatRoomId": "room1",
  "messageId": "msg123",
  "filename": "file.txt"
}' "Field required"

# Test for missing difficulty
test_missing_parameter "difficulty" '{
  "memberId": "1234",
  "topic": "coffee",
  "chatRoomId": "room1",
  "messageId": "msg123",
  "filename": "file.txt"
}' "Field required"

echo -e "\nMissing parameter tests for next-question completed."
