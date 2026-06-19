FROM node:22-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

EXPOSE 3000

CMD ["npx", "nuxt", "dev", "--host", "0.0.0.0"]
