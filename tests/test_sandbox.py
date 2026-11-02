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


def test_sandbox_cannot_read_the_home_folder():
    """Review finding 8: shell startup files in the home folder hold the API key."""
    import os
    import pwd

    home = pwd.getpwuid(os.getuid()).pw_dir
    result = sandbox.run_script(f"print(open({home + '/.hs_sandbox_probe'!r}).read())")
    assert not result.ok
    assert "PermissionError" in result.stderr and "home folder" in result.stderr


def test_sandbox_cannot_write_outside_its_folder(tmp_path):
    target = tmp_path / "escape.txt"
    result = sandbox.run_script(f"open({str(target)!r}, 'w').write('x')")
    assert not target.exists() and not result.ok
    assert "PermissionError" in result.stderr


def test_sandbox_sketch_still_works():
    result = sandbox.run_script(
        "import matplotlib.pyplot as plt\nplt.xkcd()\nplt.plot([0, 1], [0, 1])\nplt.title('beam')\n"
        "plt.savefig('sketch.png')\nprint('saved')")
    assert result.ok, result.stderr
    assert sandbox.sketch_bytes_of(result)
