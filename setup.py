import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fat",
    version="0.1.2",
    author="Samuel Vanderwaal",
    author_email="samuel.vanderwaal@gmail.com",
    description="A Python client library for the FAT protocol.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/samuelvanderwaal/fat-py",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["factom-keys", "factom-core", "urllib3", "requests"]
)
