from fiddle import *

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
    return run([(exe, function, arguments)], **kwargs)[0]
