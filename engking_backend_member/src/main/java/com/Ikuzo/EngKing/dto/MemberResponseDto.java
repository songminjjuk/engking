package com.Ikuzo.EngKing.dto;

import com.Ikuzo.EngKing.constant.Authority;
import com.Ikuzo.EngKing.entity.Member;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDate;

@Getter
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class MemberResponseDto {
    private Long id;
    private String email;
    private String password;  //pwd도 바꾸게 하려면 추가해야함
    private String name;
    private String phone;
    private LocalDate birthday;
    private String intro;
    private String profileImgUrl;

    public static MemberResponseDto getEmail(Member member){

        return com.Ikuzo.EngKing.dto.MemberResponseDto.builder()
                .email(member.getEmail())
                .build();
    }

    public static MemberResponseDto getInfo(Member member,String url) {
        return MemberResponseDto.builder()
                .email(member.getEmail())
                .name(member.getName())
                .phone(member.getPhone())
                .birthday(member.getBirthday())
                .intro(member.getIntro())
                .profileImgUrl(url)
                .build();
    }

    public static MemberResponseDto getUrl(String url){
        return MemberResponseDto.builder()
                .profileImgUrl(url)
                .build();
    }


    public static MemberResponseDto getLogin(Member member) {

        return MemberResponseDto.builder()
                .id(member.getMemberId())
                .email(member.getEmail())
                .build();
    }


}