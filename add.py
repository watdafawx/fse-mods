"""python add.py <repo clone> [--dry-run]: put a mod's current version into index.json.

The clone is the mod's public repo (its root holds info.json), at the commit to release. add.py zips that commit
(git archive: <name>/ at the top, without test/ and art/ (sources)), makes the GitHub release v<version> on the repo with the zip as its
asset (gh), and writes the entry (url, sha256, info.json fields) into index.json. Fields only the index has (fse,
plugins, pypath, repo) are kept from the entry already there; set them by hand for a new mod. Then commit and push
this repo: players see the version once index.json on main lists it.
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(*args, cwd=None):
    return subprocess.run(args, cwd=cwd, capture_output=True, check=True).stdout


def main():
    clone = Path(sys.argv[1]).resolve()
    dry = "--dry-run" in sys.argv
    if run("git", "status", "--porcelain", cwd=clone).strip():
        sys.exit(f"{clone} has uncommitted changes: the zip is made from a commit")
    info = json.loads((clone / "info.json").read_text(encoding="utf-8-sig"))
    name, version = info["name"], info["version"]
    remote = run("git", "remote", "get-url", "origin", cwd=clone).decode().strip()
    repo = re.search(r"github\.com[:/](.+?)(?:\.git)?$", remote).group(1)
    zip_name = f"{name}_{version}.zip"
    out = HERE / "out" / zip_name
    out.parent.mkdir(exist_ok=True)
    run("git", "archive", "--format=zip", f"--prefix={name}/", "-o", str(out), "HEAD", "--", ".", ":(exclude)test", ":(exclude)art",
        cwd=clone)
    sha = hashlib.sha256(out.read_bytes()).hexdigest()
    url = f"https://github.com/{repo}/releases/download/v{version}/{zip_name}"

    index_file = HERE / "index.json"
    index = json.loads(index_file.read_text(encoding="utf-8"))
    old = next((m for m in index["mods"] if m["name"] == name), {})
    entry = {"name": name, "title": info.get("title", name), "author": info.get("author", ""),
             "description": info.get("description", ""), "repo": f"https://github.com/{repo}", "version": version,
             "url": url, "sha256": sha, "fse": old.get("fse", "0.1.0"), "plugins": old.get("plugins", []),
             "dependencies": info.get("dependencies", [])}
    if old.get("pypath"):
        entry["pypath"] = True
    print(json.dumps(entry, indent=2))
    if dry:
        return
    tag = f"v{version}"
    if subprocess.run(["gh", "release", "view", tag, "--repo", repo], capture_output=True).returncode == 0:
        run("gh", "release", "upload", tag, str(out), "--clobber", "--repo", repo)
    else:
        run("gh", "release", "create", tag, str(out), "--repo", repo, "--title", f"{info.get('title', name)} {version}",
            "--notes", f"For the fse mod catalog (github.com/watdafawx/fse-mods). Zip sha256: {sha}",
            "--target", run("git", "rev-parse", "HEAD", cwd=clone).decode().strip())
    index["mods"] = [m for m in index["mods"] if m["name"] != name] + [entry]
    index["mods"].sort(key=lambda m: m["name"])
    index_file.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"index.json: {name} {version}")


main()
