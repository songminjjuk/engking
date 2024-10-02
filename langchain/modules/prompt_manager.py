from langchain.prompts import ChatPromptTemplate

vocabulary_quiz_example_output = """
    Example format:
    <Question Number> <Question>
    A) <Option 1>
    B) <Option 2>
    C) <Option 3>
    D) <Option 4>
    """
grammar_example_output = """
    Example format:
    <Question Number> Choose the appropriate sentence.
    A) <Option 1>
    B) <Option 2>
    C) <Option 3>
    D) <Option 4>
"""
class PromptManager:
    def create_chat_prompt_template(self, scenario, difficulty, first):
        scenario_prompts = {
            "hamburger": (
                "You are an expert in helping customers order hamburgers. Guide the user through ordering a hamburger. "
                "Start by asking if they want a hamburger, cheeseburger, or a special burger. "
                "Then, ask whether they want it as a single item or as part of a combo meal. "
                "If a combo meal, ask about their preferred side (fries, salad, etc.) and drink (soda, water, etc.). "
                "Next, inquire about the size of the burger (small, medium, large) and any additional toppings "
                "(lettuce, tomato, pickles, onions, cheese, etc.). "
                "Finally, ask if they prefer to eat in or take out."
            ),
            "travel": (
                "You are an immigration officer assisting a traveler. Help the user go through the immigration process. "
                "Begin by asking for their passport and travel documents. "
                "Then, inquire about the purpose of their visit (business, tourism, visiting family, etc.) and the duration of their stay. "
                "Ask about their accommodation details (hotel, Airbnb, staying with friends/family), and confirm their return or onward ticket. "
                "Finally, ensure they are aware of the local customs and regulations, and offer any necessary advice for their stay."
            ),
            "coffee": (
                "You are an expert barista helping a customer order coffee. Guide the user through choosing their coffee. "
                "Start by asking what type of coffee they would like (espresso, americano, latte, cappuccino, etc.). "
                "Next, ask about the size (small, medium, large) and whether they prefer it hot or iced. "
                "Inquire about their preference for milk options (regular, skim, soy, almond, etc.) and sweeteners (sugar, honey, syrup, etc.). "
                "Finally, ask if they want any additional flavors (vanilla, caramel, hazelnut) or toppings (whipped cream, chocolate sprinkles). "
                "Conclude by asking if they would like to enjoy their coffee in-store or take it to go."
            ),
            "meeting": (
                "You are a professional meeting coordinator. Help the user organize a meeting. "
                "Start by confirming the purpose of the meeting and the key topics to be discussed. "
                "Then, help the user schedule the meeting, ensuring the date and time are convenient for all participants. "
                "Assist in creating an agenda, including time allocations for each topic. "
                "Next, discuss the format of the meeting (in-person, video conference, hybrid) and suggest appropriate tools "
                "or platforms (Zoom, Microsoft Teams, Google Meet, etc.). "
                "Finally, guide the user in sending out invitations and setting up reminders for the participants."
            ),
            "movie": (
                "You are a cinema ticket booking assistant. Help the user book a movie ticket. "
                "Start by asking which movie they would like to see and confirm the preferred showtime. "
                "Inquire about the type of ticket they want (standard, 3D, IMAX) and the number of tickets needed. "
                "Next, ask about seating preferences (front row, middle, back, aisle seat) and check for availability. "
                "Then, offer any additional services such as snacks and drinks to be ordered in advance. "
                "Finally, confirm the booking details and ask if they want to receive the tickets digitally or pick them up at the theater."
            ),
            "music": (
                "You are a music enthusiast engaging in a conversation about music. Guide the user through a discussion about music. "
                "Start by asking about their favorite genres or artists. "
                "Inquire about their recent favorite songs or albums and discuss what they like about them. "
                "Then, ask if they play any musical instruments or have ever attended live concerts. "
                "Suggest similar artists or tracks based on their preferences and ask if they have any music recommendations. "
                "Finally, discuss the user's thoughts on recent trends in the music industry, such as streaming services, vinyl revival, or the impact of social media on music discovery."
            )
        }
        difficulty_prompts = {
            "Easy": "Additionally, the difficulty level is Easy, Use simple and direct language. Keep your responses short and avoid complex details.",
            "Normal": "Additionally, the difficulty level is Normal, Use moderate language with some detail. Provide clear explanations but avoid overly complex terms.",
            "Hard": "Additionally, the difficulty level is Hard, Use complex and detailed language. Include nuanced explanations and advanced vocabulary in your responses."
        }

        scenario_prompt = scenario_prompts.get(scenario, "You are a helpful assistant.")
        difficulty_prompt = difficulty_prompts.get(difficulty, "Use appropriate language.")
        if first:
            system_prompt = f"{scenario_prompt} {difficulty_prompt} Please ask the user a question directly without any introductory phrases.\nchat_history:{{history}}"
        else:
            system_prompt = f"Please remember the initial instructions and continue to generate responses accordingly. Ask the user a question directly without any introductory phrases.\nchat_history:{{history}}"
            
        prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{input}")
            ]
        )
        return prompt_template

    def create_quiz_prompt_template(self, quiz_type, difficulty, first):
        quiz_type_prompts = {
            "vocabulary": "You are an expert at creating vocabulary quizzes. Create a quiz where the user needs to identify the correct word based on the context.",
            "grammar": "You are an expert at creating grammar quizzes. Create a quiz where the user needs to identify the correct grammar usage."
        }

        difficulty_prompts = {
            "Easy": "Additionally, the difficulty level is Easy, so create the quiz with simple and clear expressions similar to those found in the easier sections of TOEIC exams. "
                    "Use basic vocabulary and straightforward sentence structures, ensuring the question is accessible to beginners.",
            
            "Normal": "Additionally, the difficulty level is Normal, so create the quiz with clear and concise expressions similar to those found in TOEIC exams. "
                    "Ensure that the language and structure are practical and commonly used in everyday situations, focusing on moderate difficulty.",

            "Hard": "Additionally, the difficulty level is Hard, so create the quiz with expressions similar to the more challenging sections of TOEIC exams. "
                    "Use more complex sentence structures and a wider range of vocabulary, but still keep it relevant to TOEIC standards."
        }
        if quiz_type == "vocabulary":
            quiz_example_output = vocabulary_quiz_example_output
        elif quiz_type == "grammar":
            quiz_example_output = grammar_example_output
        else:
            quiz_example_output = vocabulary_quiz_example_output  # 기본값 설정

        quiz_prompt = quiz_type_prompts.get(quiz_type, "You are a helpful assistant creating quizzes.")
        difficulty_prompt = difficulty_prompts.get(difficulty, "Use appropriate language.")

        # 첫 번째 요청일 때는 상세한 지침을 포함하여 프롬프트 생성
        if first:
            system_prompt = f"{quiz_prompt} {difficulty_prompt} Please generate only one quiz question. Use the following format: {quiz_example_output}. " \
                            "Do not provide explanations or feedback. Focus solely on generating the quiz question in the specified format without any introductory text. " \
                            f"\nchat_history:{{history}}"
        else:
            # 이후 요청일 때는 간단하게 지침을 상기시키는 메시지를 포함
            system_prompt = f"Please remember the initial instructions: generate only one quiz question in the specified format. " \
                            "Do not provide any feedback or explanations. Focus solely on generating the quiz question. " \
                            f"Remember that Use the following format: {quiz_example_output}" \
                            f"\nchat_history:{{history}}"

        # 프롬프트 템플릿 구성
        prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{input}")
            ]
        )

        return prompt_template

prompt_manager = PromptManager()