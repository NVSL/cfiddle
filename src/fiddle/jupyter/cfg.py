from cfg.cfg import do_cfg

def cfg(built_result, symbol=None, *argc, **kwargs):
    if symbol is None:
        symbol = built_result.get_default_function_name()
    assert symbol
    return do_cfg(built_result.lib, symbol=symbol, *argc, **kwargs)
