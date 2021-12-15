from cfg.cfg import do_cfg

def cfg(built_result, symbol, *argc, **kwargs):
    return do_cfg(built_result.lib, symbol=symbol, *argc, **kwargs)
