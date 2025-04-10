#!/bin/bash
set -e

# Optional: Wait for Redis to be ready
echo "Waiting for Redis..."
until nc -z -v -w30 $REDIS_HOST 6379
do
  echo "Waiting for Redis to start..."
  sleep 2
done

echo "Redis is up. Starting CLI..."
exec python chat_cli.py
