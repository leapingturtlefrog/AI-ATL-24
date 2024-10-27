terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.1"
    }
  }
}

provider "docker" {}

resource "docker_image" "app_image" {
  name = "test:latest"
  build {
    context    = "./"
    dockerfile = "Dockerfile"
  }
}

resource "docker_container" "app_container" {
  name  = "container_a"
  image = docker_image.app_image.name

  ports {
    internal = 8501
    external = 8501
  }

  ports {
    internal = 8502
    external = 8502
  }

  restart = "unless-stopped"
}

