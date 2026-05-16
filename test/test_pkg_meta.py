"""Tests whether or not Package version and ADIF version are avaialable"""


def test_pkg_meta_exposed() -> None:
    """Test if pakage version and adif sepc versoin are available"""
    import adif_mcp

    assert hasattr(adif_mcp, "__version__")
    assert isinstance(adif_mcp.__version__, str) and len(adif_mcp.__version__) > 0
    assert hasattr(adif_mcp, "__adif_spec__")
    assert adif_mcp.__adif_spec__ in {"3.1.5", "3.1.6", "3.1.7", "3.2.0"}  # keep in sync as needed
