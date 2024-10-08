from modules.memory_manager import memory_manager
from modules.prompt_manager import prompt_manager
from langchain.chains import ConversationChain
from modules.bedrock_client import bedrock_llm
from fastapi.responses import JSONResponse

import time
from fastapi import HTTPException
from loguru import logger

class QuizService:
    @staticmethod
    def process_quiz(data):
        start_time = time.time() #
        try:
            user_id = data.get('user_id')
            conversation_id = data.get('conversation_id')
            quiz_type = data.get('quiz_type', 'vocabulary')
            difficulty = data.get('difficulty', 'Normal')
            user_input = data.get('input', 'Please give me a quiz question.')
            first = data.get('first', False)
            
            logger.info(f"Request received: method=POST, url=/quiz") #data = {data}

            memory = memory_manager.get_memory(user_id, conversation_id)
            prompt_template = prompt_manager.create_quiz_prompt_template(quiz_type, difficulty, first)
            conversation = ConversationChain(llm=bedrock_llm, memory=memory, prompt=prompt_template, verbose=True)
            response_content = conversation.predict(input=user_input)

            memory_manager.delete_memory(user_id, conversation_id)
            
            end_time = time.time()
            duration = (end_time - start_time) * 1000

            logger.info(f"Response successful: status=200, duration={duration:.2f}ms")

            return JSONResponse(content={
                "content": response_content,
                "user_id": user_id,
                "conversation_id": conversation_id
            })
        except HTTPException as e:
            end_time = time.time()
            duration = (end_time - start_time) * 1000

            # HTTP 예외 발생 시 로그 기록
            logger.error(f"Exception occurred: {str(e.detail)}")

            raise e
        except Exception as e:
            # 요청 처리 시간 기록
            end_time = time.time()
            duration = (end_time - start_time) * 1000

            # 기타 예외 발생 시 로그 기록
            logger.error(f"Exception occurred: {str(e)}")

            raise HTTPException(status_code=500, detail="Internal Server Error")