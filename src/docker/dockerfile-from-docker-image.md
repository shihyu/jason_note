# 由 Docker image 反推其 Dockerfile

當我們使用現成的 Docker image 進行開發時，有時候會想知道這個 image 的內容是什麼，他提供的功能是如何達成的，這個時候如果能找到作者提供的 Dockerfile 是最好，但如果對方沒有公開的話，就有點麻煩了，這時候我們可以使用內建的 `docker history` 指令根據每層 image layer 的 metadata 看出做的事情，此外也有大大做了現成的工具讓我們可以直接產出接近原本 Dockerfile 該有的內容。

這邊我拿了兩個工具來做實驗:

```shell
1. https://github.com/CenturyLinkLabs/dockerfile-from-image
2. https://github.com/lukapeschke/dockerfile-from-image
```

其中只有第二個是可行的，以下是實驗過程。

## centurylink/dockerfile-from-image[Permalink](https://sdhuang32.github.io/zh-tw/dockerfile-from-docker-image/#centurylinkdockerfile-from-image)

首先這個工具是參考[這篇](https://philipzheng.gitbooks.io/docker_practice/content/dockerfile/file_from_image.html)而看到的。 我先拿 ruby 嘗試一下:

```shell
$ docker pull centurylink/dockerfile-from-image
$ docker pull ruby
$ docker image | grep ruby
REPOSITORY                                    TAG                 IMAGE ID            CREATED              SIZE
docker.io/ruby                                latest              d529acb9f124        4 weeks ago          840 MB
$ docker run -v /var/run/docker.sock:/var/run/docker.sock centurylink/dockerfile-from-image d529acb9f124
/usr/lib/ruby/gems/2.2.0/gems/docker-api-1.24.1/lib/docker/connection.rb:42:in `rescue in request': 400 Bad Request: malformed Host header (Docker::Error::ClientError)
        from /usr/lib/ruby/gems/2.2.0/gems/docker-api-1.24.1/lib/docker/connection.rb:38:in `request'
        from /usr/lib/ruby/gems/2.2.0/gems/docker-api-1.24.1/lib/docker/connection.rb:65:in `block (2 levels) in <class:Connection>'
        from /usr/lib/ruby/gems/2.2.0/gems/docker-api-1.24.1/lib/docker/image.rb:172:in `all'
        from /usr/src/app/dockerfile-from-image.rb:32:in `<main>'
```

發現也有其他人碰到相同問題，參考[這邊](https://github.com/CenturyLinkLabs/dockerfile-from-image/issues/14#issuecomment-272294267)的說明，利用他給的 Dockerfile 重新 build image 之後，反倒無法輸出任何東西。這個 repository 最近一次更新也是 2015 的事了，該工具似已不再適用新版的 Docker。

## lukapeschke/dockerfile-from-image[Permalink](https://sdhuang32.github.io/zh-tw/dockerfile-from-docker-image/#lukapeschkedockerfile-from-image)

參考上面同的討論串後續的內容找到第二個 repository，用他的 Dockerfile 來 build image:

```shell
$ git clone https://github.com/lukapeschke/dockerfile-from-image.git
$ cd dockerfile-from-image/
$ docker build --rm -t lukapeschke/dockerfile-from-image .
```

他的使用方法 (只能用 image ID，不能用 image name!):

```shell
$ docker run --rm -v '/var/run/docker.sock:/var/run/docker.sock' lukapeschke/dockerfile-from-image <IMAGE_ID>
```

以下拿 ruby 測試可以順利產生我們要的:

```dockerfile
$ docker run --rm -v '/var/run/docker.sock:/var/run/docker.sock' lukapeschke/dockerfile-from-image d529acb9f124
FROM docker.io/ruby:latest
ADD file:2cddee716e84c40540a69c48051bd2dcf6cd3bd02a3e399334e97f20a77126ff in /
CMD ["bash"]
RUN /bin/sh -c apt-get update \
    && apt-get install -y --no-install-recommends 		ca-certificates 		curl 		netbase 		wget 	\
    && rm -rf /var/lib/apt/lists/*
RUN /bin/sh -c set -ex; 	if ! command -v gpg > /dev/null; then 		apt-get update; 		apt-get install -y --no-install-recommends 			gnupg 			dirmngr 		; 		rm -rf /var/lib/apt/lists/*; 	fi
RUN /bin/sh -c apt-get update \
    && apt-get install -y --no-install-recommends 		git 		mercurial 		openssh-client 		subversion 	procps 	\
    && rm -rf /var/lib/apt/lists/*
RUN /bin/sh -c set -ex; 	apt-get update; 	apt-get install -y --no-install-recommends 		autoconf 		automake 		bzip2 		dpkg-dev 		file 		g++ 		gcc 		imagemagick 		libbz2-dev 	libc6-dev 		libcurl4-openssl-dev 		libdb-dev 		libevent-dev 		libffi-dev 		libgdbm-dev 	libgeoip-dev 		libglib2.0-dev 		libgmp-dev 		libjpeg-dev 		libkrb5-dev 		liblzma-dev 		libmagickcore-dev 		libmagickwand-dev 		libncurses5-dev 		libncursesw5-dev 		libpng-dev 	libpq-dev 		libreadline-dev 		libsqlite3-dev 		libssl-dev 		libtool 		libwebp-dev 	libxml2-dev 		libxslt-dev 		libyaml-dev 		make 		patch 		unzip 		xz-utils 		zlib1g-dev 				$( 			if apt-cache show 'default-libmysqlclient-dev' 2>/dev/null | grep -q '^Version:'; then 				echo 'default-libmysqlclient-dev'; 			else 				echo 'libmysqlclient-dev'; 			fi 		) 	; 	rm -rf /var/lib/apt/lists/*
RUN /bin/sh -c set -eux; 	mkdir -p /usr/local/etc; 	{ 		echo 'install: --no-document'; 		echo 'update: --no-document'; 	} >> /usr/local/etc/gemrc
ENV RUBY_MAJOR=2.6
ENV RUBY_VERSION=2.6.3
ENV RUBY_DOWNLOAD_SHA256=11a83f85c03d3f0fc9b8a9b6cad1b2674f26c5aaa43ba858d4b0fcc2b54171e1
RUN /bin/sh -c set -eux; 		savedAptMark="$(apt-mark showmanual)"; 	apt-get update; 	apt-get install -y --no-install-recommends 		bison 		dpkg-dev 		libgdbm-dev 		ruby 	; 	rm -rf /var/lib/apt/lists/*; 		wget -O ruby.tar.xz "https://cache.ruby-lang.org/pub/ruby/${RUBY_MAJOR%-rc}/ruby-$RUBY_VERSION.tar.xz"; 	echo "$RUBY_DOWNLOAD_SHA256 *ruby.tar.xz" | sha256sum --check --strict; 		mkdir -p /usr/src/ruby; 	tar -xJf ruby.tar.xz -C /usr/src/ruby --strip-components=1; 	rm ruby.tar.xz; 		cd /usr/src/ruby; 		{ 		echo '#define ENABLE_PATH_CHECK 0'; 		echo; 		cat file.c; 	} > file.c.new; 	mv file.c.new file.c; 		autoconf; 	gnuArch="$(dpkg-architecture --query DEB_BUILD_GNU_TYPE)"; 	./configure 		--build="$gnuArch" 		--disable-install-doc 		--enable-shared 	; 	make -j "$(nproc)"; 	make install; 		apt-mark auto '.*' > /dev/null; 	apt-mark manual $savedAptMark > /dev/null; 	find /usr/local -type f -executable -not \( -name '*tkinter*' \) -exec ldd '{}' ';' 		| awk '/=>/ { print $(NF-1) }' 		| sort -u 		| xargs -r dpkg-query --search 		| cut -d: -f1 		| sort -u 		| xargs -r apt-mark manual 	; 	apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false; 		cd /; 	rm -r /usr/src/ruby; 	! dpkg -l | grep -i ruby; 	[ "$(command -v ruby)" = '/usr/local/bin/ruby' ]; 	ruby --version; 	gem --version; 	bundle --version
ENV GEM_HOME=/usr/local/bundle
ENV BUNDLE_PATH=/usr/local/bundle BUNDLE_SILENCE_ROOT_WARNING=1 BUNDLE_APP_CONFIG=/usr/local/bundle
ENV PATH=/usr/local/bundle/bin:/usr/local/bundle/gems/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
RUN /bin/sh -c mkdir -p "$GEM_HOME" \
    && chmod 777 "$GEM_HOME"
CMD ["irb"]
```

不過可惜的是像這樣的工具終究無法還原出真實 Dockerfile 中 COPY 或 ADD 的時候加入到 image 中的檔案。 例如以下是用該工具還原他自己:

```shell
$ docker images | grep "lukapeschke/dockerfile-from-image"
lukapeschke/dockerfile-from-image             latest              d719f8dcb798        37 minutes ago      59 MB

$ docker run -v /var/run/docker.sock:/var/run/docker.sock lukapeschke/dockerfile-from-image d719f8dcb798
FROM docker.io/alpine:latest
RUN /bin/sh -c apk add --update python3 wget      \
    && wget -O - --no-check-certificate https://bootstrap.pypa.io/get-pip.py | python3      \
    && apk del wget      \
    && pip3 install -U docker-py      \
    && yes | pip3 uninstall pip
COPY file:d7369c0379dc34ec79c308a782b14eab9c86ed1ebc41b5ce859e32760518fb21 in /root
ENTRYPOINT ["/root/entrypoint.py"]
```

可以看到 COPY 的部分只能知道有檔案被複製到指定目錄而已。