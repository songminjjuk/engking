from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
import json
from memory_manager import MemoryManager
from bedrock_client import BedrockClient
from prompt_generator import PromptGenerator
from langchain.schema import HumanMessage, AIMessage
# from s3_storage import S3Storage

class APIHandler:
    def __init__(self):
        self.memory_manager = MemoryManager()
        self.bedrock_client = BedrockClient(model_id="anthropic.claude-3-5-sonnet-20240620-v1:0", region_name="ap-northeast-1")
        self.prompt_generator = PromptGenerator()
        # self.s3_storage = S3Storage(bucket_name="mmmybucckeet", region_name="ap-northeast-1")

    async def stream_chat_endpoint(self, request: Request):
        data = await request.json()
        user_id = data.get('user_id')
        conversation_id = data.get('conversation_id')
        user_input = data.get('input', 'Can you ask me a question?')
        difficulty = data.get('difficulty', 'Normal')
        scenario = data.get('scenario', 'coffee')

        memory = self.memory_manager.get_memory(user_id, conversation_id)
        history = memory.load_memory_variables({}).get("history", "")
        prompt_template = self.prompt_generator.create_chat_prompt(difficulty, scenario, history)
        prompt_text = prompt_template.format(input=user_input)

        async def stream_response():
            full_response = ""
            async for chunk in self.bedrock_client.stream_invoke(prompt_text):
                print(chunk, end="", flush=True)
                yield chunk
                full_response += chunk
            memory.save_context({"human": user_input}, {"ai": full_response})
            print(memory.load_memory_variables({}))
        
        return StreamingResponse(stream_response(), media_type="text/plain")

    async def stream_quiz_endpoint(self, request: Request):
        data = await request.json()
        user_id = data.get('user_id')
        conversation_id = data.get('conversation_id')
        quiz_type = data.get('quiz_type', 'vocabulary')
        difficulty = data.get('difficulty', 'Normal')
        user_input = data.get('input', 'Please give me a quiz question.')
        
        memory = self.memory_manager.get_memory(user_id, conversation_id)
        history = memory.load_memory_variables({}).get("history", "")
        prompt_template = self.prompt_generator.create_quiz_prompt(quiz_type, difficulty, history)
        prompt_text = prompt_template.format(input=user_input)

        async def stream_response():
            full_response = ""
            async for chunk in self.bedrock_client.stream_invoke(prompt_text):
                print(chunk, end="", flush=True)
                yield chunk
                full_response += chunk
            memory.save_context({"human": user_input}, {"ai": full_response})
            print(memory.load_memory_variables({}))
        
        return StreamingResponse(stream_response(), media_type="text/plain")

    async def chat_endpoint(self, request: Request):
        data = await request.json()
        user_id = data.get('user_id')
        conversation_id = data.get('conversation_id')
        user_input = data.get('input', 'Can you ask me a question?')
        difficulty = data.get('difficulty', 'Normal')
        scenario = data.get('scenario', 'coffee')
        first = data.get('first', 'True')
        memory = self.memory_manager.get_memory(user_id, conversation_id)
        history = memory.load_memory_variables({}).get("history", "")
        prompt_template = self.prompt_generator.create_chat_prompt(difficulty, scenario, history, first)
        prompt_text = prompt_template.format(input=user_input)
        print("prompt_text: ", prompt_text)
        response = self.bedrock_client.invoke(prompt_text)
        response_content = response.content
        memory.save_context({"human": user_input}, {"ai": response_content})
        print(memory.load_memory_variables({}))
        
        return JSONResponse(content={
            "content": response_content,
            "user_id": user_id,
            "conversation_id": conversation_id
        })

    async def quiz_endpoint(self, request: Request):
        data = await request.json()
        user_id = data.get('user_id')
        conversation_id = data.get('conversation_id')
        quiz_type = data.get('quiz_type', 'vocabulary')
        difficulty = data.get('difficulty', 'Normal')
        user_input = data.get('input', 'Please give me a quiz question.')
        first = data.get('first', 'True')
        memory = self.memory_manager.get_memory(user_id, conversation_id)
        history = memory.load_memory_variables({}).get("history", "")
        prompt_template = self.prompt_generator.create_quiz_prompt(quiz_type, difficulty, history, first)
        prompt_text = prompt_template.format(input=user_input)
        print("prompt_text: ", prompt_text)
        response = self.bedrock_client.invoke(prompt_text)
        response_content = response.content
        memory.save_context({"human": user_input}, {"ai": response_content})
        print(memory.load_memory_variables({}))
        
        return JSONResponse(content={
            "content": response_content,
            "user_id": user_id,
            "conversation_id": conversation_id
        })

    async def chat_evaluate_endpoint(self, request: Request):
        data = await request.json()
        user_id = data.get('user_id')
        conversation_id = data.get('conversation_id')
        # user_name = data.get('user_name')
        memory = self.memory_manager.get_memory(user_id, conversation_id)

        if not memory.chat_memory.messages:
            return JSONResponse(content={"error": "No conversation history found"}, status_code=400)
        
        # 마지막 메시지가 AI의 메시지일 경우 제거
        if messages and isinstance(messages[-1], AIMessage):
            messages = messages[:-1]  # 마지막 메시지 제거
        messages = memory.chat_memory.messages
        conversation_text = "\n".join(
            f"Human: {message.content}" if isinstance(message, HumanMessage) else f"AI: {message.content}\n"
            for message in messages
        )
        
        chat_evaluation_prompt = f"""
        Here is the conversation:\n{conversation_text}\n
        Please rate the user's language skills on a scale of 1 to 100 and provide feedback on how they can improve.
        Respond in the following JSON format:
        {{
            "score": "<numeric_score>",
            "feedback": "<feedback>"
        }}
        """
        response = self.bedrock_client.invoke(chat_evaluation_prompt)
        self.memory_manager.delete_memory(user_id, conversation_id)
        response_content = json.loads(response.content)
        print("response_content: ", response_content)
        
        return JSONResponse(content={
            "user_id": user_id,
            "conversation_id": conversation_id,
            "score": response_content.get("score"),
            "feedback": response_content.get("feedback")
        })

    async def quiz_evaluate_endpoint(self, request: Request):
        data = await request.json()
        user_id = data.get('user_id')
        conversation_id = data.get('conversation_id')
        # user_name = data.get('user_name')
        memory = self.memory_manager.get_memory(user_id, conversation_id)

        if not memory.chat_memory.messages:
            return JSONResponse(content={"error": "No quiz history found"}, status_code=400)
        messages = memory.chat_memory.messages
        # 마지막 메시지가 AI의 메시지일 경우 제거
        if messages and isinstance(messages[-1], AIMessage):
            messages = messages[:-1]  # 마지막 메시지 제거

        conversation_text = "\n".join(
            f"Human: {message.content}" if isinstance(message, HumanMessage) else f"AI: {message.content}\n"
            for message in messages
        )
        quiz_evaluation_prompt = f"""
        Here is the quiz session:\n{conversation_text}\n
        Please fill in the "correct_answers" field with the number of correct answers the user provided, and the "total_questions" field with the total number of questions in the quiz. Additionally, provide feedback in the "feedback" field based on the user's performance.
        Respond in the following JSON format:
        {{
            "correct_answers": "<number_of_correct_answers>",
            "total_questions": "<total_number_of_questions>",
            "feedback": "<your_feedback>"
        }}
        """
        response = self.bedrock_client.invoke(quiz_evaluation_prompt)
        self.memory_manager.delete_memory(user_id, conversation_id)
        response_content = json.loads(response.content)
        pprint("response_content: ", response_content)
        total_questions = int(response_content.get("total_questions"))
        correct_answers = int(response_content.get("correct_answers"))
        score = (correct_answers / total_questions) * 100
        score = round(score, 1)  # 반올림
        score = str(score)
        return JSONResponse(content={
            "user_id": user_id,
            "conversation_id": conversation_id,
            "score": score,
            "feedback": response_content.get("feedback")
        })

    async def save_endpoint(self, request: Request):
        data = await request.json()
        user_id = data.get('user_id')
        conversation_id = data.get('conversation_id')
        user_name = data.get('user_name')

        if not user_id or not conversation_id:
            return JSONResponse(content={"error": "User ID and conversation ID are required"}, status_code=400)

        memory = self.memory_manager.get_memory(user_id, conversation_id)
        conversation_text = "\n".join(
            f"Human: {message.content}" if isinstance(message, HumanMessage) else f"AI: {message.content}\n"
            for message in memory.chat_memory.messages
        )
        s3_key = self.s3_storage.save_conversation(user_name, conversation_id, conversation_text)
        
        return JSONResponse(content={"message": "Conversation saved", "s3_key": s3_key})
