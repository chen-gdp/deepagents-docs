"""Build a pinned, offline-readable source atlas from a local Deep Agents clone.

Authors:
    OpenAI coding assistant
References:
    https://github.com/langchain-ai/deepagents
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import subprocess
import tarfile
from collections import defaultdict
from collections.abc import Iterator
from pathlib import Path

PIN = "c4e2811312718e98b1465b6e67c34997ca72c793"
TEXT_SUFFIXES = {
    ".py",
    ".md",
    ".toml",
    ".yaml",
    ".yml",
    ".json",
    ".sh",
    ".txt",
    ".sql",
    ".js",
    ".ts",
    ".tsx",
    ".css",
    ".html",
    ".ipynb",
    ".j2",
    ".jinja",
}
SKIP_NAMES = {"AGENTS.md", "CLAUDE.md", "INSTRUCTIONS.md", "uv.lock", "package-lock.json"}


def symbols_for(text: str, path: str) -> tuple[list[dict], str, str | None]:
    """Extract navigable Python definitions without importing untrusted source.

    Args:
        text: UTF-8 source content.
        path: Repository-relative path.

    Returns:
        Definitions, module summary, and a syntax parse diagnostic when present.
    """
    if not path.endswith(".py"):
        return [], "", None
    try:
        tree = ast.parse(text)
    except SyntaxError as error:
        if "multiple exception types must be parenthesized" not in str(error):
            return [], "", str(error)
        # Python 3.14 permits bare exception tuples; keep original source/line
        # numbers while adapting headers solely for the Conda 3.12 AST indexer.
        compatible = re.sub(
            r"(?m)^(\s*except\*? )([^:\n]+,[^:\n]+):",
            lambda match: f"{match[1]}({match[2]}):" if not match[2].startswith("(") else match[0],
            text,
        )
        try:
            tree = ast.parse(compatible)
        except SyntaxError as compatibility_error:
            return [], "", str(compatibility_error)
    symbols = []
    for node in tree.body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            symbols.append(
                {
                    "name": node.name,
                    "kind": "class" if isinstance(node, ast.ClassDef) else "function",
                    "line": node.lineno,
                    "end": node.end_lineno,
                    "doc": (ast.get_docstring(node) or "").split("\n\n")[0],
                }
            )
            if isinstance(node, ast.ClassDef):
                for method in node.body:
                    if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        symbols.append(
                            {
                                "name": f"{node.name}.{method.name}",
                                "kind": "method",
                                "line": method.lineno,
                                "end": method.end_lineno,
                                "doc": (ast.get_docstring(method) or "").split("\n\n")[0],
                            }
                        )
    return symbols, (ast.get_docstring(tree) or "").split("\n\n")[0], None


def pinned_files(checkout: Path, revision: str) -> Iterator[tuple[str, str]]:
    """Read text blobs from Git, never from the mutable index or working tree.

    Args:
        checkout: Local repository containing the revision.
        revision: Commit whose immutable tree should be exported.

    Yields:
        Repository-relative names and original UTF-8 text.
    """
    with subprocess.Popen(["git", "archive", revision], cwd=checkout, stdout=subprocess.PIPE) as process:
        with tarfile.open(fileobj=process.stdout, mode="r|") as archive:
            for entry in archive:
                path = Path(entry.name)
                if not entry.isfile() or path.name in SKIP_NAMES:
                    continue
                if any(part in {".agents", "openwiki", ".claims"} for part in path.parts):
                    continue
                if path.suffix not in TEXT_SUFFIXES and path.name not in {
                    "Makefile",
                    "LICENSE",
                    "Dockerfile",
                    ".gitignore",
                }:
                    continue
                with archive.extractfile(entry) as stream:
                    try:
                        yield entry.name, stream.read().decode("utf-8")
                    except UnicodeDecodeError:
                        continue
        if process.wait() != 0:
            raise subprocess.CalledProcessError(process.returncode, process.args)


def build_atlas(checkout: Path, output: Path) -> dict:
    """Export tracked text files into lazy-loaded package bundles.

    Args:
        checkout: Path to the pinned local Git checkout.
        output: Directory for generated JSON files.

    Returns:
        Manifest with revision, file metadata, definitions, and provenance.

    Raises:
        ValueError: If the checkout does not match the expected revision.
    """
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=checkout, text=True).strip()
    if revision != PIN:
        raise ValueError(f"Expected {PIN}, received {revision}; update content and citations before repinning.")
    output.mkdir(parents=True, exist_ok=True)
    bundles = defaultdict(dict)
    manifest = {
        "revision": revision,
        "repository": "langchain-ai/deepagents",
        "files": [],
        "exclusions": "Binary assets, lockfiles, generated dependency data, and agent instruction files are not embedded. All tracked Python implementation and test files are included.",
        "parseDiagnostics": [],
    }
    for name, text in pinned_files(checkout, revision):
        path = Path(name)
        bucket = (
            path.parts[1]
            if len(path.parts) > 2 and path.parts[0] == "libs"
            else path.parts[0]
            if len(path.parts) > 1
            else "root"
        )
        symbols, summary, diagnostic = symbols_for(text, name)
        if diagnostic:
            manifest["parseDiagnostics"].append({"path": name, "error": diagnostic})
        bundles[bucket][name] = text
        manifest["files"].append(
            {
                "path": name,
                "bundle": bucket,
                "lines": len(text.splitlines()),
                "bytes": len(text.encode()),
                "sha256": hashlib.sha256(text.encode()).hexdigest(),
                "summary": summary,
                "symbols": symbols,
                "test": "/tests/" in name or path.name.startswith("test_"),
            }
        )
    for bucket, files in bundles.items():
        (output / f"{bucket}.json").write_text(json.dumps(files, ensure_ascii=False, separators=(",", ":")) + "\n")
    manifest["statistics"] = {
        "files": len(manifest["files"]),
        "pythonFiles": sum(f["path"].endswith(".py") for f in manifest["files"]),
        "symbols": sum(len(f["symbols"]) for f in manifest["files"]),
        "lines": sum(f["lines"] for f in manifest["files"]),
        "bundles": len(bundles),
    }
    (output / "index.json").write_text(json.dumps(manifest, ensure_ascii=False, separators=(",", ":")) + "\n")
    return manifest


def main() -> None:
    """Parse CLI arguments and build the atlas without importing the repository."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkout", type=Path)
    args = parser.parse_args()
    manifest = build_atlas(args.checkout.resolve(), Path(__file__).parent / "source")
    print(json.dumps(manifest["statistics"], indent=2))
    print(f"Python parse diagnostics: {len(manifest['parseDiagnostics'])}")


if __name__ == "__main__":
    main()
