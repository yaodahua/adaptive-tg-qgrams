#!/bin/bash
# 保存为 download_all_apps.sh

#chmod +x download_all_apps.sh
# ./download_all_apps.sh

cd /home/wlsju/adaptive-tg-qgrams/web-application-code

# 定义所有应用镜像
APPS=(
    "dockercontainervm/dimeshift:latest"
    "dockercontainervm/pagekit:latest"
    "dockercontainervm/petclinic:latest"
    "dockercontainervm/phoenix-trello:latest"
    "dockercontainervm/retroboard:latest"
    "dockercontainervm/splittypie:latest"
    "selenium/standalone-chrome:3.141.59-dubnium"
)

echo "开始下载所有Web应用容器镜像..."

for app in "${APPS[@]}"; do
    echo "正在下载: $app"
    docker pull $app
    if [ $? -eq 0 ]; then
        echo "✓ $app 下载成功"
    else
        echo "✗ $app 下载失败"
    fi
done

echo "所有镜像下载完成！"
echo "已下载的镜像列表："
docker images 