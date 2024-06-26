# setup.py
from setuptools import setup, find_packages

setup(
    name="novelai-proxy-service",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "flask",
        "requests",
        "python-dotenv",
        "argon2-cffi",
    ],
)
