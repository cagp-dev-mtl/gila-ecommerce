FROM node:22-alpine AS build

WORKDIR /storefront

COPY package.json package-lock.json ./
RUN npm ci

COPY index.html vite.config.js ./
COPY src ./src
COPY public ./public
RUN npm run build

FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /storefront/dist /usr/share/nginx/html

EXPOSE 80
