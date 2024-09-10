#!/bin/bash

# Variables
API_URL="http://localhost:8000/api/create-post-url/"
FILENAME="audio.mp3"
FILEPATH="./sh/audio.mp3"  # Change this to the path of the file you want to upload

# Step 1: Generate the presigned POST URL
echo "Generating presigned POST URL..."
RESPONSE=$(curl -s -X POST "$API_URL" -H "Content-Type: application/json" -d "{\"filename\": \"$FILENAME\"}")

# Check if the response contains the presigned post data
if [[ $RESPONSE == *"presignedPost"* ]]; then
    echo "Presigned POST URL generated successfully."
    echo "$RESPONSE"

    # Extract the URL and fields from the response
    URL=$(echo "$RESPONSE" | jq -r '.presignedPost.url')
    ACL=$(echo "$RESPONSE" | jq -r '.presignedPost.fields.acl')
    CONTENT_TYPE=$(echo "$RESPONSE" | jq -r '.presignedPost.fields["Content-Type"]')
    KEY=$(echo "$RESPONSE" | jq -r '.presignedPost.fields.key')
    CREDENTIAL=$(echo "$RESPONSE" | jq -r '.presignedPost.fields["x-amz-credential"]')
    ALGORITHM=$(echo "$RESPONSE" | jq -r '.presignedPost.fields["x-amz-algorithm"]')  # Ensure this is included
    DATE=$(echo "$RESPONSE" | jq -r '.presignedPost.fields["x-amz-date"]')
    SIGNATURE=$(echo "$RESPONSE" | jq -r '.presignedPost.fields["x-amz-signature"]')

    # Step 2: Upload the file using the presigned POST URL
    echo "Uploading file to S3..."
    curl -X POST "$URL" \
        -F "key=$KEY" \
        -F "acl=$ACL" \
        -F "Content-Type=$CONTENT_TYPE" \
        -F "x-amz-credential=$CREDENTIAL" \
        -F "x-amz-algorithm=$ALGORITHM" \
        -F "x-amz-date=$DATE" \
        -F "x-amz-signature=$SIGNATURE" \
        -F "file=@$FILEPATH"

    echo "File upload completed."
else
    echo "Failed to generate presigned POST URL."
    echo "$RESPONSE"
fi
