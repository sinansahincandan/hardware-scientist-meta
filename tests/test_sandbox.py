from hs import sandbox


def test_sandbox_numpy_matplotlib_pint():
    result = sandbox.run_script(
        "import numpy, matplotlib.pyplot, pint\nprint(float(numpy.array([1.0,2.0]).sum()))")
    assert result.ok, result.stderr
    assert "3.0" in result.stdout


def test_sandbox_socket_refused():
    result = sandbox.run_script("import socket\nprint(socket)")
    assert not result.ok
    assert "not allowed" in result.stderr


def test_sandbox_timeout():
    result = sandbox.run_script("while True:\n    pass", timeout=2.0)
    assert result.timed_out or not result.ok
