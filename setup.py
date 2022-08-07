import setuptools

setuptools.setup(
    name='symphonai',  
    version='0.1',
    scripts=['sym'],
    author="Sven Schultze",
    author_email="schultze.sven@googlemail.com",
    description="A tool to build and run docker images",
    long_description="long_description",
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)