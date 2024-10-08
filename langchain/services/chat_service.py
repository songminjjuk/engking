from modules.memory_manager import memory_manager
from modules.prompt_manager import prompt_manager
from langchain.chains import ConversationChain
from modules.bedrock_client import bedrock_llm
from fastapi.responses import JSONResponse

import time
from fastapi import HTTPException
from loguru import logger

class ChatService:
    @staticmethod
    def process_chat(data):
        start_time = time.time() #
        try:
            user_id = data.get('user_id')
            conversation_id = data.get('conversation_id')
            user_input = data.get('input', 'Can you ask me a question?')
            difficulty = data.get('difficulty', 'Normal')
            scenario = data.get('scenario', 'coffee')
            first = data.get('first', False)
            
            logger.info(f"Request received: method=POST, url=/chat") #data = {data}
            # logger.info("Request received: method=GET, url=/status")

            memory = memory_manager.get_memory(user_id, conversation_id)
            prompt_template = prompt_manager.create_chat_prompt_template(scenario, difficulty, first)
            conversation = ConversationChain(llm=bedrock_llm, memory=memory, prompt=prompt_template, verbose=True)
            response_content = conversation.predict(input=user_input)

            memory_manager.delete_memory(user_id, conversation_id)
            
            end_time = time.time()
            duration = (end_time - start_time) * 1000  # 밀리초로 변환
            
            # 응답 성공 로그 기록
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