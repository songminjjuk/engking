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
        // 회원 저장
        return memberRepository.save(member);
    }

    public MemberResponseDto loginMember(String email, String password) throws Exception {
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
    }

    public Member memberList(String email) {
        Optional<Member> optionalMember =memberRepository.findByEmail(email);
        Member member = optionalMember.get();
        // 해당 이메일 가진 회원 조회. 회원의 모든 attribute가 필요해서 객체를 반환한것?
        return member;
    }

    public MemberResponseDto updateMember(MemberRequestDto memberRequestDto){
        // 바뀐애들에 대해서만 할까? 아니면 그냥 다 할까?
        //json에서 null로 쏘면 아예 아무 작업 안 하도록 하는 방법!
        /********************************************************/
        // 사용자가 수정할 수 있는 필드에 대해서만 해주면 될듯
        //Member의 모든 필드에 대해 if문을 해줄 필요는 없을것 같으나 확인해보자!!!
        /********************************************************/
        Long id=memberRequestDto.getId();
        Member member=memberRepository.findById(id).orElseThrow(()->new IllegalArgumentException("Invalid member Id:" + id));
        //if(memberRequestDto.getEmail()!=null)  member.setEmail(memberRequestDto.getEmail());
        if(memberRequestDto.getPassword()!=null) {
            String encodedPassword=passwordEncoder.encode(memberRequestDto.getPassword());
            member.setPassword(encodedPassword);
        }
        if(memberRequestDto.getName()!=null) member.setName(memberRequestDto.getName());
        if(memberRequestDto.getBirthday()!=null) member.setBirthday(memberRequestDto.getBirthday());
        if(memberRequestDto.getPhone()!=null) member.setPhone(memberRequestDto.getPhone());
        if(memberRequestDto.getIntro()!=null) member.setIntro(memberRequestDto.getIntro());
        //if(memberRequestDto.getProfileImgUrl()!=null) member.setProfileImgUrl(memberRequestDto.getProfileImgUrl());

        // entity를 responsedto에 저장해서 반환해라!!!

        //memberRepository.save(member);  // save의 인자가 반환값
        String keyName=String.format("image/USER_ID_%s.PNG",id.toString());
        Map<String,String> metadata=new HashMap<>();
        metadata.put("Content-Type","image/jpg");
        String url=s3Service.createPresignedPutUrl(bucketName, keyName,metadata);
        memberRepository.save(member);
        return MemberResponseDto.getUrl(url);  //url 담은 responseDto 반환

    }

    public void deleteMember(String email){
        Member member=memberRepository.findByEmail(email).orElseThrow(()->new IllegalArgumentException("Invalid member Id:" + email));
        memberRepository.delete(member);

    }

    public MemberResponseDto memberInfo(MemberRequestDto mrequestd){
        //String email=mrequestd.getEmail();
        Long id=mrequestd.getId();
        Member member=memberRepository.findById(id).orElseThrow(()->new IllegalArgumentException("Invalid member Id:" + id));

        //member.getEmail()을 response에 넣자
        /************************************************/
        // url; 생성하기!!!!!! **********************************/
        //String bucketName="engking-bucket-image";

        String keyName=String.format("image/USER_ID_%s.PNG",id.toString());
        //String keyName="image/USER_ID_"+id.toString()+".jpeg";
        String url=s3Service.createPresignedGetUrl(bucketName, keyName);



        // info 및 Get할 수 있는 URL까지 생성 후 보내야 한다.
        return MemberResponseDto.getInfo(member,url);  //responseDto를 반환
    }

    public MemberResponseDto registerMember2(MemberRequestDto memberRequestDto) {
        // 패스워드 암호화
        String encodedPassword = passwordEncoder.encode(memberRequestDto.getPassword());
/*
        if(memberRequestDto.getProfileImgUrl()==null||memberRequestDto.getProfileImgUrl().isEmpty()) {
            memberRequestDto.setImgUrl();
        }*/
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
                //.profileImgUrl(memberRequestDto.getProfileImgUrl())
                .build();



        // 회원 저장
        //return MemberResponseDto.getInfo(memberRepository.save(member));
        return MemberResponseDto.getEmail(memberRepository.save(member));
    }

    public Member putUrl(Member member, String url) {
        member.setProfileImgUrl(url);
        return memberRepository.save(member);
    }

    // aws credential 잘 되어서 버킷리스트를 db에 저장하도록 하는 함수
    public void list(){
        S3Client s3=S3Client.builder()
                .region(Region.AP_NORTHEAST_1)
                .credentialsProvider(ProfileCredentialsProvider.create())
                .build();

        try{
            ListBucketsRequest req=ListBucketsRequest.builder().build();
            ListBucketsResponse b=s3.listBuckets(req);

            for(Bucket bucket:b.buckets()) {
                Member m=new Member();
                m.setName(bucket.name());
                memberRepository.save(m);

            }

        } catch(Exception e) {
            System.err.println("ERR");
        }

    }

}
