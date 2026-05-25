.PHONY: setup-mac setup-win run-mac run-win build-mac build-win build-launcher-mac build-launcher-win

# macOS / Linux
setup-mac:
	python3 -m venv .venv
	.venv/bin/python3 -m pip install -r requirements.txt

run-mac:
	.venv/bin/python3 src/main.py

build-mac:
	rm -rf .venv_build
	python3 -m venv .venv_build
	.venv_build/bin/python3 -m pip install -r requirements.txt pyinstaller -q
	find assets -name ".DS_Store" -delete
	.venv_build/bin/python3 -m PyInstaller game.spec --distpath dist/mac --workpath build/mac --noconfirm
	.venv_build/bin/python3 -m PyInstaller server.spec --distpath dist/mac --workpath build/mac --noconfirm
	rm -rf .venv_build

build-launcher-mac:
	rm -rf .venv_build
	python3 -m venv .venv_build
	.venv_build/bin/python3 -m pip install pygame colorama pyinstaller -q
	.venv_build/bin/python3 -m PyInstaller launcher.spec --distpath dist/mac --workpath build/mac --noconfirm
	rm -rf .venv_build

# Windows
setup-win:
	python -m venv .venv
	.venv\Scripts\python -m pip install -r requirements.txt

run-win:
	.venv\Scripts\python src/main.py

build-win:
	rmdir /s /q .venv_build 2>nul || true
	python -m venv .venv_build
	.venv_build\Scripts\python -m pip install -r requirements.txt pyinstaller -q
	.venv_build\Scripts\python -m PyInstaller game.spec --distpath dist\win --workpath build\win --noconfirm
	.venv_build\Scripts\python -m PyInstaller server.spec --distpath dist\win --workpath build\win --noconfirm
	rmdir /s /q .venv_build

build-launcher-win:
	rmdir /s /q .venv_build 2>nul || true
	python -m venv .venv_build
	.venv_build\Scripts\python -m pip install pygame colorama pyinstaller -q
	.venv_build\Scripts\python -m PyInstaller launcher.spec --distpath dist\win --workpath build\win --noconfirm
	rmdir /s /q .venv_build
