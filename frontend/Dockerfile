# Stage 1: Build static assets bằng Node.js
FROM node:20-alpine AS build

WORKDIR /app

# Copy dependencies manifest và cài đặt
COPY package*.json ./
RUN npm install

# Copy toàn bộ mã nguồn frontend
COPY . .

# Hỗ trợ nhận build arguments cho API
ARG VITE_API_URL=""
ARG VITE_API_PREFIX="/api/v1"
ENV VITE_API_URL=$VITE_API_URL \
    VITE_API_PREFIX=$VITE_API_PREFIX

# Build production bundle vào thư mục /dist
RUN npm run build

# Stage 2: Serve static files bằng Nginx Alpine siêu nhẹ
FROM nginx:alpine

# Copy production bundle từ Stage 1
COPY --from=build /app/dist /usr/share/nginx/html

# Cấu hình Nginx reverse proxy và SPA fallback
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Cổng mặc định
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
