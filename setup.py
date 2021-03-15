from setuptools import setup
from herokron import __version__

with open("README.md", encoding="utf-8") as readme_file:
    readme = readme_file.read()

with open("requirements.txt", encoding="utf-8") as req_file:
    requirements = req_file.read().splitlines()

setup(
    name="herokron",
    version=__version__,
    description=(
        "Herokron is a mainly command line app used to make updating Heroku apps easy between accounts."
    ),
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Hexiro",
    author_email="realhexiro@gmail.com",
    url="https://github.com/Hexiro/Herokron",
    packages=["herokron"],
    entry_points={
        "console_scripts": [
            "herokron = herokron.herokron:main"
        ]
    },
    python_requires=">=3.6",
    install_requires=requirements,
    license="CC0",
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: CC0 License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python",
        "Topic :: Software Development"
    ],
    keywords=[
        "Python",
        "Python3",
        "Heroku",
        "Herokron",
        "Cron",
        "Crontab"
    ]
)
