package com.Ikuzo.EngKing.service;

import com.Ikuzo.EngKing.dto.ChatRoomResponseDto;
import com.Ikuzo.EngKing.entity.ChatRoom;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.dynamodb.model.*;

import java.time.LocalDateTime;
import java.util.*;

@Service
public class ChatRoomService {

    private final DynamoDbClient dynamoDbClient;
    private final RestTemplate restTemplate;

    @Autowired
    public ChatRoomService(DynamoDbClient dynamoDbClient, RestTemplate restTemplate) {
        this.dynamoDbClient = dynamoDbClient;
        this.restTemplate = restTemplate;
    }

    // 회원 번호로 채팅방 내역 조회
    public List<ChatRoomResponseDto> selectChatRoomsByMemberId(String memberId) {
        // DynamoDB에서 MemberId로 ChatRoom 조회
        Map<String, AttributeValue> expressionAttributeValues = new HashMap<>();
        expressionAttributeValues.put(":MemberId", AttributeValue.builder().s(memberId).build());

        // Scan 요청 생성 (전체 테이블을 검색)
        ScanRequest scanRequest = ScanRequest.builder()
                .tableName("EngKing-ChatRoom")
                .filterExpression("MemberId = :MemberId")
                .expressionAttributeValues(expressionAttributeValues)
                .build();

        try {
            ScanResponse scanResponse = dynamoDbClient.scan(scanRequest);
            List<Map<String, AttributeValue>> items = scanResponse.items();

            if (items.isEmpty()) {
                return Collections.emptyList();  // 조회된 항목이 없을 경우
            }

            // 항목을 ChatRoomResponseDto로 변환
            List<ChatRoomResponseDto> responseDtos = new ArrayList<>();
            for (Map<String, AttributeValue> item : items) {
                ChatRoomResponseDto responseDto = new ChatRoomResponseDto();

                // 각 속성에 대해 null 체크 수행
                responseDto.setChatRoomId(item.get("ChatRoomId") != null ? item.get("ChatRoomId").s() : null);
                responseDto.setMemberId(item.get("MemberId") != null ? item.get("MemberId").s() : null);
                responseDto.setDifficulty(item.get("Difficulty") != null ? item.get("Difficulty").s() : null);
                responseDto.setTopic(item.get("Topic") != null ? item.get("Topic").s() : null);
                responseDto.setQuiz_type(item.get("Quiz_type") != null ? item.get("Quiz_type").s() : null);

                // CreatedTime 속성에 대해 null 체크와 변환 수행
                responseDto.setCreatedTime(item.get("CreatedTime") != null ?
                        ChatRoom.LocalDateTimeConverter.unconvert(item.get("CreatedTime").s()) : null);

                responseDto.setQueryResult(true);

                responseDtos.add(responseDto);
            }

            return responseDtos;

        } catch (Exception e) {
            System.err.println("Failed to scan chat room by MemberId: " + e.getMessage());
            return Collections.emptyList();
        }
    }

    // ChatRoomId와 MemberId로 ChatRoom 삭제
    public ChatRoomResponseDto deleteChatRoomByChatRoomIdAndMemberId(String chatRoomId, String memberId) {
        // 삭제할 항목의 키 구성
        Map<String, AttributeValue> key = new HashMap<>();
        key.put("ChatRoomId", AttributeValue.builder().s(chatRoomId).build());
        key.put("MemberId", AttributeValue.builder().s(memberId).build());

        // DeleteItem 요청 생성
        DeleteItemRequest deleteRequest = DeleteItemRequest.builder()
                .tableName("EngKing-ChatRoom")
                .key(key)
                .build();

        try {
            DeleteItemResponse deleteResponse = dynamoDbClient.deleteItem(deleteRequest);

            // 응답 처리 및 DTO 생성
            ChatRoomResponseDto responseDto = new ChatRoomResponseDto();
            responseDto.setChatRoomId(chatRoomId);
            responseDto.setMemberId(memberId);
            responseDto.setQueryResult(true);  // 삭제 성공

            return responseDto;

        } catch (Exception e) {
            System.err.println("Failed to delete chat room by ChatRoomId and MemberId: " + e.getMessage());

            // 예외 발생 시 실패한 상태를 담은 DTO 반환
            ChatRoomResponseDto responseDto = new ChatRoomResponseDto();
            responseDto.setChatRoomId(chatRoomId);
            responseDto.setMemberId(memberId);
            responseDto.setQueryResult(false);  // 삭제 실패

            return responseDto;
        }
    }

}
