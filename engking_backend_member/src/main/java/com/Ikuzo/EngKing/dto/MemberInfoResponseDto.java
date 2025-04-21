package com.Ikuzo.EngKing.dto;

import com.Ikuzo.EngKing.constant.Authority;
import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDate;

@Getter
@AllArgsConstructor
@NoArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL) //null인 필드는 json에서 제외
public class MemberInfoResponseDto {
    private String email;
    private String name;
    private String phone;
    private LocalDate birthday;
    private String intro;
    private Authority authority;

}
