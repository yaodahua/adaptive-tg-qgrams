#!/bin/bash

compile_instr=false

while [ $# -gt 0 ] ; do
  case $1 in
    -i | --compile-instr) compile_instr="$2" ;;
  esac
  shift
done

classpath=/root/.m2/repository/org/seleniumhq/selenium/selenium-java/3.3.1/selenium-java-3.3.1.jar:/root/.m2/repository/org/seleniumhq/selenium/selenium-chrome-driver/3.3.1/selenium-chrome-driver-3.3.1.jar:/root/.m2/repository/org/seleniumhq/selenium/selenium-edge-driver/3.3.1/selenium-edge-driver-3.3.1.jar:/root/.m2/repository/org/seleniumhq/selenium/selenium-firefox-driver/3.3.1/selenium-firefox-driver-3.3.1.jar:/root/.m2/repository/org/seleniumhq/selenium/selenium-ie-driver/3.3.1/selenium-ie-driver-3.3.1.jar:/root/.m2/repository/org/seleniumhq/selenium/selenium-opera-driver/3.3.1/selenium-opera-driver-3.3.1.jar:/root/.m2/repository/org/seleniumhq/selenium/selenium-safari-driver/3.3.1/selenium-safari-driver-3.3.1.jar:/root/.m2/repository/com/codeborne/phantomjsdriver/1.4.0/phantomjsdriver-1.4.0.jar:/root/.m2/repository/org/seleniumhq/selenium/htmlunit-driver/2.24/htmlunit-driver-2.24.jar:/root/.m2/repository/net/sourceforge/htmlunit/htmlunit/2.24/htmlunit-2.24.jar:/root/.m2/repository/xalan/xalan/2.7.2/xalan-2.7.2.jar:/root/.m2/repository/xalan/serializer/2.7.2/serializer-2.7.2.jar:/root/.m2/repository/org/apache/commons/commons-lang3/3.5/commons-lang3-3.5.jar:/root/.m2/repository/org/apache/httpcomponents/httpmime/4.5.2/httpmime-4.5.2.jar:/root/.m2/repository/commons-codec/commons-codec/1.10/commons-codec-1.10.jar:/root/.m2/repository/net/sourceforge/htmlunit/htmlunit-core-js/2.23/htmlunit-core-js-2.23.jar:/root/.m2/repository/net/sourceforge/htmlunit/neko-htmlunit/2.24/neko-htmlunit-2.24.jar:/root/.m2/repository/xerces/xercesImpl/2.11.0/xercesImpl-2.11.0.jar:/root/.m2/repository/xml-apis/xml-apis/1.4.01/xml-apis-1.4.01.jar:/root/.m2/repository/net/sourceforge/cssparser/cssparser/0.9.21/cssparser-0.9.21.jar:/root/.m2/repository/org/w3c/css/sac/1.3/sac-1.3.jar:/root/.m2/repository/commons-io/commons-io/2.5/commons-io-2.5.jar:/root/.m2/repository/commons-logging/commons-logging/1.2/commons-logging-1.2.jar:/root/.m2/repository/org/eclipse/jetty/websocket/websocket-client/9.2.20.v20161216/websocket-client-9.2.20.v20161216.jar:/root/.m2/repository/org/eclipse/jetty/jetty-util/9.2.20.v20161216/jetty-util-9.2.20.v20161216.jar:/root/.m2/repository/org/eclipse/jetty/jetty-io/9.2.20.v20161216/jetty-io-9.2.20.v20161216.jar:/root/.m2/repository/org/eclipse/jetty/websocket/websocket-common/9.2.20.v20161216/websocket-common-9.2.20.v20161216.jar:/root/.m2/repository/org/eclipse/jetty/websocket/websocket-api/9.2.20.v20161216/websocket-api-9.2.20.v20161216.jar:/root/.m2/repository/org/seleniumhq/selenium/selenium-support/3.3.1/selenium-support-3.3.1.jar:/root/.m2/repository/org/seleniumhq/selenium/selenium-remote-driver/3.3.1/selenium-remote-driver-3.3.1.jar:/root/.m2/repository/org/seleniumhq/selenium/selenium-api/3.3.1/selenium-api-3.3.1.jar:/root/.m2/repository/cglib/cglib-nodep/3.2.4/cglib-nodep-3.2.4.jar:/root/.m2/repository/org/apache/commons/commons-exec/1.3/commons-exec-1.3.jar:/root/.m2/repository/com/google/code/gson/gson/2.8.0/gson-2.8.0.jar:/root/.m2/repository/com/google/guava/guava/21.0/guava-21.0.jar:/root/.m2/repository/org/apache/httpcomponents/httpclient/4.5.2/httpclient-4.5.2.jar:/root/.m2/repository/org/apache/httpcomponents/httpcore/4.4.4/httpcore-4.4.4.jar:/root/.m2/repository/net/java/dev/jna/jna-platform/4.1.0/jna-platform-4.1.0.jar:/root/.m2/repository/net/java/dev/jna/jna/4.1.0/jna-4.1.0.jar:/root/.m2/repository/org/hamcrest/hamcrest-library/1.3/hamcrest-library-1.3.jar:/root/.m2/repository/org/hamcrest/hamcrest-core/1.3/hamcrest-core-1.3.jar:/root/.m2/repository/junit/junit/4.12/junit-4.12.jar:/root/.m2/repository/mysql/mysql-connector-java/6.0.5/mysql-connector-java-6.0.5.jar
project_cp=target/classes

if [ "$compile_instr" = true ] ; then
  javac -cp $classpath:$project_cp -d $project_cp src/main/java/main/ClassUnderTestInstr.java
fi

javac -cp $classpath:$project_cp -d $project_cp src/main/java/main/Main.java

java -Xms4096m -Xmx4096m -cp $classpath:$project_cp main.Main

