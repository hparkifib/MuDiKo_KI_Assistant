"""
Setup-Konfiguration für MIDI Analyzer Package
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="midi-analyzer",
    version="2.0.0",
    author="MIDI Analyzer Project",
    description="MIDI analysis and comparison tool for backend integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["apps", "examples", "docs", "test_data"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Sound/Audio :: MIDI",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "mido>=1.3.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
        "api": [
            "fastapi>=0.95.0",
            "python-multipart>=0.0.6",
        ],
    },
    keywords="midi, music, analysis, comparison, backend, api",
    project_urls={
        "Source": "https://github.com/yourname/midi-analyzer",
    },
)
