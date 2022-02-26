FROM node:latest

WORKDIR /workdir/
ADD ./dashboard/ ./
RUN npm install
RUN npm run build
RUN chmod +x entrypoint.sh
ADD ./configs/ /configs/
ENTRYPOINT ./entrypoint.sh
