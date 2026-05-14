FROM balenalib/raspberrypi4-64-node:20

WORKDIR /usr/src/app

COPY package.json .
RUN npm install

COPY server.js .
COPY services.json .

CMD ["npm", "start"]
