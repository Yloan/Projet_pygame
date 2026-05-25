.PHONY: help venv-mac venv-win install run-mac run-win

# Detect the operating system
OS := $(shell uname -s 2>/dev/null || echo Windows_NT)

# macOS / Linux
setup-mac:
	echo ".venv creation & installing dependencies..."
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

run-mac:
	echo "execution..."
	.venv/bin/python src/main.py

# And Windows
setup-win:
	echo ".venv creation & installing dependencies..."
	python -m venv .venv
	.venv\Scripts\pip install -r requirements.txt

run-win:
	echo "execution..."
	.venv\Scripts\python src/main.py
