package com.Ikuzo.EngKing.controller;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@Slf4j
@RestController
@RequiredArgsConstructor
@RequestMapping("/health")
public class HealthController {

    @GetMapping("")
    public ResponseEntity<Void> healthCheck(){
        return ResponseEntity.ok().build();
    }
}
