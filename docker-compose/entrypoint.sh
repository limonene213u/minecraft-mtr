#!/bin/bash

# コンテナのIPアドレスを取得
CONTAINER_IP=$(hostname -i)

# JMXのホストIPを設定
export JVM_OPTS="-Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.port=9090 -Dcom.sun.management.jmxremote.rmi.port=9090 -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.ssl=false -Djava.rmi.server.hostname=${CONTAINER_IP}"

# Minecraftサーバーを起動
exec /start
