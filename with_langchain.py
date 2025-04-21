from langchain_core.runnables import RunnablePassthrough
from langchain.prompts import ChatPromptTemplate
from langchain_bedrock import Bedrock

prompt = ChatPromptTemplate.from_template("Tell me a short joke about {topic}")

model = Bedrock(model_id="anthropic.claude-3-haiku-20240307-v1:0")

chain = {
    "topic": RunnablePassthrough() | prompt | model
}

result = chain.invoke("ice cream")
print(result)
