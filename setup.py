from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="maximus-client",
    version="0.1.0",
    author="Vodeninja",
    author_email="root@vodeninja.ru",
    description="Python library for working with MAX messenger API through WebSocket connections",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Vodeninja/maximus-client",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    keywords="max messenger api websocket client",
    project_urls={
        "Bug Reports": "https://github.com/Vodeninja/maximus-client/issues",
        "Source": "https://github.com/Vodeninja/maximus-client",
    },
)