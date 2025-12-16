package testutil

import (
	"database/sql"
	"fmt"
	"strconv"

	_ "github.com/jackc/pgx/v5/stdlib"
	"github.com/ory/dockertest/v3"
	"github.com/ory/dockertest/v3/docker"
)

var (
	PostgresContainer ContainerType = "postgres"
)

type PostgresContainerOptions struct {
	Name         string
	Host         string
	Port         string
	Username     string
	Password     string
	DatabaseName string
	ImageRepo    string
	ImageTag     string
}

type PostgresContainerResult struct {
	Name         string
	Host         string
	Port         string
	Username     string
	Password     string
	DatabaseName string
}

const (
	pgPort    = 5432
	pgPortStr = "5432/tcp"
)

func BuildPostgresContainer(builder *ContainerBuilder, options PostgresContainerOptions) (PostgresContainerResult, error) {
	imageRepo := options.ImageRepo
	if imageRepo == "" {
		imageRepo = "postgres"
	}
	imageTag := options.ImageTag
	if imageTag == "" {
		imageTag = "18"
	}

	runOptions := dockertest.RunOptions{
		Name:       options.Name,
		Repository: imageRepo,
		Tag:        imageTag,
		Env: []string{
			"POSTGRES_USER=" + options.Username,
			"POSTGRES_PASSWORD=" + options.Password,
			"POSTGRES_DB=" + options.DatabaseName,
		},
	}
	if options.Port != "" {
		runOptions.PortBindings = map[docker.Port][]docker.PortBinding{
			docker.Port(pgPortStr): {{HostIP: "127.0.0.1", HostPort: options.Port}},
		}
	}

	container, err := builder.FindContainer(options.Name)
	if err != nil {
		return PostgresContainerResult{}, err
	}
	if container != nil && container.State == containerRunningState {
		publicPort := int64(0)
		host := ""
		for _, bind := range container.Ports {
			if bind.PrivatePort == pgPort {
				host = bind.IP
				publicPort = bind.PublicPort
				break
			}
		}
		if publicPort == 0 {
			return PostgresContainerResult{}, fmt.Errorf("failed to find public port for mongo container (%s)", options.Name)
		}

		builder.AddContainer(container.ID, ContainerInfo{
			Name: options.Name,
			Type: PostgresContainer,
		})
		return PostgresContainerResult{
			Name:         options.Name,
			Host:         host,
			Port:         strconv.FormatInt(publicPort, 10),
			Username:     options.Username,
			Password:     options.Password,
			DatabaseName: options.DatabaseName,
		}, nil
	}
	resource, err := builder.RunWithOptions(&runOptions)
	if err != nil {
		return PostgresContainerResult{}, err
	}
	builder.AddContainer(resource.Container.ID, ContainerInfo{
		Name: options.Name,
		Type: PostgresContainer,
	})
	host := resource.GetBoundIP(pgPortStr)
	port := resource.GetPort(pgPortStr)

	err = builder.Retry(func() error {
		dsn := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
			host,
			port,
			options.Username,
			options.Password,
			options.DatabaseName,
		)
		db, err := sql.Open("pgx", dsn)
		if err != nil {
			return err
		}
		defer db.Close()
		return db.Ping()
	})
	if err != nil {
		return PostgresContainerResult{}, err
	}

	return PostgresContainerResult{
		Host:         host,
		Port:         port,
		Username:     options.Username,
		Password:     options.Password,
		DatabaseName: options.DatabaseName,
	}, nil
}
