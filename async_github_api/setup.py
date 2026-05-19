from setuptools import setup, find_packages

setup(
    name="async-github-api",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.8"
    ],
    python_requires=">=3.8",
    author="Raghu",
    description="Async GitHub API Wrapper Library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/pailaraghunathreddy21-afk/python-cybersecurity-portfolio",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)