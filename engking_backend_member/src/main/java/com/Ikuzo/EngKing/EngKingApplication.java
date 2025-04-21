package com.Ikuzo.EngKing;

import io.swagger.v3.oas.annotations.OpenAPIDefinition;
import io.swagger.v3.oas.annotations.info.Info;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@OpenAPIDefinition(info = @Info(title = "My API", version = "v1", description = "My API Description"))
public class EngKingApplication {

	public static void main(String[] args) {
		SpringApplication.run(EngKingApplication.class, args);
	}

}


