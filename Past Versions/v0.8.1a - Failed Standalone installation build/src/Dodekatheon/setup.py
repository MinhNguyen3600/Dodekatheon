# setup.py
from setuptools import setup, find_packages
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["os"],  # Add any packages your script uses
    "excludes": ["tkinter"],  # Exclude modules not used
    "include_files": []  # Include any additional files your script needs
}

build_exe_options = {
    "packages": ["pygame", "numpy"],
    "include_files": ["path_to_additional_files"]
}

setup(
    name="wh40kgame",
    version="0.8.1",
    description="Description of your application",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
       # e.g. "numpy>=1.18", …
    ],
    entry_points={
      "console_scripts": [
        "wh40k=wh40kgame.main:main",
      ]
    },
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=None)],
)
