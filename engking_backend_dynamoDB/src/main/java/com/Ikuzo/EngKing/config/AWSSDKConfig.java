package com.Ikuzo.EngKing.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import software.amazon.awssdk.auth.credentials.AwsCredentialsProvider;
import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.s3.S3Client;

@Configuration
public class AWSSDKConfig {

    // 공통 AWS 설정: 리전 및 자격 증명 공급자
    private final Region region = Region.AP_NORTHEAST_1;  // 원하는 리전 설정
    private final AwsCredentialsProvider credentialsProvider = DefaultCredentialsProvider.create();

    @Bean
    public DynamoDbClient dynamoDbClient() {
        return DynamoDbClient.builder()
                .region(region)
                .credentialsProvider(credentialsProvider)
                .build();
    }

    @Bean
    public S3Client s3Client() {
        return S3Client.builder()
                .region(region)
                .credentialsProvider(credentialsProvider)
                .build();
    }

}
