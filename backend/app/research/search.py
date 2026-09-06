from typing import Any


def build_structure_summary(structure: Any) -> str:
    return "\n".join(
        [
            f"fields={structure.fields}",
            f"content_format={structure.content_format}",
            f"quote={structure.quote}",
            f"item_indent={repr(structure.item_indent)}",
            f"property_indent={repr(structure.property_indent)}",
            f"semicolon={structure.semicolon}",
        ]
    )
