from setuptools import find_packages
from setuptools import setup


with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="RustTranspiler",
    version="0.6.0",
    description="Python to Rust Transpiler",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tayler Porter",
    author_email="taylerporter@gmail.com",
    url="https://github.com/tayler6000/transpiler",
    project_urls={
        "Bug Tracker": "https://github.com/tayler6000/transpiler/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Natural Language :: English",
    ],
    packages=find_packages(exclude=("tests",)),
    entry_points={
        "console_scripts": [
            "rusttranspiler = rusttranspiler.main:cli",
        ],
    },
    package_data={"rusttranspiler": ["py.typed"]},
    python_requires="~=3.12.0",
)
