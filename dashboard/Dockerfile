FROM node:latest

WORKDIR /workdir/
ADD ./dashboard/ ./
RUN npm install
RUN npm run build
RUN chmod +x entrypoint.sh
ENTRYPOINT ./entrypoint.sh
