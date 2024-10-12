package com.Ikuzo.EngKing.service;



import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.*;
import software.amazon.awssdk.services.s3.presigner.S3Presigner;
import software.amazon.awssdk.services.s3.presigner.model.GetObjectPresignRequest;
import software.amazon.awssdk.services.s3.presigner.model.PresignedGetObjectRequest;
import software.amazon.awssdk.services.s3.presigner.model.PresignedPutObjectRequest;
import software.amazon.awssdk.services.s3.presigner.model.PutObjectPresignRequest;

import java.time.Duration;
import java.util.Map;


@Service
//presignedUrl 생성
public class S3Service {
    private final S3Client s3Client;
    private final ObjectMapper objectMapper;
    private final Logger logger= LoggerFactory.getLogger(S3Service.class.getName());

    @Autowired
    public S3Service(S3Client s3Client) {
        this.s3Client=s3Client;
        this.objectMapper=new ObjectMapper();
    }


    // Get용 info 회원페이지에서 이미지를 불러올 때 접근할 url 생성 후 보내기
    public String createPresignedGetUrl(String bucketName, String keyName) {
        try(S3Presigner s3Presigner=S3Presigner.create()) {

            GetObjectRequest objectRequest= GetObjectRequest.builder()
                    .bucket(bucketName)
                    .key(keyName)
                    .build();

            GetObjectPresignRequest presignRequest= GetObjectPresignRequest.builder()
                    .signatureDuration(Duration.ofMinutes(60))
                    .getObjectRequest(objectRequest)
                    .build();


            PresignedGetObjectRequest presignedRequest=s3Presigner.presignGetObject(presignRequest);

            logger.info("Successfully created presigned GET URL for bucket: [{}], key: [{}]", bucketName, keyName);
            logger.info("Presigned URL: [{}], HTTP method: [{}]", presignedRequest.url().toString(), presignedRequest.httpRequest().method());

            return presignedRequest.url().toString();
        }
        catch(Exception e) {
            logger.error("Failed to create presigned GET URL for bucket: [{}], key: [{}]. Error message: {}", bucketName, keyName, e.getMessage(), e);
            return "failed";
        }
    }
    //update 시 접근할 url 생성하기

    public String createPresignedPutUrl(String bucketName, String keyName, Map<String, String> metadata){
        try (S3Presigner s3Presigner=S3Presigner.create()){

            PutObjectRequest objectRequest= PutObjectRequest.builder()
                    .bucket(bucketName)
                    .key(keyName)
                    .contentType("image/jpg")
                    //.metadata(metadata)
                    .build();

            PutObjectPresignRequest presignRequest = PutObjectPresignRequest.builder()
                    .signatureDuration(Duration.ofMinutes(60))
                    .putObjectRequest(objectRequest)
                    .build();



            PresignedPutObjectRequest presignedRequest=s3Presigner.presignPutObject(presignRequest);

            String URL=presignedRequest.url().toString();
            /*
            logger.info("content-type IS ||||||||||||||||||||||||||||||||||||||||||||: [{}]", objectRequest.contentType());
            logger.info("HTTP method: [{}]", presignedRequest.httpRequest().method());*/

            logger.info("Successfully created presigned PUT URL for bucket: [{}], key: [{}]", bucketName, keyName);
            logger.info("Presigned URL: [{}], HTTP method: [{}]", presignedRequest.url().toString(), presignedRequest.httpRequest().method());

            return presignedRequest.url().toString();
        }

        catch(Exception e) {
            e.printStackTrace();
            return "failed ";
        }


    }

}
















