import boto3
from flask import Flask, request, jsonify
from langchain_aws import ChatBedrock
from langchain.prompts import ChatPromptTemplate

app = Flask(__name__)

# Claude 모델을 초기화 ChatBedrock 사용
def initialize_bedrock_client(model_id, region_name):
    return ChatBedrock(
        model_id=model_id,
        model_kwargs=dict(temperature=0),
        region_name=region_name,
        client=boto3.client("bedrock-runtime", region_name=region_name)
    )

# 난이도 및 상황에 따른 프롬프트 템플릿 생성
def create_prompt_template(difficulty, scenario):
    scenario_prompts = {
        "햄버거 주문하기": "You are helping a customer order a hamburger.",
        "입국 심사하기": "You are assisting a traveler going through immigration.",
        "커피 주문하기": "You are helping a customer order a coffee."
    }

    difficulty_prompts = {
        "Easy": "Use simple and straightforward language.",
        "Normal": "Use moderate language with some detail.",
        "Hard": "Use complex and detailed language."
    }

    scenario_prompt = scenario_prompts.get(scenario, "You are a helpful assistant.") # 만약 사전에 없는 시나리오가 들어올 경우 기본값으로 "You are a helpful assistant."를 사용
    difficulty_prompt = difficulty_prompts.get(difficulty, "Use appropriate language.") # Use appropriate language."를 사용

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", f"{scenario_prompt} {difficulty_prompt}"),
            ("human", "{input}")
        ]
    )

    return prompt_template

# 모델과 프롬프트를 연결하고 응답 생성
def get_response_from_claude(difficulty, scenario, user_input):
    bedrock_llm = initialize_bedrock_client(
        model_id="anthropic.claude-3-haiku-20240307-v1:0",
        region_name="ap-northeast-1"
    )

    prompt_template = create_prompt_template(difficulty, scenario)
    chain = prompt_template | bedrock_llm

    response = chain.invoke({"input": user_input})
    return response.content if hasattr(response, "content") else str(response)

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    data = request.json
    user_input = data.get('input')
    difficulty = data.get('difficulty', 'Normal')
    scenario = data.get('scenario', '커피 주문하기')

    if not user_input:
        return jsonify({"error": "Input is required"}), 400

    response = get_response_from_claude(difficulty, scenario, user_input)
    print(response)
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
