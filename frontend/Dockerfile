# Frontend multi-stage: build -> nginx
FROM node:26-alpine AS build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
# Production build
RUN npm run build

FROM nginx:1.27-alpine
# Non-root (nginx official uses 101)
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
# Add simple health file
RUN echo "ok" > /usr/share/nginx/html/healthz
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://localhost/healthz || exit 1