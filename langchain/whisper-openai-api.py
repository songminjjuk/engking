# import openai

# # OpenAI API 설정
# openai.api_key = ""
# def transcribe_audio(audio_file_path):
#     with open(audio_file_path, "rb") as audio_file:
#         transcript = openai.Audio.transcribe(
#             model="whisper-1",
#             file=audio_file
#         )
#     return transcript["text"]

# # 예시 사용: 현재 음성 파일을 STT 변환
# audio_file_path = "sample2.flac"  # 사용자가 가지고 있는 음성 파일 경로
# transcribed_text = transcribe_audio(audio_file_path)

# # 결과 출력
# print(f"Transcribed Text: {transcribed_text}")