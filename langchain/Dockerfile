FROM python:3.12.3-slim

ENV TZ=Asia/Seoul
RUN apt-get update && apt-get install -y tzdata && \
    ln -snf /usr/share/zoneinfo/Asia/Seoul /etc/localtime && echo "Asia/Seoul" > /etc/timezone

ENV PYTHONDONTWRITEBYTECODE=1 
ENV PYTHONUNBUFFERED=1 

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]