FROM node:20-alpine
WORKDIR /app
COPY package.json .
RUN npm install
COPY enforcePolicyMiddleware.js .
COPY server.js .
ENTRYPOINT ["node", "server.js"]
