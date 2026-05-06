#!/bin/bash

poetry run isort --profile black src tests
poetry run black src tests

# npx markdownlint-cli2 "**/*.md" "#node_modules" "#.venv"
