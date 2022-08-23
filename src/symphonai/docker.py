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
    tag = f"sym/{currentdir}:{dockerfile}"
    print(f"Building {tag}")
    os.system(f"docker build -q -t {tag} -f env/{dockerfile} {os.getcwd()}")
    inject_sympy_dockerfile(tag)

def build_mosquitto():
    print(f"Building symphonai/mosquitto")
    os.system(f"docker build -q -t symphonai/mosquitto {symdir}/mosquitto")

def build_nginx():
    print(f"Building symphonai/nginx")
    os.system(f"docker build -q -t symphonai/nginx {symdir}/nginx")

