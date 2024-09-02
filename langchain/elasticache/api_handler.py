from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
import json
from services.memory_service import MemoryService
from services.bedrock_service import BedrockService
from services.prompt_service import PromptService
from services.s3_service import S3Service
from utils.config import MODEL_ID, REGION_NAME, S3_BUCKET_NAME
from langchain.chains import ConversationChain
from langchain.schema import HumanMessage
# from s3_storage import S3Storage

class APIHandler:
    def __init__(self):
        self.memory_service = MemoryService()
        self.bedrock_service = BedrockService(model_id=MODEL_ID, region_name=REGION_NAME)
        self.prompt_service = PromptService()
        self.s3_storage = S3Service(bucket_name=S3_BUCKET_NAME, region_name=REGION_NAME)

    async def stream_chat_endpoint(self, request: Request):
        data = await request.json()
        user_id = data.get('user_id')
        conversation_id = data.get('conversation_id')
        user_input = data.get('input', 'Can you ask me a question?')
        difficulty = data.get('difficulty', 'Normal')
        scenario = data.get('scenario', 'coffee')

        memory = self.memory_service.get_memory(user_id, conversation_id)
        history = memory.load_memory_variables({}).get("history", "")
        prompt_template = self.prompt_service.create_chat_prompt(difficulty, scenario, history)
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
        
        memory = self.memory_service.get_memory(user_id, conversation_id)
        history = memory.load_memory_variables({}).get("history", "")
        prompt_template = self.prompt_service.create_quiz_prompt(quiz_type, difficulty, history)
        prompt_text = prompt_template.format(input=user_input)

        async def stream_response():
            full_response = ""
            async for chunk in self.bedrock_service.stream_invoke(prompt_text):
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

        memory = self.memory_service.get_memory(user_id, conversation_id)
        prompt_template = self.prompt_service.create_chat_prompt_template(scenario, difficulty, first=True)
        conversation = ConversationChain(llm=self.bedrock_service.get_llm(), memory=memory, prompt=prompt_template, verbose=True)
        response_content = conversation.predict(input=user_input)

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

        memory = self.memory_service.get_memory(user_id, conversation_id)
        prompt_template = self.prompt_service.create_quiz_prompt_template(quiz_type, difficulty, first=True)
        conversation = ConversationChain(llm=self.bedrock_service.get_llm(), memory=memory, prompt=prompt_template, verbose=True)
        response_content = conversation.predict(input=user_input)

        return JSONResponse(content={
            "content": response_content,
            "user_id": user_id,
            "conversation_id": conversation_id
        })

    async def chat_evaluate_endpoint(self, request: Request):
        data = await request.json()
        user_id = data.get('user_id')
        conversation_id = data.get('conversation_id')

        memory = self.memory_service.get_memory(user_id, conversation_id)

        if not memory.chat_memory.messages:
            return JSONResponse(content={"error": "No conversation history found"}, status_code=400)

        conversation_text = "\n".join(
            f"Human: {message.content}" if isinstance(message, HumanMessage) else f"AI: {message.content}\n"
            for message in memory.chat_memory.messages
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
        response = self.bedrock_service.get_llm().invoke(chat_evaluation_prompt)
        self.memory_service.delete_memory(user_id, conversation_id)
        response_content = json.loads(response.content)
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

        memory = self.get_memory(user_id, conversation_id)

        if not memory.chat_memory.messages:
            return JSONResponse(content={"error": "No quiz history found"}, status_code=400)

        conversation_text = "\n".join(
            f"Human: {message.content}" if isinstance(message, HumanMessage) else f"AI: {message.content}\n"
            for message in memory.chat_memory.messages
        )
        print("conversation_text: ", conversation_text)
        quiz_evaluation_prompt=f"""
        Here is the quiz session:\n{conversation_text}\n
        Please fill in the "correct_answers" field with the number of correct answers the user provided, and the "total_questions" field with the total number of questions in the quiz. Additionally, provide feedback in the "feedback" field based on the user's performance.
        Respond in the following JSON format:
        {{
            "correct_answers": "<number_of_correct_answers>",
            "total_questions": "<total_number_of_questions>",
            "feedback": "<your_feedback>"
        }}
        """
        response = self.bedrock_llm.invoke(quiz_evaluation_prompt)
        self.delete_memory(user_id, conversation_id)
        response_content = json.loads(response.content)
        total_questions = int(response_content.get("total_questions"))
        correct_answers = int(response_content.get("correct_answers"))
        score = (correct_answers / total_questions) * 100
        score = round(score, 1)
        return JSONResponse(content={
            "user_id": user_id,
            "conversation_id": conversation_id,
            "score": str(score),
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
