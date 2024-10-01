package com.Ikuzo.EngKing.controller;

import com.Ikuzo.EngKing.dto.ChatRoomRequestDto;
import com.Ikuzo.EngKing.dto.ChatRoomResponseDto;
import com.Ikuzo.EngKing.service.ChatRoomService;
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
    public ResponseEntity<List<ChatRoomResponseDto>> selectChatRoomsByMemberId(@RequestBody ChatRoomRequestDto chatRoomRequestDto) {
        String memberId = chatRoomRequestDto.getMemberId();

        try {
            // 로그 기록 (요청 정보)
            log.info("Request received: memberId={}", memberId);

            // 서비스 호출하여 채팅방 리스트 가져오기
            List<ChatRoomResponseDto> chatRoomResponseDtoLists = chatRoomService.selectChatRoomsByMemberId(memberId);

            log.info("Response successful: status=OK, memberId={}, totalChatRooms={}", memberId, chatRoomResponseDtoLists.size());
            return ResponseEntity.status(HttpStatus.OK).body(chatRoomResponseDtoLists);

        } catch (Exception e) {
            log.error("Error processing request: memberId={}, error={}", memberId, e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    @PostMapping("/deletechatroom")
    public ResponseEntity<ChatRoomResponseDto> deleteChatRoomByChatRoomId(@RequestBody ChatRoomRequestDto chatRoomRequestDto) {
        String memberId = chatRoomRequestDto.getMemberId();
        String chatRoomId = chatRoomRequestDto.getChatRoomId();

        try {
            // 로그 기록 (요청 정보)
            log.info("Request to delete chat room: memberId={}, chatRoomId={}", memberId, chatRoomId);

            // 채팅방 삭제
            ChatRoomResponseDto chatRoomResponseDto = chatRoomService.deleteChatRoomByChatRoomIdAndMemberId(chatRoomId, memberId);

            log.info("Chat room deleted successfully: status=OK, memberId={}, chatRoomId={}", memberId, chatRoomId);
            return ResponseEntity.status(HttpStatus.OK).body(chatRoomResponseDto);

        } catch (Exception e) {
            log.error("Error deleting chat room: memberId={}, chatRoomId={}, error={}", memberId, chatRoomId, e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

}
