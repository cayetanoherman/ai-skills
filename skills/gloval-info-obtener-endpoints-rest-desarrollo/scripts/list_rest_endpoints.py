#!/usr/bin/env python3
"""List common Java REST mappings as development URLs.

This is a lightweight static aid for the skill. It deliberately does not
contact the target environment or inspect Git metadata.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


MAPPING_METHODS = {
    "GetMapping": "GET",
    "PostMapping": "POST",
    "PutMapping": "PUT",
    "PatchMapping": "PATCH",
    "DeleteMapping": "DELETE",
    "HeadMapping": "HEAD",
    "OptionsMapping": "OPTIONS",
}

PARAM_ANNOTATIONS = {
    "PathVariable": "path",
    "RequestParam": "query",
    "RequestHeader": "header",
    "CookieValue": "cookie",
    "RequestBody": "body",
    "ModelAttribute": "form",
}

HTTP_METHOD_PRIORITY = {
    "GET": 0,
    "POST": 1,
}


@dataclass(frozen=True)
class Endpoint:
    method: str
    path: str
    parameters: str


def strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//.*", "", text)


def annotation_body(text: str, start: int) -> tuple[str, int]:
    """Return annotation arguments and the index after the annotation."""
    open_index = text.find("(", start)
    if open_index == -1:
        return "", start

    depth = 0
    quote = False
    escaped = False
    for index in range(open_index, len(text)):
        char = text[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quote = False
            continue
        if char == '"':
            quote = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return text[open_index + 1 : index], index + 1
    return text[open_index + 1 :], len(text)


def quoted_values(expression: str) -> list[str]:
    return [value.replace('\\"', '"') for value in re.findall(r'"((?:\\.|[^"\\])*)"', expression)]


def mapping_paths(body: str) -> list[str]:
    named = re.search(r"(?:value|path)\s*=\s*(\{.*?\}|\"(?:\\.|[^\"])*\")", body, flags=re.S)
    values = quoted_values(named.group(1)) if named else quoted_values(body)
    return values or [""]


def mapping_methods(name: str, body: str) -> list[str]:
    if name != "RequestMapping":
        return [MAPPING_METHODS[name]]
    methods = re.findall(r"RequestMethod\.([A-Z]+)", body)
    return methods or ["ANY"]


def join_paths(*parts: str) -> str:
    values = [part.strip("/") for part in parts if part.strip("/")]
    return "/" + "/".join(values)


def split_parameters(text: str) -> list[str]:
    result: list[str] = []
    start = 0
    depth = 0
    quote = False
    for index, char in enumerate(text):
        if char == '"':
            quote = not quote
        elif not quote and char in "<([{":
            depth += 1
        elif not quote and char in ">)]}":
            depth = max(0, depth - 1)
        elif not quote and char == "," and depth == 0:
            result.append(text[start:index].strip())
            start = index + 1
    tail = text[start:].strip()
    if tail:
        result.append(tail)
    return result


def parameter_description(parameter_text: str) -> str | None:
    annotation = re.search(r"@(PathVariable|RequestParam|RequestHeader|CookieValue|RequestBody|ModelAttribute)\b", parameter_text)
    if not annotation:
        return None

    kind = PARAM_ANNOTATIONS[annotation.group(1)]
    annotation_body_text, _ = annotation_body(parameter_text, annotation.start())
    explicit_name = re.search(r"(?:name|value)\s*=\s*\"([^\"]+)\"", annotation_body_text)
    quoted = quoted_values(annotation_body_text)
    name = explicit_name.group(1) if explicit_name else (quoted[0] if quoted else None)

    without_annotations = re.sub(r"@\w+(?:\([^)]*\))?", " ", parameter_text, flags=re.S).strip()
    tokens = re.findall(r"[A-Za-z_$][\w$]*", without_annotations)
    parameter_name = tokens[-1] if tokens else "?"
    parameter_type = " ".join(tokens[:-1]) if len(tokens) > 1 else "?"

    if kind == "body":
        return f"body {parameter_name}: {parameter_type}"
    label = name or parameter_name
    return f"{kind} {label}: {parameter_type}"


def method_signature(text: str, start: int) -> tuple[str, str] | None:
    tail = text[start : start + 5000]
    match = re.search(
        r"\b(?:public|protected|private)\s+(?:static\s+|final\s+|synchronized\s+|default\s+)*[^;{}()]+?\s+(\w+)\s*\(([^()]*)\)",
        tail,
        flags=re.S,
    )
    if not match:
        return None
    return match.group(1), match.group(2)


def context_path(root: Path) -> str:
    preferred = root / "src/main/resources/application.properties"
    files = [preferred] if preferred.exists() else sorted(root.rglob("application*.properties"))
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        match = re.search(r"^\s*server\.servlet\.context-path\s*=\s*(\S+)\s*$", text, flags=re.M)
        if match:
            value = match.group(1).strip().strip("/")
            return f"/{value}" if value else ""
    return ""


def parse_file(path: Path) -> list[tuple[str, str, str, str]]:
    text = strip_comments(path.read_text(encoding="utf-8", errors="replace"))
    class_match = re.search(r"\bclass\s+\w+", text)
    if not class_match:
        return []

    before_class = text[: class_match.start()]
    rest_controller = bool(re.search(r"@RestController\b", before_class))
    controller = bool(re.search(r"@Controller\b", before_class))
    class_response_body = bool(re.search(r"@ResponseBody\b", before_class))
    if not rest_controller and not controller:
        return []

    class_mapping = ""
    annotations_before_class = list(re.finditer(r"@(RequestMapping)\b", before_class))
    if annotations_before_class:
        annotation = annotations_before_class[-1]
        body, _ = annotation_body(before_class, annotation.start())
        class_mapping = mapping_paths(body)[0]

    result: list[tuple[str, str, str, str]] = []
    after_class = text[class_match.end() :]
    for match in re.finditer(
        r"@(RequestMapping|GetMapping|PostMapping|PutMapping|PatchMapping|DeleteMapping|HeadMapping|OptionsMapping)\b",
        after_class,
    ):
        absolute_start = class_match.end() + match.start()
        body, annotation_end = annotation_body(text, absolute_start)
        signature = method_signature(text, annotation_end)
        if not signature:
            continue
        method_name, parameter_text = signature
        if not rest_controller and not class_response_body and "@ResponseBody" not in text[absolute_start : annotation_end + 200]:
            continue

        descriptions = [parameter_description(parameter) for parameter in split_parameters(parameter_text)]
        descriptions = [description for description in descriptions if description]
        parameters = ", ".join(descriptions) if descriptions else "ninguno"
        for http_method in mapping_methods(match.group(1), body):
            for path_value in mapping_paths(body):
                result.append((http_method, join_paths(class_mapping, path_value), parameters, method_name))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--port", required=True)
    parser.add_argument("--source", action="append", default=["src/main"])
    parser.add_argument("--context-path", default=None)
    args = parser.parse_args()

    if not args.port.isdigit() or not 1 <= int(args.port) <= 65535:
        parser.error("port must be an integer between 1 and 65535")

    root = args.root.resolve()
    base = f"http://devnext.gloval.internal:{args.port}"
    prefix = args.context_path if args.context_path is not None else context_path(root)
    prefix = "/" + prefix.strip("/") if prefix.strip("/") else ""

    endpoints: set[Endpoint] = set()
    for source in args.source:
        source_path = root / source
        if not source_path.exists():
            continue
        for java_file in source_path.rglob("*.java"):
            for method, path, parameters, _ in parse_file(java_file):
                endpoints.add(Endpoint(method, f"{base}{prefix}{path}", parameters))

    for endpoint in sorted(
        endpoints,
        key=lambda item: (HTTP_METHOD_PRIORITY.get(item.method, 2), item.method, item.path, item.parameters),
    ):
        print(f"- {endpoint.method} {endpoint.path} — parámetros: {endpoint.parameters}")
    if not endpoints:
        print("Ninguno")


if __name__ == "__main__":
    main()
