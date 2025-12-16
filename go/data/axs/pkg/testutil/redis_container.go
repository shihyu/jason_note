package testutil

import (
	"context"
	"fmt"
	"strconv"

	"github.com/ory/dockertest/v3"
	"github.com/ory/dockertest/v3/docker"
	"github.com/redis/go-redis/v9"
)

var (
	RedisContainer ContainerType = "redis"
)

const (
	redisPort    = 6379
	redisPortStr = "6379/tcp"
)

type RedisContainerOptions struct {
	Name      string
	Host      string
	Port      string
	Password  string
	ImageRepo string
	ImageTag  string
}

type RedisContainerResult struct {
	Name     string
	Host     string
	Port     string
	Password string
}

// BuildRedisContainer builds and starts a Redis container based on the provided options.
func BuildRedisContainer(builder *ContainerBuilder, options RedisContainerOptions) (RedisContainerResult, error) {
	imageRepo := options.ImageRepo
	if imageRepo == "" {
		imageRepo = "redis"
	}
	imageTag := options.ImageTag
	if imageTag == "" {
		imageTag = "7-alpine"
	}
	runOptions := dockertest.RunOptions{
		Name:       options.Name,
		Repository: imageRepo,
		Tag:        imageTag,
		Env:        []string{},
	}
	if options.Password != "" {
		runOptions.Cmd = []string{"--requirepass " + options.Password}
	}
	if options.Port != "" {
		runOptions.PortBindings = map[docker.Port][]docker.PortBinding{
			docker.Port(redisPortStr): {
				{HostIP: "127.0.0.1", HostPort: options.Port},
			},
		}
	}

	container, err := builder.FindContainer(options.Name)
	if err != nil {
		return RedisContainerResult{}, err
	}
	if container != nil && container.State == containerRunningState {
		publicPort := int64(0)
		host := ""
		for _, bind := range container.Ports {
			if bind.PrivatePort == redisPort {
				host = bind.IP
				publicPort = bind.PublicPort
				break
			}
		}
		if publicPort == 0 {
			return RedisContainerResult{}, fmt.Errorf("failed to find public port for redis container (%s)", options.Name)
		}

		builder.AddContainer(container.ID, ContainerInfo{
			Name: options.Name,
			Type: RedisContainer,
		})
		return RedisContainerResult{
			Name:     options.Name,
			Host:     host,
			Port:     strconv.FormatInt(publicPort, 10),
			Password: options.Password,
		}, nil
	}
	resource, err := builder.RunWithOptions(&runOptions)
	if err != nil {
		return RedisContainerResult{}, err
	}
	builder.AddContainer(resource.Container.ID, ContainerInfo{
		Name: options.Name,
		Type: RedisContainer,
	})
	host := resource.GetBoundIP(redisPortStr)
	port := resource.GetPort(redisPortStr)

	err = builder.Retry(func() error {
		opt := redis.Options{
			Addr:     fmt.Sprintf("%s:%s", host, port),
			Password: options.Password,
		}
		client := redis.NewClient(&opt)
		defer client.Close()
		_, err := client.Ping(context.Background()).Result()
		return err
	})
	if err != nil {
		return RedisContainerResult{}, err
	}

	return RedisContainerResult{
		Name:     options.Name,
		Host:     host,
		Port:     port,
		Password: options.Password,
	}, nil
}
