import inspect


def print_call_stack():
    """Easy access to the current call stack for debugging"""
    for frame in inspect.stack():
        print(f"{frame.filename}:{frame.lineno} {frame.function}")
