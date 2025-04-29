# setup.py
from setuptools import setup, find_packages

setup(
    name="wh40kgame",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
       # e.g. "numpy>=1.18", …
    ],
    entry_points={
      "console_scripts": [
        "wh40k=wh40kgame.main:main",
      ]
    }
)
