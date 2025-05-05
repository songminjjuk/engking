import time
import boto3
import redis
import statistics
import json

# Redis 설정
redis_url = ''
redis_client = redis.StrictRedis.from_url(redis_url)

# DynamoDB 설정
dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2')
table = dynamodb.Table('')
key = 'test-key'
dynamo_key = {'test-key': key}

# 테스트 데이터
test_data = {
    "AI": "What your favorite color?",
    "Human": "Hi. Nice to meet you! I like blue.",
    "AI2": "Why do you like blue color?",
    "Human2": "Because . . ."
}

# 반복 횟수
ITERATIONS = 10

def test_redis_write():
    times = []
    for _ in range(ITERATIONS):
        start = time.time()
        redis_client.set('test-key', json.dumps(test_data))
        end = time.time()
        times.append(end - start)
    return times

def test_redis_read():
    redis_client.set('test-key', json.dumps(test_data))
    times = []
    for _ in range(ITERATIONS):
        start = time.time()
        redis_client.get('test-key')
        end = time.time()
        times.append(end - start)
    return times

def test_redis_rw_combined():
    times = []
    for _ in range(ITERATIONS):
        start = time.time()
        redis_client.set('test-key', json.dumps(test_data))
        redis_client.get('test-key')
        end = time.time()
        times.append(end - start)
    return times

def test_dynamodb_write():
    times = []
    for _ in range(ITERATIONS):
        start = time.time()
        table.put_item(Item={**dynamo_key, **test_data})
        end = time.time()
        times.append(end - start)
    return times

def test_dynamodb_read():
    table.put_item(Item={**dynamo_key, **test_data})
    times = []
    for _ in range(ITERATIONS):
        start = time.time()
        table.get_item(Key=dynamo_key)
        end = time.time()
        times.append(end - start)
    return times

def test_dynamodb_rw_combined():
    times = []
    for _ in range(ITERATIONS):
        start = time.time()
        table.put_item(Item={**dynamo_key, **test_data})
        table.get_item(Key=dynamo_key)
        end = time.time()
        times.append(end - start)
    return times


# 실행
redis_write = test_redis_write()
redis_read = test_redis_read()
redis_rw = test_redis_rw_combined()

dynamo_write = test_dynamodb_write()
dynamo_read = test_dynamodb_read()
dynamo_rw = test_dynamodb_rw_combined()

# 삭제
redis_client.delete('test-key')
table.delete_item(Key=dynamo_key)

# 결과
# print(f"Redis 쓰기 평균 응답 시간: {statistics.mean(redis_write) * 1000:.2f} ms")
# print(f"Redis 읽기 평균 응답 시간: {statistics.mean(redis_read) * 1000:.2f} ms")
print(f"Redis 평균 응답 시간: {statistics.mean(redis_rw) * 1000:.2f} ms")
# print(f"DynamoDB 쓰기 평균 응답 시간: {statistics.mean(dynamo_write) * 1000:.2f} ms")
# print(f"DynamoDB 읽기 평균 응답 시간: {statistics.mean(dynamo_read) * 1000:.2f} ms")
print(f"DynamoDB 평균 응답 시간: {statistics.mean(dynamo_rw) * 1000:.2f} ms")
