# TimeFlow CLI Makefile
# 构建和开发辅助命令

.PHONY: help install dev test clean build upload lint format

help:
	@echo "TimeFlow CLI - 可用命令 | Available commands:"
	@echo ""
	@echo "  make install    - 安装依赖 | Install dependencies"
	@echo "  make dev        - 开发模式安装 | Install in dev mode"
	@echo "  make test       - 运行测试 | Run tests"
	@echo "  make lint       - 代码检查 | Lint code"
	@echo "  make format     - 格式化代码 | Format code"
	@echo "  make clean      - 清理构建文件 | Clean build files"
	@echo "  make build      - 构建分发包 | Build distribution"
	@echo "  make upload     - 上传到 PyPI | Upload to PyPI"
	@echo ""

install:
	pip install -r requirements.txt

dev:
	pip install -e .

test:
	python -m pytest tests/ -v

lint:
	flake8 timeflow/ --max-line-length=100
	pylint timeflow/ --disable=C,R

format:
	black timeflow/ --line-length=100
	isort timeflow/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf __pycache__/
	rm -rf timeflow/__pycache__/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

build: clean
	python setup.py sdist bdist_wheel

upload: build
	twine upload dist/*

# 快捷命令
run:
	python -m timeflow.cli

db-init:
	python -c "from timeflow.database import Database; db = Database(); print('Database initialized')"
