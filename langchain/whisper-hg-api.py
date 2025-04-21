import requests
import time
import jiwer  # WER 계산을 위한 라이브러리
import datetime

# Hugging Face Whisper API URL 및 헤더 설정
API_URL = "https://api-inference.huggingface.co/models/openai/whisper-small"
headers = {"Authorization": f"Bearer api-key"}

# 참고 텍스트 (실제 음성 파일이 담고 있는 텍스트)
reference_text = ("Before he had time to answer, a much-encumbered Vera burst into the room "
                  "with the question: I say, can I leave these here? These were a small black pig "
                  "and a lusty specimen of black-red gamecock.")

# STT 변환 및 성능 측정 함수
def transcribe_with_hf(filename):
    with open(filename, "rb") as f:
        data = f.read()

    # 실행 시간 측정 시작
    start_time = time.time()

    # API 호출 (STT 요청)
    response = requests.post(
        API_URL, 
        headers=headers, 
        data=data, 
        params={"language": "en"}  # 언어를 영어로 설정
    )

    # 실행 시간 측정 종료
    end_time = time.time()
    execution_time = end_time - start_time  # 실행 시간 계산

    # 결과 처리
    result = response.json()
    transcribed_text = result.get('text', '')

    # 오류율 (WER) 계산
    wer = jiwer.wer(reference_text, transcribed_text)

    # 결과 출력
    print(f"Transcribed Text: {transcribed_text}")
    print(f"Execution Time: {str(datetime.timedelta(seconds=execution_time))}")
    print(f"Word Error Rate (WER): {wer * 100:.2f}%")

    return transcribed_text, execution_time, wer

# 예시 사용: 오디오 파일 경로 설정
audio_file_path = "sample2.flac"

# STT 변환 및 성능 측정
transcribed_text, execution_time, wer = transcribe_with_hf(audio_file_path)
