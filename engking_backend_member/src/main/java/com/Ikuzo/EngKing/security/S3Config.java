package com.Ikuzo.EngKing.security;


import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import software.amazon.awssdk.services.s3.S3Client;
/*
//자격증명 검증
@Configuration
public class S3Config {
    @Value("${cloud.aws.credentials.accessKey}")
    private String awsAccessKey;

    @Value("${cloud.aws.credentials.secretKey}")
    private String awsSecretKey;

    @Value("${cloud.aws.region.static}")
    private String region;


/*
    @Bean
    public AmazonS3 s3Client(){
        final BasicAWSCredentials awsCredentials=new BasicAWSCredentials(awsAccessKey,awsSecretKey);
        return AmazonS3Client
                .standard()
                .withRegion(Regions.fromName(region))
                .withCredentials(new AWSStaticCredentialsProvider(awsCredentials))
                .build();

    }
}

*/













