# Caduceus 前端 Dockerfile
FROM node:20-alpine

LABEL maintainer="Caduceus Team"
LABEL description="Caduceus Vue Frontend Service"

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY package.json ./

# 安装依赖
RUN npm install

# 复制项目文件
COPY . .

# 构建生产版本
RUN npm run build

# 输出构建产物到 dist 目录
# 生产环境使用 Nginx 服务静态文件，此镜像仅用于构建
CMD ["npm", "run", "preview"]