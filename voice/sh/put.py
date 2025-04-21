import requests
import argparse

# 인자 파서 설정
parser = argparse.ArgumentParser(description='Upload a file to S3 using a pre-signed URL.')
parser.add_argument('presigned_url', type=str, help='The pre-signed URL for uploading the file.')
parser.add_argument('file_path', type=str, help='The path to the file to be uploaded.')

# 인자 파싱
args = parser.parse_args()

# S3 pre-signed URL
presigned_url = args.presigned_url
# 업로드할 음성 파일 경로
file_path = args.file_path

# 파일을 열고 PUT 요청을 보냅니다.
with open(file_path, 'rb') as f:
    # 파일을 pre-signed URL로 업로드
    response = requests.put(presigned_url, data=f)

# 응답 상태 코드 확인
if response.status_code == 200:
    print("파일 업로드 성공!")
else:
    print(f"파일 업로드 실패. 상태 코드: {response.status_code}")
    print("응답 내용:", response.text)
