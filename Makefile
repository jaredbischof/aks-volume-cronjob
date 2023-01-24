BINARY_NAME=kubernetes-file-backup

build:
	GOARCH=amd64 GOOS=darwin go build -o ${BINARY_NAME}-darwin cmd/main.go
	GOARCH=amd64 GOOS=linux go build -o ${BINARY_NAME}-linux cmd/main.go

run:
	./${BINARY_NAME}-linux

build_and_run: build run

clean:
	go clean
	rm ${BINARY_NAME}-darwin
	rm ${BINARY_NAME}-linux

test:
	go test ./...

test_coverage:
	go test ./... -coverprofile=coverage.out

dep:
	go mod download

vet:
	go vet
