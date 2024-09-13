# build stage
FROM gradle:7.6.0-jdk17 AS build
WORKDIR /app
COPY --chown=gradle:gradle ./app
RUN gradle clean bootJar --no-daemon

# execution stage
FROM openjdk:17-jdk-alpine
WORKDIR /app
COPY --from=build /app/build/libs/*.jar app.jar

EXPOSE 8888

ENTRYPOINT ["java","-jar","/app.jar"]
