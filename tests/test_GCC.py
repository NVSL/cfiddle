from cfiddle.Toolchain.GCC import GCCToolchain

def test_availabable():
    assert GCCToolchain.is_toolchain_available("x86") or GCCToolchain.is_toolchain_available("arm")
