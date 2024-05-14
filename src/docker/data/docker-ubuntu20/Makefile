# 定義映像檔名稱和版本
IMAGE_NAME = ubuntu-20.04
IMAGE_VERSION = latest

# 定義主機端資料夾路徑
HOST_DATA_DIR = data

# 建立映像檔
build:
	docker build -t $(IMAGE_NAME):$(IMAGE_VERSION) .

# 執行容器並映射資料卷
run:
	docker run -it -v $(HOST_DATA_DIR):/usr/src/app $(IMAGE_NAME):$(IMAGE_VERSION) /bin/bash

# 推送映像檔到 Docker 註冊畫面庫
push:
	docker push $(IMAGE_NAME):$(IMAGE_VERSION)

# 清除本機映像檔
clean:
	docker rmi $(IMAGE_NAME):$(IMAGE_VERSION)
