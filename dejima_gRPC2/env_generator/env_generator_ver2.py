import os
import sys
from utils.tpcc.tpcc_env_gen import TPCCEnvGenerator
from utils.ycsb.ycsb_env_gen import YCSBEnvGenerator
from utils.tenv.tenv_env_gen import TENVEnvGenerator

# add root directory to sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)


# get benchmark name
if len(sys.argv) < 2:
    print("At least a argument is required")
    exit()

benchmark = sys.argv[1].upper()


# generate environment
if benchmark == "TPCC":
    env_generator = TPCCEnvGenerator(sys.argv)
elif benchmark == "YCSB":
    env_generator = YCSBEnvGenerator(sys.argv)
elif benchmark == "TENV":
    env_generator = TENVEnvGenerator(sys.argv)
else:
    print("Invalid benchmark name")
    exit()
env_generator.generate_env()
