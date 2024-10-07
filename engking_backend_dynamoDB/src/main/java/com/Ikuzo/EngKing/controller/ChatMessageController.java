package com.Ikuzo.EngKing.controller;

import com.Ikuzo.EngKing.dto.ChatMessageRequestDto;
import com.Ikuzo.EngKing.dto.ChatMessageResponseDto;
import com.Ikuzo.EngKing.service.ChatMessageService;
import com.Ikuzo.EngKing.service.S3Service;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Slf4j
@RestController
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
@RequestMapping("/chatmessage")
public class ChatMessageController {

    private final ChatMessageService chatMessageService;
    private final S3Service s3Service;

    @PostMapping("/allmessages")
    public ResponseEntity<List<ChatMessageResponseDto>> selectChatRoomsByChatRoomId(
            @RequestBody ChatMessageRequestDto chatMessageRequestDto, HttpServletRequest request) {

        String memberId = chatMessageRequestDto.getMemberId();
        String chatRoomId = chatMessageRequestDto.getChatRoomId();

        // 요청 시각 기록
        long startTime = System.currentTimeMillis();

        // 클라이언트 IP 주소
        String clientIp = request.getRemoteAddr();

        // 헤더 정보
        String userAgent = request.getHeader("User-Agent");
        String authorization = request.getHeader("Authorization");

        try {
            // 로그 기록 (요청 정보)
            log.info("Request received: memberId={}, chatRoomId={}, method={}, url={}, clientIp={}, userAgent={}, authorization={}",
                    memberId, chatRoomId, request.getMethod(), request.getRequestURL(), clientIp, userAgent, authorization);

            List<ChatMessageResponseDto> chatRoomResponseDtoLists = chatMessageService.selectChatMessagesByChatRoomId(chatRoomId);

            // 각 메시지에 대해 audioFileUrl을 생성하여 추가
            for (ChatMessageResponseDto message : chatRoomResponseDtoLists) {
                if (memberId != null && message.getMessageId() != null) {
                    // 프리사인드 URL 생성
                    String audioUrl = s3Service.generatePreSignedUrl(memberId, chatRoomId, message.getMessageId());

                    // audioFileUrl 설정
                    message.setAudioFileUrl(audioUrl);
                }
            }

            // 요청 처리 시간
            long endTime = System.currentTimeMillis();
            long duration = endTime - startTime;

            // 로그 기록 (응답 성공)
            log.info("Response successful: status=OK, chatRoomId={}, totalMessages={}, duration={}ms",
                    chatRoomId, chatRoomResponseDtoLists.size(), duration);

            return ResponseEntity.status(HttpStatus.OK).body(chatRoomResponseDtoLists);

        } catch (Exception e) {
            // 요청 처리 시간
            long endTime = System.currentTimeMillis();
            long duration = endTime - startTime;

            // 로그 기록 (에러 발생 시)
            log.error("Error processing request: memberId={}, chatRoomId={}, error={}, duration={}ms",
                    memberId, chatRoomId, e.getMessage(), duration, e);

            // 에러 스택 트레이스 포함
            log.error("Stack trace:", e);

            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    @PostMapping("/deletemessage")
    public ResponseEntity<ChatMessageResponseDto> deleteChatMessageByChatRoomIdAndMemberIdAndMessageId(@RequestBody ChatMessageRequestDto chatMessageRequestDto) {
        String memberId = chatMessageRequestDto.getMemberId();
        String chatRoomId = chatMessageRequestDto.getChatRoomId();
        String messageId = chatMessageRequestDto.getMessageId();

        try {
            // 로그 기록
            log.info("Delete request received: memberId={}, chatRoomId={}, messageId={}", memberId, chatRoomId, messageId);

            // 메시지 삭제 처리
            chatMessageService.deleteChatMessage(memberId, chatRoomId, messageId);

            // 삭제 성공 로그 기록
            log.info("Message deleted successfully: memberId={}, chatRoomId={}, messageId={}", memberId, chatRoomId, messageId);

            return ResponseEntity.status(HttpStatus.NO_CONTENT).build();  // 성공 시 204 응답 반환

        } catch (Exception e) {
            // 에러 발생 시 로그 기록
            log.error("Error deleting message: memberId={}, chatRoomId={}, messageId={}, error={}", memberId, chatRoomId, messageId, e.getMessage(), e);

            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();  // 실패 시 500 응답 반환
        }


    }
}
