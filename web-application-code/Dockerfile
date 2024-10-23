FROM ubuntu:bionic

RUN apt update \
    && apt install -y openjdk-8-jdk \
    && apt install -y maven

COPY ./selenium-custom-library /home/selenium-custom-library
COPY ./apps /home/apps

RUN ls /home \
    && mkdir -p ~/.m2/repository/org/seleniumhq/ \
    && cp -r /home/selenium-custom-library/selenium ~/.m2/repository/org/seleniumhq/ \
    && rm -rf /home/selenium-custom-library

# compile all apps such that the dependencies are downloaded
RUN for app in $(ls /home/apps); do cd /home/apps/$app; mvn clean compile; done

RUN rm -rf /home/apps

WORKDIR /home

