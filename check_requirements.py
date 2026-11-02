import json
import sys
import urllib.error
import urllib.request

from packaging.specifiers import SpecifierSet
from packaging.version import Version


def fetch_release(name, version):
    url = f"https://pypi.org/pypi/{name}/{version}/json"
    try:
        with urllib.request.urlopen(url) as response:
            return json.load(response)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def min_python(requires_python):
    versions = [
        Version(s.version)
        for s in SpecifierSet(requires_python)
        if s.operator in (">=", ">", "~=", "==")
    ]
    return max(versions, default=Version("0"))


def main():
    with open("requirements.txt") as f:
        requirements = [
            line.strip() for line in f if line.strip() and not line.startswith("#")
        ]

    not_found = []
    incompatible = []
    highest = None

    for req in requirements:
        name, version = req.split("==")
        data = fetch_release(name, version)
        if data is None:
            not_found.append(req)
            continue
        requires_python = data["info"].get("requires_python")
        if not requires_python:
            continue
        if "3.11" not in SpecifierSet(requires_python):
            incompatible.append(req)
        minimum = min_python(requires_python)
        if highest is None or minimum > highest[1]:
            highest = (req, minimum)

    print(f"Dependencies checked: {len(requirements)}")
    print(f"Not found on PyPI: {len(not_found)}")
    print(f"Incompatible with Python 3.11: {len(incompatible)}")
    print(
        f"Highest requirement: {f'{highest[0]} (>={highest[1]})' if highest else 'None'}"
    )


if __name__ == "__main__":
    main()
