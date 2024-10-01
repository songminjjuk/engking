# 빌드 단계
FROM gradle:7.6.0-jdk17 AS build
WORKDIR /app
COPY --chown=gradle:gradle . /app
RUN gradle clean bootJar --no-daemon

# 실행 단계
FROM openjdk:17-jdk-alpine
WORKDIR /app

# 타임존 설정
ENV TZ=Asia/Seoul
RUN apk add --no-cache tzdata && \
    cp /usr/share/zoneinfo/Asia/Seoul /etc/localtime && \
    echo "Asia/Seoul" > /etc/timezone

COPY --from=build /app/build/libs/*.jar app.jar

# 애플리케이션에서 사용하는 포트
EXPOSE 8080

# JVM 시간대 설정
ENTRYPOINT ["java", "-Duser.timezone=Asia/Seoul", "-jar", "app.jar"]
