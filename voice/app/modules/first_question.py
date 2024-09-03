# app/modules/first_question.py
import os
import requests
import json

def get_first_question(member_id, topic, difficulty):
    b3_url = os.getenv('B3_URL')

    # Create request body
    request_body = {
        "memberId": member_id,
        "topic": topic,
        "difficulty": difficulty
    }

    # Send POST request
    try:
        response = requests.post(
            f"{b3_url}/chat/firstquestion",
            headers={"Content-Type": "application/json"},
            data=json.dumps(request_body),
            timeout=5
        )

        # Handle response
        if response.status_code == 200:
            response_data = response.json()
            first_question = response_data.get("firstQuestion")

            # Set a temporary question if firstQuestion is missing
            if not first_question:
                first_question = "Temporary question: Please enter a basic question."

            return {
                "success": response_data.get("success"),
                "firstQuestion": first_question,
                "memberId": response_data.get("memberId"),
                "chatRoomId": response_data.get("chatRoomId"),
                "createdTime": response_data.get("createdTime"),
                "messageId": response_data.get("messageId")
            }
        elif response.status_code == 503:
            response_data = response.json()
            return {
                "success": response_data.get("success"),
                "memberId": response_data.get("memberId"),
                "chatRoomId": response_data.get("chatRoomId"),
                "createdTime": response_data.get("createdTime"),
                "message": "Service is unavailable. Please try again later."
            }
        else:
            return {
                "success": False,
                "message": "Invalid request format."
            }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }
