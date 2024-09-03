def generate_unique_filename(member_id: str, chat_room_id: str, message_id: str) -> str:
    """고유한 파일명을 생성하는 함수"""
    return f"{member_id}/{chat_room_id}/{message_id}.mp3"  # 파일명 포맷