package com.Ikuzo.EngKing.dto;


import com.Ikuzo.EngKing.constant.Authority;
import com.Ikuzo.EngKing.constant.Existence;
import com.Ikuzo.EngKing.entity.Member;
import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.*;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
@Builder
@JsonInclude(JsonInclude.Include.NON_NULL) //null인 필드는 json에서 제외
public class MemberRequestDto {
    private Long id;
    private String email;
    private String password;
    private String name;
    private String phone;
    private LocalDate birthday;
    private String intro;
    private Authority authority;
    //private String profileImgUrl;  // 없어도 될수도??
    //register, update request 할 때 넘기는 Dto

    public Member toMember(PasswordEncoder passwordEncoder) {
        return Member.builder()
                .email(email)
                .password(passwordEncoder.encode(password)) // 암호화된 값으로 DB에 저장됨
                .name(name)
                .phone(phone)
                .birthday(birthday)
                .signUpTime(LocalDateTime.now()) // 오늘 날짜 입력(2023-01-01 같은 형식)
                .existence(Existence.YES) // 자동으로 존재 회원
                .authority(authority) // 회원 종류
                .intro(intro)
                .build();
    }
    // 로그인시 넘겨받은 아이디와 비밀번호 조합으로 토큰 생성 준비
    public UsernamePasswordAuthenticationToken toAuthentication() {
        return new UsernamePasswordAuthenticationToken(email, password);
    }

    public void setImgUrl(){

    }




}
