#!/usr/bin/env python3
"""Scan Java package declarations and classify fixed canonical package names."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


PACKAGE_RE = re.compile(r"^\s*package\s+([A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*)\s*;")

ALWAYS_SINGULAR = {
    "configuration": "configuration",
    "configurations": "configuration",
    "xml": "xml",
    "xmls": "xml",
}

SINGULAR_TO_PLURAL = {
    "annotation": "annotations",
    "bean": "beans",
    "builder": "builders",
    "component": "components",
    "constant": "constants",
    "controller": "controllers",
    "conversion": "conversions",
    "dao": "daos",
    "domain": "domains",
    "dto": "dtos",
    "entity": "entities",
    "enumeration": "enumerations",
    "exception": "exceptions",
    "helper": "helpers",
    "interceptor": "interceptors",
    "mapper": "mappers",
    "repository": "repositories",
    "request": "requests",
    "serializer": "serializers",
    "service": "services",
    "util": "utils",
    "view": "views",
}

PLURAL_SEGMENTS = set(SINGULAR_TO_PLURAL.values())

SPANISH_TO_CANONICAL = {
    "anotacion": "annotations",
    "anotaciones": "annotations",
    "ayudante": "helpers",
    "ayudantes": "helpers",
    "componente": "components",
    "componentes": "components",
    "configuracion": "configuration",
    "configuraciones": "configuration",
    "constante": "constants",
    "constantes": "constants",
    "controlador": "controllers",
    "controladores": "controllers",
    "conversion": "conversions",
    "conversiones": "conversions",
    "entidad": "entities",
    "entidades": "entities",
    "excepcion": "exceptions",
    "excepciones": "exceptions",
    "mapeador": "mappers",
    "mapeadores": "mappers",
    "repositorio": "repositories",
    "repositorios": "repositories",
    "serializador": "serializers",
    "serializadores": "serializers",
    "servicio": "services",
    "servicios": "services",
    "utilidad": "utils",
    "utilidades": "utils",
    "vista": "views",
    "vistas": "views",
}


def scan(root: Path, source_roots: list[str]) -> dict[str, dict[str, object]]:
    packages: dict[str, dict[str, object]] = {}
    for source_root in source_roots:
        base = root / source_root
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.java")):
            package = None
            with path.open(encoding="utf-8") as source:
                for line in source:
                    match = PACKAGE_RE.match(line)
                    if match:
                        package = match.group(1)
                        break
            if package is None:
                continue
            entry = packages.setdefault(package, {"sources": set(), "files": []})
            entry["sources"].add(source_root.split("/")[1])
            entry["files"].append(str(path.relative_to(root)))

    result = {}
    for package in sorted(packages):
        entry = packages[package]
        result[package] = {
            "sources": sorted(entry["sources"]),
            "files": sorted(entry["files"]),
            "class_count": len(entry["files"]),
        }
    return result


def subtree_details(
    packages: dict[str, dict[str, object]],
    prefix: str,
) -> tuple[set[str], set[str]]:
    """Return all Java files and source roots below a package prefix."""
    files: set[str] = set()
    sources: set[str] = set()
    for package, entry in packages.items():
        if package == prefix or package.startswith(f"{prefix}."):
            files.update(entry["files"])
            sources.update(entry["sources"])
    return files, sources


def architecture_segment(segment: str) -> tuple[str, str] | None:
    """Return the fixed canonical name and the detected source form."""
    if segment in SPANISH_TO_CANONICAL:
        return SPANISH_TO_CANONICAL[segment], "spanish"
    if segment in ALWAYS_SINGULAR:
        return ALWAYS_SINGULAR[segment], "fixed_singular"
    if segment in SINGULAR_TO_PLURAL:
        return SINGULAR_TO_PLURAL[segment], "english_singular"
    if segment in PLURAL_SEGMENTS:
        return segment, "english_plural"
    return None


def scan_architecture(
    packages: dict[str, dict[str, object]],
) -> dict[str, dict[str, object]]:
    """Find architecture prefixes and apply names without using class cardinality."""
    architecture: dict[str, dict[str, object]] = {}
    for package in packages:
        segments = package.split(".")
        for index, segment in enumerate(segments):
            detected = architecture_segment(segment)
            if detected is None:
                continue
            canonical_name, source_kind = detected
            prefix = ".".join(segments[: index + 1])
            files, sources = subtree_details(packages, prefix)
            main_files = {path for path in files if path.startswith("src/main/")}
            test_files = {path for path in files if path.startswith("src/test/")}
            architecture.setdefault(
                prefix,
                {
                    "segment": segment,
                    "canonical_name": canonical_name,
                    "source_kind": source_kind,
                    "target": canonical_name,
                    "class_count": len(main_files) if main_files else len(test_files),
                    "class_counts": {
                        "main": len(main_files),
                        "test": len(test_files),
                    },
                    "sources": sources,
                    "files": files,
                },
            )

    return {
        package: {
            "segment": entry["segment"],
            "canonical_name": entry["canonical_name"],
            "source_kind": entry["source_kind"],
            "target": entry["target"],
            "class_count": entry["class_count"],
            "class_counts": entry["class_counts"],
            "sources": sorted(entry["sources"]),
            "files": sorted(entry["files"]),
        }
        for package, entry in sorted(architecture.items())
    }


def changed_entries(
    architecture: dict[str, dict[str, object]],
    predicate,
) -> dict[str, dict[str, object]]:
    return {
        package: entry
        for package, entry in architecture.items()
        if entry["segment"] != entry["target"] and predicate(entry)
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".", help="Java project root")
    parser.add_argument(
        "--source-root",
        action="append",
        dest="source_roots",
        default=None,
        help="Source root relative to project root; may be repeated",
    )
    args = parser.parse_args()
    source_roots = args.source_roots or ["src/main/java", "src/test/java"]
    packages = scan(Path(args.root).resolve(), source_roots)
    architecture = scan_architecture(packages)
    print(
        json.dumps(
            {
                "packages": packages,
                "architecture": architecture,
                "spanish_architecture": changed_entries(
                    architecture,
                    lambda entry: entry["source_kind"] == "spanish",
                ),
                "singular_architecture": changed_entries(
                    architecture,
                    lambda entry: entry["source_kind"] == "english_singular",
                ),
                "fixed_architecture": changed_entries(
                    architecture,
                    lambda entry: entry["source_kind"] == "fixed_singular",
                ),
                "conforming_architecture": {
                    package: entry
                    for package, entry in architecture.items()
                    if entry["segment"] == entry["target"]
                },
                "changes": {
                    package: entry
                    for package, entry in architecture.items()
                    if entry["segment"] != entry["target"]
                },
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
