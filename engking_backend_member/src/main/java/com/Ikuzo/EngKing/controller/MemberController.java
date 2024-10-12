package com.Ikuzo.EngKing.controller;


import com.Ikuzo.EngKing.dto.MemberRequestDto;
import com.Ikuzo.EngKing.dto.MemberResponseDto;
import com.Ikuzo.EngKing.entity.Member;
import com.Ikuzo.EngKing.service.MemberService;
import com.Ikuzo.EngKing.service.S3Service;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.constraints.Email;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;


@Slf4j
@RestController //JSON 형식 반환
@RequiredArgsConstructor //final, @NonNull 에 대한 생성자 자동생성
@CrossOrigin(origins = "*")
@RequestMapping("/member")
public class MemberController {
    private final MemberService memberService;
    private final S3Service s3Service;
    private final String bucketName="engking-bucket-image";

    @PostMapping("/register")
    public ResponseEntity<Member> registerMember(@RequestBody MemberRequestDto memberRequestDto, HttpServletRequest request) {

        long startTime=System.currentTimeMillis();

        try {

            log.info("Request received: method={}, url={}, data={}",request.getMethod(), request.getRequestURL(), request);

            Member member = memberService.registerMember(memberRequestDto);

            long endTime=System.currentTimeMillis();
            long duration=endTime - startTime;

            log.info("Response successful : status=201, duration={}ms" , duration);
            return ResponseEntity.status(HttpStatus.CREATED).body(member); //member 객체를 JSON으로 반환

        } catch(Exception e) {
            long endTime=System.currentTimeMillis();
            long duration=endTime-startTime;

            log.error("Error occured: duration={}ms, message={}", duration,e.getMessage(),e);

            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();

        }

    }

    @PostMapping("/login")
    public ResponseEntity<MemberResponseDto> loginMember(@RequestBody MemberRequestDto memberRequestDto) throws Exception {
        try {
            log.info("Login attempt for email={}", memberRequestDto.getEmail());
            MemberResponseDto mrd = memberService.loginMember(memberRequestDto.getEmail(), memberRequestDto.getPassword());
            log.info("Login successful for email={}", memberRequestDto.getEmail());
            return ResponseEntity.ok(mrd);

        } catch (Exception e) {
            log.error("Login failed for email={}, message={}", memberRequestDto.getEmail(), e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
    }

    @PostMapping("/info")
    public ResponseEntity<MemberResponseDto> memberInfo(@RequestParam String email) {
        try {
            log.info("Fetching member info for email={}", email);

            // 로직 시작
            Member member = memberService.memberList(email);
            MemberRequestDto memberRequestDto= MemberRequestDto.builder().id(member.getMemberId()).build();
            MemberResponseDto mrd=memberService.memberInfo(memberRequestDto);

            log.info("Member info retrieved successfully for email={}", email);
            return ResponseEntity.ok(mrd);

        } catch (Exception e) {

            log.error("Failed to fetch member info for email={}, message={}", email, e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.NOT_FOUND).build();
        }


    }  //email 관련 쿼리로 멤버 정보 조회





    @PatchMapping("/update")
    public ResponseEntity<MemberResponseDto> updateMember( @RequestBody MemberRequestDto memberRequestDto) {
        try {
            log.info("Updating member info for email={}", memberRequestDto.getEmail());
            MemberResponseDto mrd=memberService.updateMember(memberRequestDto);
            log.info("Member info updated successfully for email={}", memberRequestDto.getEmail());

            return ResponseEntity.ok(mrd);  // email이 반환될 것
        } catch (Exception e) {
            log.error("Failed to update member info for email={}, message={}", memberRequestDto.getEmail(), e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build(); // 수정 성공했지만 응답 본문 X. 204 No Content
        }

        //ok의 인자로 Dto를 넣는 것이 안전하다!
    }

    @DeleteMapping("/delete")
    public ResponseEntity<MemberResponseDto> deleteMember(@RequestBody MemberRequestDto memberRequestDto) {
        String email=memberRequestDto.getEmail();
        try {
            log.info("Deleting member with email={}", memberRequestDto.getEmail());
            memberService.deleteMember(email);
            log.info("Member deleted successfully for email={}", memberRequestDto.getEmail());
            return ResponseEntity.noContent().build();
        } catch (Exception e) {
            log.error("Failed to delete member with email={}, message={}", memberRequestDto.getEmail(), e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }

    }


}
