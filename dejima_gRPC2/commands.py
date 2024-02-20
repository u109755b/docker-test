import os
import glob
import subprocess
import shutil
import sys
import argparse

# start
def start(N, env_directory, start_db=True, start_proxy=True):
    os.chdir(env_directory)
    peer_names = []
    if start_db:
        peer_names += [f"peer{i}-db" for i in range(1, N+1)]
    if start_proxy:
        peer_names += [f"peer{i}-proxy" for i in range(1, N+1)]

    if peer_names:
        subprocess.run(["docker-compose", "up"] + peer_names)
    else:
        print("no peers selected")

# remove
def remove(remove_db=True, remove_proxy=True):
    result = subprocess.run(["docker", "ps", "-a"], capture_output=True, text=True)
    lines = result.stdout.splitlines()
    dockers = []
    if remove_db:
        dockers += [line.split()[0] for line in lines if "db" in line]
    if remove_proxy:
        dockers += [line.split()[0] for line in lines if "proxy" in line]
    
    if dockers:
        subprocess.run(["docker", "rm", "-fv"] + dockers)
        print("removed dockers")
    else:
        print("no dockers found")

# update
def update():
    for root, dirs, _ in os.walk("."):
        for name in dirs:
            if name == '__pycache__':
                subprocess.run(["sudo", "rm", "-r", os.path.join(root, name)])

    proxy_paths = ["./env_generator/src/TENV/", "./env_generator/src/TPCC/", "./env_generator/src/YCSB/"]
    for path in proxy_paths:
        shutil.copytree("./proxy", os.path.join(path, "proxy"), dirs_exist_ok=True)
        shutil.copy("./db/postgresql.conf", os.path.join(path, "db", "postgresql.conf"))

    peer_dirs = []
    for base_path in ["./env_generator/TENV*", "./env_generator/TPCC*", "./env_generator/YCSB*"]:
        peer_dirs += glob.glob(base_path)

    for peer_dir in peer_dirs:
        config_path = os.path.join(peer_dir, "proxy", "dejima_config.json")
        shutil.move(config_path, os.path.join(peer_dir, "dejima_config.json"))
        shutil.rmtree(os.path.join(peer_dir, "proxy"))
        shutil.copytree("./proxy", os.path.join(peer_dir, "proxy"))
        shutil.move(os.path.join(peer_dir, "dejima_config.json"), config_path)
        shutil.copy("./db/postgresql.conf", os.path.join(peer_dir, "db", "postgresql.conf"))

    print("updated TENV, TPCC and TPCC files")


# commands
def start_command(args):
    remove()
    update()
    start(args.N, args.env_directory, start_db=True, start_proxy=True)

def startdb_command(args):
    remove(remove_db=True, remove_proxy=False)
    start(args.N, args.env_directory, start_db=True, start_proxy=False)

def startproxy_command(args):
    remove(remove_db=False, remove_proxy=True)
    update()
    start(args.N, args.env_directory, start_db=False, start_proxy=True)

def remove_command(args):
    remove()
    update()

def update_command(args):
    update()

command_mappings = {
    "start": start_command,
    "startdb": startdb_command,
    "startproxy": startproxy_command,
    "remove": remove_command,
    "update": update_command
}


# receive arguments and options
parser = argparse.ArgumentParser()

parser.add_argument("command_name", choices=command_mappings.keys(), help="which commands to use")
parser.add_argument("-N", type=int, help="number of peers")
parser.add_argument("-e", "--env_directory", help="environment directory")
args = parser.parse_args()

command = command_mappings[args.command_name]
command(args)


# command examples
# python3 commands.py start -N 3 -e env_generator/TPCC_N3/
# python3 commands.py startdb -N 3 -e env_generator/TPCC_N3/
# python3 commands.py startproxy -N 3 -e env_generator/TPCC_N3/
# python3 commands.py remove
# python3 commands.py update
