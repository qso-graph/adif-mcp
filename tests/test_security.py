"""Security audit tests for adif-mcp — MCP Security Framework compliance."""

import ast
import os
import re

SRC_DIR = os.path.join(os.path.dirname(__file__), "..", "src", "adif_mcp")


def _all_py_sources():
    """Yield all Python source files under SRC_DIR."""
    for root, _, files in os.walk(SRC_DIR):
        for f in files:
            if f.endswith(".py"):
                yield os.path.join(root, f)


def test_no_print_credentials():
    """No print() calls with credential keywords."""
    pattern = re.compile(
        r"print\s*\(.*?(password|passwd|secret|api_key|token)",
        re.IGNORECASE,
    )
    for path in _all_py_sources():
        with open(path) as fh:
            src = fh.read()
        assert not pattern.search(src), f"Credential print in {path}"


def test_no_logging_credentials():
    """No logging calls with credential keywords."""
    pattern = re.compile(
        r"log(?:ging)?\.\w+\s*\(.*?(password|passwd|secret|api_key)",
        re.IGNORECASE,
    )
    for path in _all_py_sources():
        with open(path) as fh:
            src = fh.read()
        assert not pattern.search(src), f"Credential logging in {path}"


def test_no_subprocess():
    """No subprocess or shell=True usage."""
    pattern = re.compile(r"\bsubprocess\b|shell\s*=\s*True")
    for path in _all_py_sources():
        with open(path) as fh:
            src = fh.read()
        assert not pattern.search(src), f"subprocess/shell in {path}"


def test_all_urls_https():
    """All hardcoded URLs use HTTPS."""
    pattern = re.compile(r"http://(?!localhost|127\.0\.0\.1)")
    for path in _all_py_sources():
        with open(path) as fh:
            src = fh.read()
        assert not pattern.search(src), f"Non-HTTPS URL in {path}"


def test_error_messages_safe():
    """Credentials never interpolated in error messages."""
    dangerous = re.compile(
        r"\{(password|api_key|secret|creds\.password|creds\.api_key)\}",
        re.IGNORECASE,
    )
    for path in _all_py_sources():
        with open(path) as fh:
            for i, line in enumerate(fh, 1):
                if line.lstrip().startswith("#"):
                    continue
                matches = dangerous.findall(line)
                assert not matches, f"Credential interpolation in {path}:{i}: {line.strip()}"


def test_no_eval_exec():
    """No eval() or exec() in source."""
    for path in _all_py_sources():
        with open(path) as fh:
            src = fh.read()
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id in ("eval", "exec"):
                    raise AssertionError(f"eval/exec found in {path}")


def test_spec_resource_rejects_path_traversal(tmp_path):
    """A resource name cannot read a .json file outside the spec directory (#9)."""
    import json

    from adif_mcp.mcp import server

    outside = tmp_path / "probe.json"
    outside.write_text('{"secret": "outside the spec dir"}')
    spec_dir = os.path.join(os.path.dirname(server.__file__), "..", "resources", "spec", "317")
    rel = os.path.relpath(str(outside)[: -len(".json")], os.path.abspath(spec_dir))
    for name in (rel, rel.lower(), "../fields", "/etc/passwd", "all/../fields"):
        result = json.loads(server.get_spec_text(name))
        assert "error" in result and "secret" not in result, name


def test_spec_resource_unknown_name_is_an_error():
    """An unknown name is an error listing the names, never the whole spec (#9)."""
    import json

    from adif_mcp.mcp.server import get_spec_text

    raw = get_spec_text("nosuchresource")
    assert len(raw) < 10_000
    result = json.loads(raw)
    assert "error" in result
    assert "mode" in result["available"] and "all" in result["available"]
    # The names that must keep working.
    assert json.loads(get_spec_text("all"))["Adif"]["Version"] == "3.1.7"
    assert "Mode" in json.loads(get_spec_text("mode"))["Adif"]["Enumerations"]
    assert "Records" in json.loads(get_spec_text("fields"))["Adif"]["Fields"]
