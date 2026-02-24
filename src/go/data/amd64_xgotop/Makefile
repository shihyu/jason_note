all: proto gen compile run
.PHONY: all

install-protoc:
	@if [ "$$(uname)" = "Darwin" ]; then \
		brew install protobuf || echo "Failed to install protobuf using Homebrew."; \
	elif [ "$$(uname)" = "Linux" ]; then \
		sudo apt-get install -y protobuf-compiler || echo "Failed to install protobuf using apt-get."; \
	fi
	go install google.golang.org/protobuf/cmd/protoc-gen-go@latest

vmlinux:
	bpftool btf dump file /sys/kernel/btf/vmlinux format c > vmlinux.h

proto:
	protoc --go_out=. --go_opt=paths=source_relative cmd/xgotop/storage/event.proto

gen: proto vmlinux
	go generate

compile: gen
	go build -o testserver ./cmd/testserver
	go build -o goroutinepadding ./cmd/goroutinepadding
	go build -o xgotop ./cmd/xgotop

samplingtest: compile
	./scripts/test_sampling.sh

weboverheadtest: compile
	./scripts/test_web_overhead.sh -r "1 2 4 8 16 32 64 128" -p "1" --storage "jsonl protobuf" --flood -n 50000

buffertest: compile
	./scripts/test_web_overhead.sh -r "1" -p "1" --storage "jsonl protobuf" --only-web --batch-sizes "500 1000 2000 4000 8000 16000 32000 64000" --flood -n 50000

run: compile
	sudo ./xgotop -b ./testserver -rw 8 -pw 1 -batch-size 32000 -sample "casgstatus:0.1"

run-silent: compile
	sudo ./xgotop -b ./testserver -rw 8 -pw 1 -batch-size 32000 -sample "casgstatus:0.1" -s

web-install:
	cd web && npm install

web-dev: web-install
	cd web && npm run dev

web-build: web-install
	cd web && npm run build

run-web: compile
	sudo ./xgotop -b ./testserver -rw 8 -pw 1 -batch-size 100 -web -web-port 8080 -storage-format protobuf -storage-dir ./sessions

testserver: compile
	./testserver

testserver-client:
	while true; do curl http://localhost/books/test-book/page/100 > /dev/null 2>&1; done

testserver-client-slow:
	while true; do curl http://localhost/books/test-book/page/100 > /dev/null 2>&1; sleep 1; done

testserver-client-fast:
	while true; do curl http://localhost/books/test-book/page/100 > /dev/null 2>&1 & done

clean:
	- rm ebpf_arm64*.go
	- rm ebpf_arm64*.o
	- rm testserver
	- rm goroutinepadding
	- rm xgotop
	- rm -rf web/dist
	- rm -rf sessions
	- rm cmd/xgotop/storage/event.pb.go
