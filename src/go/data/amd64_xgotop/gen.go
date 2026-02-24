package main

//go:generate sh -c "case \"$(go env GOARCH)\" in amd64) exec go run github.com/cilium/ebpf/cmd/bpf2go -type go_runtime_event_t -target amd64 -output-dir cmd/xgotop ebpf xgotop.bpf.c ;; arm64) exec go run github.com/cilium/ebpf/cmd/bpf2go -type go_runtime_event_t -target arm64 -output-dir cmd/xgotop ebpf xgotop.bpf.c ;; *) echo unsupported GOARCH=$(go env GOARCH) >&2; exit 1 ;; esac"
