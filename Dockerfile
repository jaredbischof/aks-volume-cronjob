FROM golang:1.19.4-alpine3.17 as builder

USER root
RUN apk update && apk add g++ make
WORKDIR /go/src/github.com/jaredbischof/kubernetes-file-backup
ADD Makefile .
ADD go.sum .
ADD go.mod .
RUN go mod download
COPY . .
RUN make build

FROM golang:1.19.4-alpine3.17
ARG COMMIT
LABEL commit=${COMMIT}
ENV COMMIT_SHA=${COMMIT}
USER guest
COPY --from=builder /go/src/github.com/jaredbischof/kubernetes-file-backup/kubernetes-file-backup-linux /go/src/github.com/jaredbischof/kubernetes-file-backup/kubernetes-file-backup-linux
ENTRYPOINT ["/bin/sh", "-c", "/go/src/github.com/jaredbischof/kubernetes-file-backup/kubernetes-file-backup-linux"]
