serve:
	@mdbook serve

build:
	@mdbook build 2>&1 | grep -v "search index is very large" || true

clean:
	rm -fr book

github:
	@ghp-import book -p -n
