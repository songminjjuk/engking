package com.Ikuzo.EngKing.controller;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@Slf4j
@RestController
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
@RequestMapping("/status")
public class HealthController {

    @GetMapping("")
    public ResponseEntity<Void> healthCheck() {
       try {
           return ResponseEntity.ok().build();  // 200 응답 코드 반환

       } catch (Exception e) {
           log.error("Error occurred during health check: {}", e.getMessage());
           return ResponseEntity.status(500).build();
       }
    }
}
