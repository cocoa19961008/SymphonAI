import setuptools

setuptools.setup(
    name='sympy',  
    version='0.1',
    author="Sven Schultze",
    author_email="schultze.sven@googlemail.com",
    description="A tool to communicate within symphonai",
    long_description="long_description",
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "paho-mqtt>=1.6.1",
        "bottle>=0.12.23",
        "Paste>=3.5.1",
        "requests>=2.28.1",
        "tornado",
        "asyncio"
    ]
)