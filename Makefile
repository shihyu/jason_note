serve:
	@mdbook serve

build:
	@mdbook build

clean:
	rm -fr book

github:
	@ghp-import book -p -n
