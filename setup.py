from setuptools import find_packages, setup

setup(
    name="esm_tools_yaml",
    version="0.1.0",
    author="Paul Gierz",
    author_email="pgierz@awi.de",
    description="A package for ESM (Earth System Models) tools to support parsing of YAML configurations",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/pgierz/esm_tools_yaml",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.6",
    install_requires=[
        "ruamel.yaml>=0.18.6",
        "loguru",
        # Add other dependencies as needed
    ],
    extras_require={
        "dev": [
            "pytest>=6.2",  # For running tests
            "pytest-cov>=2.12",  # For generating coverage reports
            "flake8>=4.0",  # For code linting
            "mypy>=0.910",  # For static type checking
            "sphinx>=4.2",  # For generating documentation
            "sphinx-rtd-theme>=1.0",  # For the ReadTheDocs theme
            # Add other development dependencies as needed
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
)
