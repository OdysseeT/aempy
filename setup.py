import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aempy-odyssee", # Replace with your own username
    version="0.0.1",
    author="Odyssée TREMOULIS",
    author_email="otremoulis@gmail.com",
    description="Python library to interact with Adobe Experience Manager (AEM)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OdysseeT/aempy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
