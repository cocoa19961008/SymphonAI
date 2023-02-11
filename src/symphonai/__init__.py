import os
from symphonai import docker
import shutil
import json
import yaml
from glob import glob

symdir = "/".join(__file__.split("/")[:-1])
currentdir = os.getcwd().split('/')[-1]

class CLI:
    """
    A tool to build and run dockerized nodes connected with gRPC in a clear project structure.
    """
    def setup(self):
        """
        Setup project structure
        """
        os.makedirs("env", exist_ok=True)
        os.makedirs("src", exist_ok=True)
        os.makedirs("protos", exist_ok=True)
        os.makedirs(".sym", exist_ok=True)

        if not os.path.exists("global.env"):
            open("global.env", "w").close()

    def create(self, name, env):
        """
        Create a new package with name <name> and dockerfile <env>
        """
        print("Creating package", name, "with env", env)

        pkg_dir = f"src/{name}"
        if os.path.exists(pkg_dir):
            print(f"Package of name {name} already exists")
            return

        if not os.path.exists(f"env/{env}"):
            print(f"Env {env} does not exist. Creating from default env")
            shutil.copy(f"{symdir}/envs/default", f"env/{env}")

        shutil.copytree(f"{symdir}/template", f"{pkg_dir}")

        with open(f"{pkg_dir}/config.json", "w") as f:
            json.dump({
                "env": env,
                "options": {},
            }, f, indent=4)

    def build(self):
        """
        Build all docker images and create docker-compose.yml
        """
        for dockerfile in os.listdir("env"):
            docker.build(dockerfile)

        pkgs = {}
        for pkg in os.listdir("src"):
            pkgs[pkg] = json.load(open(f"src/{pkg}/config.json"))

        services = dict()
        for pkg, config in pkgs.items():
            services[pkg] = config["options"]
            services[pkg].update({
                "image": f"sym/{currentdir}:{config['env']}",
                "volumes": [f"{os.getcwd()}/protos:/node/protos", f"{os.getcwd()}/src/{pkg}:/node"],
                "networks": [currentdir],
                "env_file": [f"{os.getcwd()}/global.env", f"{os.getcwd()}/src/{pkg}/params.env"],
                "environment": [f"SYMNAME={pkg}", "PYTHONPYCACHEPREFIX=../pycache"],
                "extra_hosts": [f"symhost:host-gateway"],
            })

        with open(".sym/docker-compose.yml", "w") as f:
            yaml.dump({
                "version": "3.7",
                "services": services,
                "networks": {
                    currentdir: {
                        "driver": "bridge",
                    },
                }
            }, f)

    def run(self, profile=None):
        """
        Run the docker containers
        """
        if profile:
            os.system(f"docker compose -f .sym/docker-compose.yml --profile {profile} -p sym/{currentdir} up --remove-orphans")
        else:
            os.system(f"docker compose -f .sym/docker-compose.yml -p sym-{currentdir} up --remove-orphans")

    def stop(self):
        """
        Stop the docker containers
        """
        os.system("docker compose -f .sym/docker-compose.yml down")

    def docs(self):
        """
        Generate documentation for all protos
        """
        for proto in glob(f"protos/*.proto"):
            package = proto.split("/")[-1].split(".")[0]
            os.system(f'docker run --rm -v {os.getcwd()}/docs:/out -v {os.getcwd()}/protos:/protos/protos pseudomuto/protoc-gen-doc */{package}.proto -I / --doc_opt=markdown,{package}.md')
