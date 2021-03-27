from setuptools import setup

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

with open("requirements.txt", "r") as req_file:
    requirements = req_file.read().splitlines()

setup(
    name="herokron",
    version="4.0.0",
    description=(
        "Herokron is a python package used to make switching Heroku apps on/off easy, especially between accounts. "
        "The primary use case is from the command line in the form of a cron job (hence the ending kron)"
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

