package com.Ikuzo.EngKing.service;

import com.Ikuzo.EngKing.dto.ChatMessageResponseDto;
import com.Ikuzo.EngKing.entity.ChatMessages;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.dynamodb.model.*;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class ChatMessageService {

    private final DynamoDbClient dynamoDbClient;

    public List<ChatMessageResponseDto> selectChatMessagesByChatRoomId(String chatRoomId) {
        // DynamoDB에서 ChatRoomId로 ChatMessages 조회
        Map<String, AttributeValue> expressionAttributeValues = new HashMap<>();
        expressionAttributeValues.put(":ChatRoomId", AttributeValue.builder().s(chatRoomId).build());

        // Query 요청 생성
        QueryRequest queryRequest = QueryRequest.builder()
                .tableName("EngKing-ChatMessages")
                .keyConditionExpression("ChatRoomId = :ChatRoomId")
                .expressionAttributeValues(expressionAttributeValues)
                .build();

        try {
            log.info("Querying chat messages: chatRoomId={}", chatRoomId);
            QueryResponse queryResponse = dynamoDbClient.query(queryRequest);
            List<Map<String, AttributeValue>> items = queryResponse.items();

            if (items.isEmpty()) {
                log.info("No messages found for chatRoomId={}", chatRoomId);
                return new ArrayList<>();  // 조회된 항목이 없을 경우 빈 리스트 반환
            }

            // 항목을 ChatMessageResponseDto로 변환
            List<ChatMessageResponseDto> responseDtos = new ArrayList<>();
            for (Map<String, AttributeValue> item : items) {
                ChatMessageResponseDto responseDto = new ChatMessageResponseDto();

                // 각 속성에 대해 null 체크 수행
                responseDto.setChatRoomId(item.get("ChatRoomId") != null ? item.get("ChatRoomId").s() : null);
                responseDto.setMessageTime(item.get("MessageTime") != null ?
                        ChatMessages.LocalDateTimeConverter.unconvert(item.get("MessageTime").s()) : null);
                responseDto.setMessageId(item.get("MessageId") != null ? item.get("MessageId").s() : null);
                responseDto.setSenderId(item.get("SenderId") != null ? item.get("SenderId").s() : null);
                responseDto.setMessageText(item.get("MessageText") != null ? item.get("MessageText").s() : null);
                responseDto.setAudioFileUrl(item.get("AudioFileUrl") != null ? item.get("AudioFileUrl").s() : null);
                responseDto.setScore(item.get("Score") != null ? item.get("Score").s() : null);
                responseDto.setFeedback(item.get("Feedback") != null ? item.get("Feedback").s() : null);

                responseDtos.add(responseDto);
            }
            log.info("Successfully retrieved {} messages for chatRoomId={}", responseDtos.size(), chatRoomId);
            return responseDtos;

        } catch (Exception e) {
            log.error("Failed to query chat messages: chatRoomId={}, error={}", chatRoomId, e.getMessage());
            return new ArrayList<>();
        }
    }

    public void deleteChatMessage(String memberId, String chatRoomId, String messageId) {
        try {
            // Step 1: Scan으로 messageId로 해당 항목 조회 (chatRoomId도 함께 사용하여 정확한 항목 조회)
            Map<String, AttributeValue> expressionAttributeValues = new HashMap<>();
            expressionAttributeValues.put(":ChatRoomId", AttributeValue.builder().s(chatRoomId).build());
            expressionAttributeValues.put(":MessageId", AttributeValue.builder().s(messageId).build());

            ScanRequest scanRequest = ScanRequest.builder()
                    .tableName("EngKing-ChatMessages")
                    .filterExpression("ChatRoomId = :ChatRoomId AND MessageId = :MessageId")
                    .expressionAttributeValues(expressionAttributeValues)
                    .build();

            ScanResponse scanResponse = dynamoDbClient.scan(scanRequest);
            List<Map<String, AttributeValue>> items = scanResponse.items();

            // Step 2: 조회된 항목이 있는지 확인
            if (items.isEmpty()) {
                log.info("No message found for deletion: memberId={}, chatRoomId={}, messageId={}", memberId, chatRoomId, messageId);
                return;  // 항목이 없으면 삭제할 필요가 없으므로 종료
            }

            // Step 3: messageTime을 추출
            Map<String, AttributeValue> item = items.get(0);  // 첫 번째 항목을 가져옴 (일치하는 항목이 1개일 것으로 가정)
            String messageTime = item.get("MessageTime").s();  // messageTime을 추출

            // Step 4: 파티션 키와 정렬 키로 항목 삭제
            Map<String, AttributeValue> keyToDelete = new HashMap<>();
            keyToDelete.put("ChatRoomId", AttributeValue.builder().s(chatRoomId).build());  // 파티션 키
            keyToDelete.put("MessageTime", AttributeValue.builder().s(messageTime).build());  // 정렬 키

            DeleteItemRequest deleteRequest = DeleteItemRequest.builder()
                    .tableName("EngKing-ChatMessages")
                    .key(keyToDelete)
                    .build();

            DeleteItemResponse deleteResponse = dynamoDbClient.deleteItem(deleteRequest);

            log.info("Delete successful for messageId={}, chatRoomId={}, messageTime={}, memberId={}", messageId, chatRoomId, messageTime, memberId);
        } catch (DynamoDbException e) {
            log.error("Failed to delete message: memberId={}, chatRoomId={}, messageId={}, error={}", memberId, chatRoomId, messageId, e.getMessage());
        }
    }



}
