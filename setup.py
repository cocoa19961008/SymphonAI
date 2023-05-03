import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name='symphonai',
    version='0.2.4',
    scripts=['sym'],
    author="Sven Schultze",
    author_email="schultze.sven@googlemail.com",
    description="A tool to build and run docker images together",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_namespace_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    zip_safe = False,
    #package_data={
    #    'symphonai/envs': ['*'],
    #    'symphonai/mosquitto': ['*'],
    #    'symphonai/nginx': ['*'],
    #    'symphonai/sympy': ['*'],
    #    'symphonai/template': ['*'],
    #},
    
    package_data={
    	"symphonai": ["*"],
    	"symphonai.mosquitto": ["*", "config/*"],
    	"symphonai.nginx": ["*"],
    	"symphonai.envs": ["*"],
    	"symphonai.sympy": ["*"],
    	"symphonai.template": ["*"]
    },
    install_requires=[
        'pyyaml',
        'fire'
    ]
)

