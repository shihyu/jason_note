FROM golang:1.24-alpine3.22 AS builder

RUN apk update && \
    apk upgrade && \
    apk add --no-cache openssl alpine-sdk bash git ca-certificates imagemagick-dev openssl gcc build-base && \
    rm -rf /var/cache/apk/*

RUN addgroup --gid 1000 golang && \
    adduser --disabled-password --ingroup golang --uid 1000 golang 


USER root
WORKDIR /home/axs
COPY . /home/axs/
RUN chown -R golang:golang /home/axs
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    go mod tidy
RUN go build -tags musl -o /home/axs/app ./main.go


FROM alpine:3.22 

RUN apk add openssl --no-cache --repository http://dl-3.alpinelinux.org/alpine/edge/main && \
    apk add --no-cache ca-certificates && \
    apk add --no-cache tzdata && \
    apk del openssl && rm -f /var/cache/apk/*

RUN addgroup axs && adduser -DH axs -G axs
WORKDIR /home/axs
RUN chown axs /home/axs
USER axs

COPY ./config/config.example.toml /home/axs/config/config.toml
COPY --from=builder /home/axs/app /home/axs/app

ENTRYPOINT [ "/home/axs/app" ]
CMD [ "/home/axs/app" ]
