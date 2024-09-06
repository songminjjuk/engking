package com.Ikuzo.EngKing.service;



import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.GetObjectRequest;
import software.amazon.awssdk.services.s3.model.PutObjectRequest;
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
    //private final s3 s3;
    private final Logger logger= LoggerFactory.getLogger(S3Service.class.getName());

    // S3 client 생성했으나 어느 클래스에서 해야하는 것인가?
    private final Region region= Region.AP_NORTHEAST_1;
    S3Client s3=S3Client.builder()
            .region(region)
            .build();



    // Get용 info 회원페이지에서 이미지를 불러올 때 접근할 url 생성 후 보내기
    public String createPresignedGetUrl(String bucketName, String keyName) {
        try(S3Presigner presigner = S3Presigner.create()) {

            GetObjectRequest objectRequest= GetObjectRequest.builder()
                    .bucket(bucketName)
                    .key(keyName)
                    .build();

            GetObjectPresignRequest presignRequest= GetObjectPresignRequest.builder()
                    .signatureDuration(Duration.ofMinutes(60))
                    .getObjectRequest(objectRequest)
                    .build();

            PresignedGetObjectRequest presignedRequest=presigner.presignGetObject(presignRequest);
            logger.info("Presigned URL: [{}]", presignedRequest.url().toString());
            logger.info("HTTP method: [{}]", presignedRequest.httpRequest().method());

            return presignedRequest.url().toExternalForm();
        }
    }
    //update 시 접근할 url 생성하기
    public String createPresignedPutUrl(String bucketName, String keyName, Map<String, String> metadata){
        try(S3Presigner presigner=S3Presigner.create()) {

            PutObjectRequest objectRequest= PutObjectRequest.builder()
                    .bucket(bucketName)
                    .key(keyName)
                    .metadata(metadata)
                    .build();

            PutObjectPresignRequest presignRequest = PutObjectPresignRequest.builder()
                    .signatureDuration(Duration.ofMinutes(60))
                    .putObjectRequest(objectRequest)
                    .build();

            PresignedPutObjectRequest presignedRequest=presigner.presignPutObject(presignRequest);

            String URL=presignedRequest.url().toString();
            logger.info("Presigned URL to upload a file to: [{}]", URL);
            logger.info("HTTP method: [{}]", presignedRequest.httpRequest().method());

            return presignedRequest.url().toExternalForm();
//            return URL;
        }

        catch(Exception e) {
            e.printStackTrace();
            return "LALA";
        }


    }

}
















