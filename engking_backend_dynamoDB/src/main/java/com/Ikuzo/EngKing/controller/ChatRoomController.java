package com.Ikuzo.EngKing.controller;

import com.Ikuzo.EngKing.dto.ChatRoomRequestDto;
import com.Ikuzo.EngKing.dto.ChatRoomResponseDto;
import com.Ikuzo.EngKing.service.ChatRoomService;
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
@RequestMapping("/chatroom")
public class ChatRoomController {

    private final ChatRoomService chatRoomService;

    @PostMapping("/chatroomlist")
    public ResponseEntity<List<ChatRoomResponseDto>> selectChatRoomsByMemberId(
            @RequestBody ChatRoomRequestDto chatRoomRequestDto, HttpServletRequest request) {

        String memberId = chatRoomRequestDto.getMemberId();

        // 요청 시각 기록
        long startTime = System.currentTimeMillis();

        // 클라이언트 IP 주소
        String clientIp = request.getRemoteAddr();

        // 헤더 정보
        String userAgent = request.getHeader("User-Agent");
        String authorization = request.getHeader("Authorization");

        try {
            // 로그 기록 (요청 정보)
            log.info("Request received: memberId={}, method={}, url={}, clientIp={}, userAgent={}, authorization={}",
                    memberId, request.getMethod(), request.getRequestURL(), clientIp, userAgent, authorization);

            // 서비스 호출하여 채팅방 리스트 가져오기
            List<ChatRoomResponseDto> chatRoomResponseDtoLists = chatRoomService.selectChatRoomsByMemberId(memberId);

            // 요청 처리 시간
            long endTime = System.currentTimeMillis();
            long duration = endTime - startTime;

            // 로그 기록 (응답 성공)
            log.info("Response successful: status=OK, memberId={}, totalChatRooms={}, duration={}ms",
                    memberId, chatRoomResponseDtoLists.size(), duration);

            return ResponseEntity.status(HttpStatus.OK).body(chatRoomResponseDtoLists);

        } catch (Exception e) {
            // 요청 처리 시간
            long endTime = System.currentTimeMillis();
            long duration = endTime - startTime;

            // 로그 기록 (에러 발생 시)
            log.error("Error processing request: memberId={}, error={}, duration={}ms",
                    memberId, e.getMessage(), duration, e);

            // 에러 스택 트레이스 포함
            log.error("Stack trace:", e);

            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    @PostMapping("/deletechatroom")
    public ResponseEntity<ChatRoomResponseDto> deleteChatRoomByChatRoomId(
            @RequestBody ChatRoomRequestDto chatRoomRequestDto, HttpServletRequest request) {

        String memberId = chatRoomRequestDto.getMemberId();
        String chatRoomId = chatRoomRequestDto.getChatRoomId();

        // 요청 시각 기록
        long startTime = System.currentTimeMillis();

        // 클라이언트 IP 주소
        String clientIp = request.getRemoteAddr();

        // 헤더 정보
        String userAgent = request.getHeader("User-Agent");
        String authorization = request.getHeader("Authorization");

        try {
            // 로그 기록 (요청 정보)
            log.info("Request to delete chat room: memberId={}, chatRoomId={}, method={}, url={}, clientIp={}, userAgent={}, authorization={}",
                    memberId, chatRoomId, request.getMethod(), request.getRequestURL(), clientIp, userAgent, authorization);

            // 채팅방 삭제
            ChatRoomResponseDto chatRoomResponseDto = chatRoomService.deleteChatRoomByChatRoomIdAndMemberId(chatRoomId, memberId);

            // 요청 처리 시간
            long endTime = System.currentTimeMillis();
            long duration = endTime - startTime;

            // 로그 기록 (응답 성공)
            log.info("Chat room deleted successfully: status=OK, memberId={}, chatRoomId={}, duration={}ms",
                    memberId, chatRoomId, duration);

            return ResponseEntity.status(HttpStatus.OK).body(chatRoomResponseDto);

        } catch (Exception e) {
            // 요청 처리 시간
            long endTime = System.currentTimeMillis();
            long duration = endTime - startTime;

            // 로그 기록 (에러 발생 시)
            log.error("Error deleting chat room: memberId={}, chatRoomId={}, error={}, duration={}ms",
                    memberId, chatRoomId, e.getMessage(), duration, e);

            // 에러 스택 트레이스 포함
            log.error("Stack trace:", e);

            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
}
