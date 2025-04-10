#!/bin/bash

# Runs the CLI container interactively so input() works correctly
docker compose run --rm --service-ports cli
