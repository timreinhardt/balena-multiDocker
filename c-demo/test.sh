#!/bin/sh

BASE_URL="http://localhost:8080"

echo "Testing C API"

echo "GET /status"
curl -s "$BASE_URL/status"
echo

echo "POST /toggle"
curl -s -X POST "$BASE_URL/toggle"
echo

echo "POST /count"
curl -s -X POST "$BASE_URL/count"
echo

echo "POST /reset"
curl -s -X POST "$BASE_URL/reset"
echo

echo "Done"
