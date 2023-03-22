# build front-end
FROM node:lts-alpine AS builder

COPY ./ /app
WORKDIR /app

RUN apk add --no-cache git \
    && npm install pnpm -g \
    && pnpm install \
    && pnpm run build \
    && rm -rf /root/.npm /root/.pnpm-store /usr/local/share/.cache /tmp/*

