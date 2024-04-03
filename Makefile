# Makefile for Django Messaging App

.PHONY: help build up build-up down

help:
	@echo "Available commands:"
	@echo "  make build      - Build the Docker image"
	@echo "  make up         - Start the Docker containers"
	@echo "  make build-up   - Build the Docker image and start containers"
	@echo "  make down       - Stop and remove Docker containers"

build:
	docker-compose build

up:
	docker-compose up

build-up: build up

down:
	docker-compose down