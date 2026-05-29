#!/usr/bin/env python3
"""
TimeFlow CLI - 智能命令行时间追踪工具
A smart command-line time tracking tool with Pomodoro support
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="timeflow-cli",
    version="1.0.0",
    author="TimeFlow Team",
    author_email="hello@timeflow.dev",
    description="智能命令行时间追踪工具 | A smart CLI time tracking tool with Pomodoro support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gitstq/timeflow-cli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Scheduling",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "timeflow=timeflow.cli:main",
            "tf=timeflow.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
