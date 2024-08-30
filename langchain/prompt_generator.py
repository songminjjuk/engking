from langchain.prompts import ChatPromptTemplate

class PromptGenerator:
    quiz_example_output = """
    Example format:
    <Question Number> <Question>
    A) <Option 1>
    B) <Option 2>
    C) <Option 3>
    D) <Option 4>
    """

    def create_chat_prompt(self, difficulty, scenario, history):
        scenario_prompts = {
            "hamburger": "You are an expert in helping customers order hamburgers. Guide the user through ordering a hamburger, including selecting ingredients, sides, and drinks.",
            "travel": "You are an immigration officer assisting a traveler. Help the user go through the immigration process, including answering questions about their trip and providing necessary documentation.",
            "coffee": "You are an expert barista helping a customer order coffee. Guide the user through choosing their coffee type, size, and any additional preferences like milk, sugar, or flavorings.",
            "meeting": "You are a professional meeting coordinator. Help the user organize a meeting, including setting the agenda, scheduling, and inviting participants.",
            "movie": "You are a cinema ticket booking assistant. Help the user book a movie ticket, including selecting the movie, showtime, and seating preferences.",
            "music": "You are a music enthusiast engaging in a conversation about music. Discuss various genres, artists, or specific songs based on the user's interests."
        }

        difficulty_prompts = {
            "Easy": "Additionally, the difficulty level is Easy, Use simple and direct language. Keep your responses short and avoid complex details.",
            "Normal": "Additionally, the difficulty level is Normal, Use moderate language with some detail. Provide clear explanations but avoid overly complex terms.",
            "Hard": "Additionally, the difficulty level is Hard, Use complex and detailed language. Include nuanced explanations and advanced vocabulary in your responses."
        }

        scenario_prompt = scenario_prompts.get(scenario)
        difficulty_prompt = difficulty_prompts.get(difficulty)

        prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", f"{scenario_prompt} {difficulty_prompt}. Please ask the user a question directly without any introductory phrases.\nchat_history: {history}"),
                ("human", "{{input}}")
            ]
        )
        return prompt_template

    def create_quiz_prompt(self, quiz_type, difficulty, history):
        quiz_type_prompts = {
            "vocabulary": "You are an expert at creating vocabulary quizzes. Create a quiz where the user needs to identify the correct word based on the context.",
            "grammar": "You are an expert at creating grammar quizzes. Create a quiz where the user needs to identify the correct grammar usage."
        }

        difficulty_prompts = {
            "Easy": "Additionally, the difficulty level is Easy, so create the quiz with simple and direct expressions.",
            "Normal": "Additionally, the difficulty level is Normal, so create the quiz with moderate expressions that include some details.",
            "Hard": "Additionally, the difficulty level is Hard, so create the quiz with complex and detailed expressions."
        }

        quiz_prompt = quiz_type_prompts.get(quiz_type)
        difficulty_prompt = difficulty_prompts.get(difficulty)

        prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", f"{quiz_prompt} {difficulty_prompt} Generate only one quiz question. Use the following format: {self.quiz_example_output}. Ask a question right away without any introductory text, and do not generate multiple questions.\nchat_history: {history}"),
                ("human", "{{input}}")
            ]
        )
        return prompt_template
