# Docker 安裝 Centos 7

```sh
docker search centos
docker pull centos:7.5.1804
docker run -itd --privileged=true -p 20010:22 --name="centos" centos:7.5.1804  /usr/sbin/init
docker exec -it centos bash
cat /etc/redhat-release
```



```sh
yum install java-1.8.0-openjdk  vim
java -version
```

- vim /etc/yum.repos.d/cassandra.repo

```sh
[cassandra]
name=Apache Cassandra
baseurl=https://www.apache.org/dist/cassandra/redhat/311x/
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://www.apache.org/dist/cassandra/KEYS
```



```sh
yum update
yum install cassandra
systemctl enable cassandra &&  systemctl restart cassandra

查看
systemctl status cassandra
nodetool status
```

- 刪除 cassandra

```
sudo rm -r /var/lib/cassandra
sudo rm -r /var/log/cassandra
sudo yum remove "cassandra-*"
```

