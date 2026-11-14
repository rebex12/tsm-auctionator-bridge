#!/usr/bin/env python3
"""Create an installable ZIP with a single TSMAuctionatorBridge/ root folder."""
from pathlib import Path
import json
import re
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
ADDON = ROOT / "TSMAuctionatorBridge"
toc = (ADDON / "TSMAuctionatorBridge.toc").read_text(encoding="utf-8")
version = re.search(r"^## Version: ([\w.-]+)$", toc, re.MULTILINE).group(1)
interface = int(re.search(r"^## Interface: (\d+)$", toc, re.MULTILINE).group(1))
output = ROOT / "dist" / f"TSMAuctionatorBridge-{version}-forever.zip"
output.parent.mkdir(exist_ok=True)
with ZipFile(output, "w", ZIP_DEFLATED) as archive:
    for path in sorted(ADDON.iterdir()):
        if path.is_file():
            archive.write(path, f"TSMAuctionatorBridge/{path.name}")
    for filename in ("README.md", "CHANGELOG.md"):
        archive.write(ROOT / filename, f"TSMAuctionatorBridge/{filename}")
with ZipFile(output) as archive:
    assert archive.testzip() is None
    assert "TSMAuctionatorBridge/TSMAuctionatorBridge.toc" in archive.namelist()
    for filename in toc.splitlines():
        filename = filename.strip()
        if filename and not filename.startswith("#"):
            assert f"TSMAuctionatorBridge/{filename}" in archive.namelist(), filename

# WowUp reads this sidecar when it is attached to the same GitHub Release as
# the ZIP. Keep the suffix too, for clients that select by filename instead.
metadata = {
    "releases": [{
        "name": "TSM Auctionator Bridge",
        "version": version,
        "filename": output.name,
        "nolib": False,
        "metadata": [{"flavor": "forever", "interface": interface}],
    }],
}
(output.parent / "release.json").write_text(
    json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
)
print(output)
