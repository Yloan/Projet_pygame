.PHONY: help venv-mac venv-win install run-mac run-win

# Detect the operating system
OS := $(shell uname -s 2>/dev/null || echo Windows_NT)

# macOS / Linux
setup-mac:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

run-mac:
	.venv/bin/python src/main.py

# And Windows
setup-win:
	python -m venv .venv
	.venv\Scripts\pip install -r requirements.txt

run-win:
	.venv\Scripts\python src/main.py
