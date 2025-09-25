from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="eport-generator",
    version="0.1.0",
    author="Giselle Penaloza",
    author_email="gisellep89@gmail.com",
    description="GitHub Repository Contribution Report Generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Gisellev14/report-generator",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        "Topic :: Office/Business",
    ],
    python_requires=">=3.7",
    install_requires=[
        "python-dotenv>=0.19.0",
        "PyGithub>=1.55",
        "pandas>=1.3.0",
        "matplotlib>=3.4.0",
        "python-dateutil>=2.8.2",
        "pydantic>=1.8.0",
        "requests>=2.26.0",
        "tqdm>=4.62.0",
        "plotly>=5.3.0",
        "python-multipart>=0.0.5",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "pyyaml>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "github-report=github_report_generator.application.cli:main",
        ],
    },
)
