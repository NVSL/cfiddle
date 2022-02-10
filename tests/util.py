from cfiddle import *
from cfiddle.util import invoke_process


def build_and_run(source_file, build_parameters, function, arguments):
    executable = build_one(source_file, build_parameters)

    return run_one(executable, function, arguments)


def build_one(*args, **kwargs):
    r = build(*args, **kwargs)
    if len(r) != 1:
        ValueError("You specified more than one build.")
    return r[0]


def run_one(exe, function, arguments=None, **kwargs):
    if arguments is None:
        arguments = {}
    return run(executable=[exe], function=[function], arguments=[arguments], **kwargs)[0]

def skip_if_go_not_available():
    go_is_available, _ = invoke_process(["go", "version"])
    if not go_is_available:
        pytest.skip("unsupported configuration")

