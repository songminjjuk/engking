from langchain.prompts import ChatPromptTemplate

class PromptTemplateManager:
    @staticmethod
    def create_chat_prompt_template(difficulty, scenario):
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

        scenario_prompt = scenario_prompts.get(scenario, "You are a helpful assistant.")
        difficulty_prompt = difficulty_prompts.get(difficulty, "Use appropriate language.")

        return ChatPromptTemplate.from_messages(
            [
                ("system", f"{scenario_prompt} {difficulty_prompt}. Please ask the user a question directly without any introductory phrases.\n{{history}}"),
                ("human", "{input}")
            ]
        )

    @staticmethod
    def create_quiz_prompt_template(quiz_type, difficulty):
        quiz_type_prompts = {
            "vocabulary": "You are a helpful assistant creating a vocabulary quiz. Ask questions where the user needs to select the correct word in context.",
            "grammar": "You are a helpful assistant creating a grammar quiz. Ask questions where the user needs to identify the correct grammar usage."
        }

        difficulty_prompts = {
            "Easy": "Use simple and straightforward language.",
            "Normal": "Use moderate language with some detail.",
            "Hard": "Use complex and detailed language."
        }

        quiz_prompt = quiz_type_prompts.get(quiz_type, "You are a helpful assistant creating a quiz.")
        difficulty_prompt = difficulty_prompts.get(difficulty, "Use appropriate language.")

        return ChatPromptTemplate.from_messages(
            [
                ("system", f"{quiz_prompt} {difficulty_prompt}. Generate the quiz based on the user's selected difficulty level. Ask the quiz question directly without any introductory phrases, do not respond to the user's answer, and move immediately to the next question.\n{{history}}"),
                ("human", "{input}")
            ]
        )
