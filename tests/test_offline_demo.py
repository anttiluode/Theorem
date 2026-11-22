"""The HTML microscope must remain an offline, parseable standalone page."""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import pytest


def test_expected_fields_and_no_network_dependencies():
    html=(Path(__file__).parent.parent/"index.html").read_text()
    for key in ("original","shifted","difference","spectrum","ky","kx",
                "Exact dark pattern","Maximum reveal","function modeGain",
                "function render"):
        assert key in html
    assert "<canvas" in html and "</script>" in html
    assert "https://" in html  # ordinary source citations are okay
    assert "<script src=" not in html  # no scripts downloaded from a third party


@pytest.mark.skipif(shutil.which("node") is None,reason="Node not installed")
def test_inline_javascript_is_syntactically_valid():
    html=(Path(__file__).parent.parent/"index.html").read_text()
    scripts=re.findall(r"<script>(.*?)</script>",html,re.S|re.I)
    assert len(scripts)==1
    with tempfile.TemporaryDirectory() as t:
        path=Path(t)/"microscope.js"
        path.write_text(scripts[0])
        run=subprocess.run(["node","--check",str(path)],
                           capture_output=True,text=True)
    assert run.returncode==0,run.stderr
