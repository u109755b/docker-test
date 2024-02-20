import dejima

def _execute(params):
    if "stmt" not in params:
        raise ValueError("stmt is not included in params")

    stmt = params["stmt"]

    # create executer
    executer = dejima.get_executer("load")
    executer.create_tx()
    executer.lock_global(['dummy'])

    # workload
    stmt = stmt

    # execution
    print("")
    print("stmt:", stmt)
    executer.execute_stmt(stmt)
    try:
        execution_result = executer.fetchone()
    except Exception as e:
        dejima.out_err(e)
        execution_result = [[None]]

    print(f"{type(execution_result)}: {execution_result}")
    if type(execution_result) is list:
        try:
            print("Row result:", list(execution_result[0].keys()))
            for result in execution_result:
                print("Row result:", result)
        except Exception as e:
            dejima.out_err(e, "Dict is not available", light_trace=False)
    else:
        print("result is not list")

    # propagation
    executer.propagate()

    # termination
    result = executer.terminate()
    print("committed?:", result)
    return {"result": execution_result}


def execute(params):
    try:
        return _execute(params)
    except Exception as e:
        dejima.out_err(e, "failed execute a statement", out_trace=True)
        return {"result": "Internal error"}
