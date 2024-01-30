import traceback
import inspect
import linecache
import psycopg2

# LockNotAvailable
LockNotAvailable = psycopg2.errors.LockNotAvailable

# LocalLockNotAvailable
class LocalLockNotAvailable(LockNotAvailable):
    pass

# GlobalLockNotAvailable
class GlobalLockNotAvailable(LockNotAvailable):
    pass

# DatabaseErrorpsycopg2.DatabaseError
DatabaseError = psycopg2.DatabaseError

# SyntaxError
SyntaxError = psycopg2.errors.SyntaxError

# TxTerminated
class TxTerminated(Exception):
    pass


# out_err
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

    # display error info
    if light_trace:
        print()
        print("----------------------- Dejima Error Info -----------------------")
    if light_trace:
        print(f'File "{file_name}", line {line_num}, in {func_name}')
        print(f"  {line}")
    if info: print("Comment:", info)
    if e: print(f"{type(e)}: {e.strip()}")
    if out_trace:
        print("------------------ Trackback ------------------")
        print(traceback.format_exc().strip())
        print("-----------------------------------------------")
    if light_trace:
        print("-----------------------------------------------------------------")
        print()
