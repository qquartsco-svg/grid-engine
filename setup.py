"""
Grid Engine - Setup Configuration
Grid Engine 패키지 설정
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="grid-engine",
    version="0.1.1",
    author="Qquarts co.",
    author_email="",
    description="Grid Engine - 2D spatial state memory engine using Ring ⊗ Ring structure",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/qquartsco-svg/grid-engine",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "ring-attractor-engine>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/qquartsco-svg/grid-engine/issues",
        "Source": "https://github.com/qquartsco-svg/grid-engine",
        "Documentation": "https://github.com/qquartsco-svg/grid-engine#readme",
    },
)

