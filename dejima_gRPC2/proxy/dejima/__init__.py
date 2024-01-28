import traceback
import inspect
import linecache
import psycopg2
from dejima import load_executer
from dejima import bench_executer
from dejima.executer import Executer
from dejima.loader import Loader
from dejima.global_bencher import GlobalBencher
from dejima.local_bencher import LocalBencher

errors = psycopg2.errors

DatabaseError = psycopg2.DatabaseError

class TxTerminated(Exception):
    pass

# LockNotAvailable = errors.LockNotAvailable
class GlobalLockNotAvailable(Exception):
    pass

def out_err(e=None, info=None, light_trace=True, out_trace=False):
    # Get the caller's frame
    frame_info = inspect.stack()[1]
    caller_frame = frame_info[0]

    # Get the function name, file name, and line number
    func_name = caller_frame.f_code.co_name
    file_name = caller_frame.f_code.co_filename
    line_num = caller_frame.f_lineno

    # Get the source code of the line
    line = linecache.getline(file_name, line_num).strip()

    if out_trace: light_trace = True

    if light_trace:
        print()
        print("----------------------- Dejima Error Info -----------------------")
    if light_trace:
        print(f'File "{file_name}", line {line_num}, in {func_name}')
        print(f"  {line}")
    if info: print("Comment:", info)
    if e: print(f"{type(e)}: {e}")
    if out_trace:
        print("------------------ Trackback ------------------")
        print(traceback.format_exc().strip())
        print("-----------------------------------------------")
    if light_trace:
        print("-----------------------------------------------------------------")
        print()


def get_executer(executer_name=None):
    if executer_name == "load":
        return load_executer.LoadExecuter()
    if executer_name == "bench":
        return bench_executer.BenchExecuter()
    return Executer()
