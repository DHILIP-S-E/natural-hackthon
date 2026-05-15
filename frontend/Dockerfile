FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# Vite bakes VITE_* vars at build time — pass them as build args
ARG VITE_API_URL
ARG VITE_GOOGLE_MAPS_KEY
ARG VITE_GOOGLE_CLIENT_ID

ENV VITE_API_URL=$VITE_API_URL
ENV VITE_GOOGLE_MAPS_KEY=$VITE_GOOGLE_MAPS_KEY
ENV VITE_GOOGLE_CLIENT_ID=$VITE_GOOGLE_CLIENT_ID

RUN npm run build

# ── Serve with nginx ──────────────────────────────────────────────────────────
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html

# SPA fallback — all routes serve index.html
RUN printf 'server {\n  listen 80;\n  root /usr/share/nginx/html;\n  index index.html;\n  location / { try_files $uri $uri/ /index.html; }\n}\n' \
    > /etc/nginx/conf.d/default.conf

EXPOSE 80
