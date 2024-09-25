from modules.memory_manager import memory_manager
from modules.bedrock_client import bedrock_llm
import json
from fastapi.responses import JSONResponse
from langchain.schema import HumanMessage, AIMessage

class EvaluateService:
    @staticmethod
    def evaluate_chat(data):
        user_id = data.get('user_id')
        conversation_id = data.get('conversation_id')
        memory = memory_manager.get_memory(user_id, conversation_id)

        if not memory.chat_memory.messages:
            return JSONResponse(content={"error": "No conversation history found"}, status_code=400)

        # 대화 내용을 텍스트로 변환
        messages = memory.chat_memory.messages
        conversation_text = "\n".join(
            f"Human: {message.content}" if isinstance(message, HumanMessage) else f"AI: {message.content}\n"
            for message in messages
        )

        chat_evaluation_prompt = f"""
        You are an expert in evaluating language skills based on conversations. Below is a conversation between a user and an AI.
        Please evaluate the user's English language skills on a scale of 1 to 100, and provide detailed feedback on how the user can improve.
        The feedback should be written **in Korean** but based on the user's English answers.
        Ensure that your JSON response uses proper escaping for special characters like newlines and quotes.

        Ensure your response is strictly in the following JSON format without any additional comments or text:

        {{
            "score": "<percentage_score as string>",
            "feedback": "<feedback in Korean, with proper escaping of special characters>"
        }}

        The response should be a valid JSON string only. Make sure the feedback string uses proper JSON escaping for characters like newline (\\n) and quotes (\\").
        Conversation:
        {conversation_text}

        Remember, your response should be a valid JSON string, and do not include any extra information or comments outside the JSON.
        """
        response = bedrock_llm.invoke(chat_evaluation_prompt)
        memory_manager.delete_memory(user_id, conversation_id)
        print("response_content: ", response.content)
        # 응답 처리
        try:
            # clean_content = response.content.decode('utf-8')            
            response_content = json.loads(response.content)
            feedback = response_content.get("feedback")
            score = response_content.get("score")

            return JSONResponse(content={
                "user_id": user_id,
                "conversation_id": conversation_id,
                "score": str(score),
                "feedback": feedback
            })
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError: {str(e)} - Response content: {response.content}")
            return JSONResponse(content={"error": "Invalid response from the LLM service"}, status_code=500)

        except ValueError as e:
            print(f"ValueError: {str(e)}")
            return JSONResponse(content={"error": str(e)}, status_code=400)

        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return JSONResponse(content={"error": "An unexpected error occurred."}, status_code=500)

    @staticmethod
    def evaluate_quiz(data):
        user_id = data.get('user_id')
        conversation_id = data.get('conversation_id')
        quiz_type = data.get('quiz_type', 'vocabulary')
        difficulty = data.get('difficulty', 'Normal')
        user_input = data.get('input', 'Please give me a quiz question.')
        first = data.get('first', False)
        memory = memory_manager.get_memory(user_id, conversation_id)

        if not memory.chat_memory.messages:
            return JSONResponse(content={"error": "No quiz history found"}, status_code=400)

        # 대화 내용을 텍스트로 변환
        messages = memory.chat_memory.messages
        conversation_text = "\n".join(
            f"Human: {message.content}" if isinstance(message, HumanMessage) else f"AI: {message.content}\n"
            for message in messages
        )
        # memory.chat_memory.add_user_message(HumanMessage(content=message_text))
        quiz_evaluation_prompt = f"""
        You are an expert at evaluating quiz sessions. Below is a conversation that includes a quiz session.
        Please evaluate the user's performance in answering the quiz questions. Calculate the score as a percentage based on the number of correct answers and total questions.
        Additionally, provide feedback in Korean that focuses on the user's English skills, including grammar, vocabulary, and comprehension.

        Ensure your response is strictly in the following JSON format without any additional comments or text:

        {{
            "score": "<percentage_score as string>",
            "feedback": "<feedback in Korean with properly escaped newlines, e.g., \\n>"
        }}

        The response should be a valid JSON string only.
        Conversation:
        {conversation_text}

        Remember, your response should be a valid JSON string, and do not include any extra information or comments outside the JSON.
        """

        
        response = bedrock_llm.invoke(quiz_evaluation_prompt)
        memory_manager.delete_memory(user_id, conversation_id)
        print("response_content: ", response.content)
        # 응답 처리
        try:
            # clean_content = response.content.decode('utf-8')
            response_content = json.loads(response.content)
            feedback = response_content.get("feedback")
            score = response_content.get("score")

            return JSONResponse(content={
                "user_id": user_id,
                "conversation_id": conversation_id,
                "score": str(score),
                "feedback": feedback
            })
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError: {str(e)} - Response content: {response.content}")
            return JSONResponse(content={"error": "Invalid response from the LLM service"}, status_code=500)

        except ValueError as e:
            print(f"ValueError: {str(e)}")
            return JSONResponse(content={"error": str(e)}, status_code=400)

        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return JSONResponse(content={"error": "An unexpected error occurred."}, status_code=500)
