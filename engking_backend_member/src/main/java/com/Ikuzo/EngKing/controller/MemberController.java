package com.Ikuzo.EngKing.controller;


import com.Ikuzo.EngKing.dto.MemberRequestDto;
import com.Ikuzo.EngKing.dto.MemberResponseDto;
import com.Ikuzo.EngKing.entity.Member;
import com.Ikuzo.EngKing.service.MemberService;
import com.Ikuzo.EngKing.service.S3Service;
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
    public ResponseEntity<Member> registerMember(@RequestBody MemberRequestDto memberRequestDto) throws Exception {

        Member member = memberService.registerMember(memberRequestDto);
        return ResponseEntity.status(HttpStatus.CREATED).body(member); //member 객체를 JSON으로 반환
    }
/*
    @PostMapping("/register")
    public ResponseEntity<MemberResponseDto> registerMember2(@RequestBody MemberRequestDto memberRequestDto) throws Exception {
        String filename="/image/USER_ID_";
        Member member = memberService.registerMember(memberRequestDto);  //memberId가 부여됨

        //MemberResponseDto memberResponseDto=MemberResponseDto.getInfo(member);  //url 필드를 제외한 Dto를 생성 후 반환


        //requestDto로부터 bucketName과 keyName 추출하자!!
        // url 생성
        Map<String, String> metadata=new HashMap<>();
        metadata.put("Content-Type","image/jpeg");
        //String url="FFFF";
        //String url=member.getMemberId().toString();



        String url=s3Service.createPresignedPutUrl(bucketName, filename + member.getMemberId(), metadata);

        //member.setProfileImgUrl(url);

        // member객체의 url 설정 및 repository.save()로 db에 저장까지, 해당 member 객체 반환
        memberService.putUrl(member, url);//DB에 url 넣기 - 잘 안되는데??? 해당 member 객체 반환

        //MemberResponseDto memberResponseDto=MemberResponseDto.getInfo(member);

        //MemberResponseDto.pushUrl(memberResponseDto,url);   // responseDto에 url 넣기

        //memberService.list();

        MemberResponseDto memberResponseDto=MemberResponseDto.getUrl(member);

        return ResponseEntity.status(HttpStatus.CREATED).body(memberResponseDto);
    }*/

    @PostMapping("/login")
    public ResponseEntity<MemberResponseDto> loginMember(@RequestBody MemberRequestDto memberRequestDto) throws Exception {
        MemberResponseDto mrd = memberService.loginMember(memberRequestDto.getEmail(), memberRequestDto.getPassword());

        return ResponseEntity.ok(mrd);
    }

    @PostMapping("/info")
    public ResponseEntity<MemberResponseDto> memberInfo(@RequestParam String email) {
        Member member = memberService.memberList(email);
        //MemberRequestDto mrequestd= MemberRequestDto.builder().email(email).build();  //email을 가진 dto 생성

        // email만 받아서 해당 id를 requestDto에 넣을 것인가??
        MemberRequestDto memberRequestDto= MemberRequestDto.builder().id(member.getMemberId()).build();
        //dto로 요청을 보내고 응답dto를 받자
        //MemberRequestDto memberRequestDto=MemberRequestDto.builder().id(id).build();
        MemberResponseDto mrd=memberService.memberInfo(memberRequestDto);

        return ResponseEntity.ok(mrd);
    }  //email 관련 쿼리로 멤버 정보 조회





    @PatchMapping("/update")
    public ResponseEntity<MemberResponseDto> updateMember( @RequestBody MemberRequestDto memberRequestDto) {
        //Member member=memberService.updateMember(id,memberRequestDto);
        MemberResponseDto mrd=memberService.updateMember(memberRequestDto);
        return ResponseEntity.ok(mrd);  // email이 반환될 것

        //return ResponseEntity.status(HttpStatus.NO_CONTENT).build(); // 수정 성공했지만 응답 본문 X. 204 No Content

        //ok의 인자로 Dto를 넣는 것이 안전하다!
    }

    @DeleteMapping("/delete")
    public ResponseEntity<MemberResponseDto> deleteMember(@RequestBody MemberRequestDto memberRequestDto) {

        String email=memberRequestDto.getEmail();
        memberService.deleteMember(email);
        return ResponseEntity.noContent().build();
    }





}
