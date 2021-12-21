from cfg.cfg import do_cfg

def cfg(built_result, symbol=None, *argc, **kwargs):
    if symbol is None:
        symbol = built_result.get_default_function_name()
    if not symbol:
        raise ValueError("Couldn't find default function in build {build_result}")
    return do_cfg(built_result.lib, symbol=symbol, *argc, **kwargs)
