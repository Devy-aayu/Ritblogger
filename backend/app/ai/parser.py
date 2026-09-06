from dataclasses import dataclass
import re


@dataclass
class BlogStructure:
    array_start: int
    array_end: int
    item_indent: str
    property_indent: str
    quote: str
    semicolon: bool
    trailing_comma: bool
    object_sample: dict[str, str]
    fields: list[str]
    content_format: str


def _skip_string(text: str, index: int) -> int:
    quote = text[index]
    index += 1
    while index < len(text):
        if text[index] == "\\":
            index += 2
            continue
        if text[index] == quote:
            return index + 1
        index += 1
    raise ValueError("Unterminated string in JavaScript.")


def _skip_comment(text: str, index: int) -> int:
    if text.startswith("//", index):
        end = text.find("\n", index + 2)
        return len(text) if end == -1 else end
    if text.startswith("/*", index):
        end = text.find("*/", index + 2)
        return len(text) if end == -1 else end + 2
    return index


def _matching(text: str, start: int) -> int:
    pairs = {"[": "]", "{": "}", "(": ")"}
    opening = text[start]
    stack = [opening]
    i = start + 1
    while i < len(text):
        ch = text[i]
        if ch in "\"'`":
            i = _skip_string(text, i)
            continue
        if text.startswith("//", i) or text.startswith("/*", i):
            i = _skip_comment(text, i)
            continue
        if ch in pairs:
            stack.append(ch)
        elif ch in "]} )".replace(" ", ""):
            expected = {"]": "[", "}": "{", ")": "("}[ch]
            if not stack or stack[-1] != expected:
                raise ValueError("Unbalanced JavaScript structure.")
            stack.pop()
            if not stack:
                return i
        i += 1
    raise ValueError("Could not find matching bracket.")


def _find_array(text: str) -> tuple[int, int]:
    patterns = [
        r"(?:export\s+default|export\s+const|const|let|var)\s+\w+\s*=\s*\[",
        r"(?:export\s+default)\s+\[",
    ]
    matches = []
    for pattern in patterns:
        matches.extend(re.finditer(pattern, text))
    if not matches:
        raise ValueError("Could not find a JavaScript array in the blog file.")
    match = min(matches, key=lambda m: m.start())
    start = text.find("[", match.start(), match.end())
    return start, _matching(text, start)


def _top_level_objects(array_text: str, absolute_start: int) -> list[tuple[int, int]]:
    result = []
    i = 0
    while i < len(array_text):
        if array_text[i] in "\"'`":
            i = _skip_string(array_text, i)
            continue
        if array_text.startswith("//", i) or array_text.startswith("/*", i):
            i = _skip_comment(array_text, i)
            continue
        if array_text[i] == "{":
            end = _matching(array_text, i)
            result.append((absolute_start + i, absolute_start + end))
            i = end + 1
            continue
        i += 1
    return result


def _object_fields(obj: str) -> dict[str, str]:
    fields = {}
    pattern = re.compile(
        r"(?:^|,)\s*([A-Za-z_$][\w$]*|['\"][^'\"]+['\"])\s*:\s*",
        re.MULTILINE,
    )
    for match in pattern.finditer(obj):
        key = match.group(1).strip("\"'")
        value_start = match.end()
        i = value_start
        depth = 0
        while i < len(obj):
            if obj[i] in "\"'`":
                i = _skip_string(obj, i)
                continue
            if obj[i] in "[{(":
                depth += 1
            elif obj[i] in "]})":
                if depth == 0:
                    break
                depth -= 1
            elif obj[i] == "," and depth == 0:
                break
            i += 1
        fields[key] = obj[value_start:i].strip()
    return fields


def inspect_blog_file(text: str) -> BlogStructure:
    array_start, array_end = _find_array(text)
    objects = _top_level_objects(
        text[array_start + 1:array_end],
        array_start + 1,
    )
    if not objects:
        raise ValueError("The configured blog array is empty.")
    first_start, first_end = objects[0]
    sample_text = text[first_start:first_end + 1]
    sample = _object_fields(sample_text)

    line_start = text.rfind("\n", 0, first_start) + 1
    item_indent = re.match(r"\s*", text[line_start:first_start]).group(0)

    property_indent = item_indent + "  "
    first_property_match = re.search(
        r"\n(\s+)[A-Za-z_$][\w$]*\s*:",
        sample_text,
    )
    if first_property_match:
        property_indent = first_property_match.group(1)

    quote = "'"
    if re.search(r":\s*\"", sample_text):
        quote = '"'

    content_value = ""
    for key in ("content", "body", "description", "text", "html"):
        if key in sample:
            content_value = sample[key]
            break

    content_format = "markdown"
    if "<h2" in content_value or "<p" in content_value or "</" in content_value:
        content_format = "html"

    tail = text[first_start:first_end + 1].rstrip()
    trailing_comma = tail.endswith(",")
    semicolon = bool(re.search(r"\]\s*;\s*$", text[array_end:]))

    return BlogStructure(
        array_start=array_start,
        array_end=array_end,
        item_indent=item_indent,
        property_indent=property_indent,
        quote=quote,
        semicolon=semicolon,
        trailing_comma=trailing_comma,
        object_sample=sample,
        fields=list(sample.keys()),
        content_format=content_format,
    )
