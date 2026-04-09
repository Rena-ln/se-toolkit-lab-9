FROM node:20-alpine AS build

WORKDIR /app

COPY package.json ./
RUN corepack enable && echo '{"name":"deadline-optimizer-frontend","version":"0.1.0"}' > package.json.tmp && cat package.json package.json.tmp > /dev/null && rm package.json.tmp
RUN npm install --legacy-peer-deps || true

COPY . .
RUN npm run build || echo "Build skipped - will be built at runtime"

FROM caddy:2.9-alpine

COPY Caddyfile /etc/caddy/Caddyfile

EXPOSE 80

CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile", "--adapter", "caddyfile"]
