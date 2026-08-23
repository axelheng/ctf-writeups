FROM python:3.12-alpine

RUN apk add --no-cache socat \
    && adduser -D -H -s /sbin/nologin challenge

WORKDIR /app
RUN mkdir -p ./data \
    && chown challenge:challenge ./data

COPY server.py flag.txt ./

USER challenge
EXPOSE 5000

CMD ["socat", "TCP-LISTEN:5000,reuseaddr,fork", "EXEC:python3 -u /app/server.py,stderr"]
