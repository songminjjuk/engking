package com.Ikuzo.EngKing.service;

import com.Ikuzo.EngKing.constant.Authority;
import com.Ikuzo.EngKing.constant.Existence;
import com.Ikuzo.EngKing.dto.MemberRequestDto;
import com.Ikuzo.EngKing.dto.MemberResponseDto;
import com.Ikuzo.EngKing.entity.Member;
import com.Ikuzo.EngKing.repository.MemberRepository;
import jakarta.persistence.EntityNotFoundException;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.config.annotation.authentication.builders.AuthenticationManagerBuilder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.Bucket;
import software.amazon.awssdk.services.s3.model.ListBucketsRequest;
import software.amazon.awssdk.services.s3.model.ListBucketsResponse;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

@Service
@Transactional
@Slf4j
@RequiredArgsConstructor
public class MemberService {
    private final AuthenticationManagerBuilder managerBuilder;
    private final MemberRepository memberRepository;
    private final HttpSession session;
    private final PasswordEncoder passwordEncoder;
    private final S3Service s3Service;
    private final String bucketName="engking-bucket-image";


    public Member registerMember(MemberRequestDto memberRequestDto) {
        log.info("Attempting to register a new member: email={}", memberRequestDto.getEmail());
        try {
            // 패스워드 암호화
            String encodedPassword = passwordEncoder.encode(memberRequestDto.getPassword());

            // 회원 엔티티 생성
            Member member = Member.builder()
                    .email(memberRequestDto.getEmail())
                    .password(encodedPassword)
                    .name(memberRequestDto.getName())
                    .phone(memberRequestDto.getPhone())
                    .birthday(memberRequestDto.getBirthday())
                    .signUpTime(LocalDateTime.now())  // register
                    .authority(Authority.ROLE_MEMBER) // 기본 권한 설정
                    .existence(Existence.YES) // 기본 존재 상태 설정
                    .intro(memberRequestDto.getIntro())
                    .profileImgUrl(null)
                    .build();

            Member savedMember = memberRepository.save(member);
            log.info("Member successfully registered: email={}, memberId={}", savedMember.getEmail(), savedMember.getMemberId());
            return savedMember;
        } catch (Exception e) {
            log.error("Error occurred while registering member: email={}, error={}", memberRequestDto.getEmail(), e.getMessage());
            throw e;

        }

    }

    public MemberResponseDto loginMember(String email, String password) throws Exception {

        log.info("Login attempt: email={}", email);
        try {
            // 이메일로 회원 조회
            Optional<Member> optionalMember = memberRepository.findByEmail(email);
            if (optionalMember.isPresent()) {
                Member member = optionalMember.get();
                // 비밀번호 검증
                if (passwordEncoder.matches(password, member.getPassword())) {
                    // 세션에 회원 정보 저장
                    session.setAttribute("member", member);
                    return MemberResponseDto.getLogin(member);

                } else {
                    throw new Exception("비밀번호가 일치하지 않습니다.");
                }
            } else {
                throw new Exception("회원 정보를 찾을 수 없습니다.");
            }
        } catch (Exception e){
            log.error("Error during login attempt for email={}: {}", email, e.getMessage());
            throw e;
        }

    }

    public Member memberList(String email) {
        Optional<Member> optionalMember =memberRepository.findByEmail(email);
        Member member = optionalMember.get();
        // 해당 이메일 가진 회원 조회. 회원의 모든 attribute가 필요해서 객체를 반환한것?
        return member;
    }

    public MemberResponseDto updateMember(MemberRequestDto memberRequestDto){

        Long id=memberRequestDto.getId();
        log.info("Attempting to update member: id={}", id);
        try {
            Member member=memberRepository.findById(id).orElseThrow(()->new IllegalArgumentException("Invalid member Id:" + id));

            if(memberRequestDto.getPassword()!=null) {
                String encodedPassword=passwordEncoder.encode(memberRequestDto.getPassword());
                member.setPassword(encodedPassword);
            }
            if(memberRequestDto.getName()!=null) member.setName(memberRequestDto.getName());
            if(memberRequestDto.getBirthday()!=null) member.setBirthday(memberRequestDto.getBirthday());
            if(memberRequestDto.getPhone()!=null) member.setPhone(memberRequestDto.getPhone());
            if(memberRequestDto.getIntro()!=null) member.setIntro(memberRequestDto.getIntro());


            //memberRepository.save(member);  // save의 인자가 반환값
            String keyName=String.format("image/USER_ID_%s.PNG",id.toString());
            Map<String,String> metadata=new HashMap<>();
            metadata.put("Content-Type","image/jpg");
            String url=s3Service.createPresignedPutUrl(bucketName, keyName,metadata);
            memberRepository.save(member);

            log.info("Member updated successfully: id={}", id);
            return MemberResponseDto.getUrl(url);

        } catch (Exception e) {
            log.error("Error updating member: id={}, error={}", id, e.getMessage());
            throw e;
        }
    }

    public void deleteMember(String email){
        log.info("Member deleted successfully: email={}", email);
        try {
            Member member=memberRepository.findByEmail(email).orElseThrow(()->new IllegalArgumentException("Invalid member Id:" + email));
            memberRepository.delete(member);
            log.info("Member deleted successfully: email={}", email);
        } catch (Exception e) {
            log.error("Error deleting member: email={}, error={}", email, e.getMessage());
            throw e;
        }

    }

    public MemberResponseDto memberInfo(MemberRequestDto mrequestd){

        Long id=mrequestd.getId();
        log.info("Fetching member info: id={}", id);
        try {
            Member member=memberRepository.findById(id).orElseThrow(()->new IllegalArgumentException("Invalid member Id:" + id));
            String keyName=String.format("image/USER_ID_%s.PNG",id.toString());
            String url=s3Service.createPresignedGetUrl(bucketName, keyName);

            log.info("Successfully fetched member info and generated S3 URL: id={}", id);
            return MemberResponseDto.getInfo(member,url);  //responseDto를 반환

        } catch (Exception e) {
            log.error("Error fetching member info: id={}, error={}", id, e.getMessage());
            throw e;
        }

    }

}
