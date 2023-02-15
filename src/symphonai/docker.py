import os

symdir = "/".join(__file__.split("/")[:-1])
currentdir = os.getcwd().split('/')[-1]

def inject_sympy_dockerfile(tag):
    injection = [
        f"FROM {tag}",
        f"ADD sympy /root/sympy",
        f"RUN pip3 install /root/sympy",
        f"WORKDIR /node/",
        f"ENV PYTHONUNBUFFERED 1",
    ]
    injectstr = '\n'.join(injection)
    os.system(f"docker build -q -t {tag} {symdir} -f-<<EOF\n{injectstr}\nEOF")

def build(dockerfile):
    tag = f"sym/{currentdir}.{dockerfile}"
    print(f"Building {tag}")
    os.system(f"docker build -t {tag} -f env/{dockerfile} {os.getcwd()}")
    inject_sympy_dockerfile(tag)
    return tag


def build_on_platform(dockerfile, platforms):
    tag = f"sym/{currentdir}.{dockerfile}"
    platforms = ",".join(platforms)
    print(f"Building {tag}")
    os.system(f"docker buildx build --platform {platforms} -t {tag} -f env/{dockerfile} {os.getcwd()}")
    inject_sympy_dockerfile(tag)
    return tag

def build_node_image(image, node, tag, platforms):
    injection = [
        f"FROM {image}",
        f"COPY src/{node} /node",
        f"COPY protos /node/protos",
    ]
    injectstr = '\n'.join(injection)
    name = f"{image}.{node}"
    print(f"Building {name}:{tag}")
    platforms = ",".join(platforms)
    os.system(f"docker buildx build --platform {platforms} -q -t {name}:{tag} . -f-<<EOF\n{injectstr}\nEOF")
