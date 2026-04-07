import tree_sitter_python as tspython
from tree_sitter import Language, Parser

PY_LANGUAGE = Language(tspython.language())


def chunk_python_file(source: str, file_path: str) -> list[dict]:
    """Parse Python source and return chunks per function/class."""
    parser = Parser(PY_LANGUAGE)
    tree = parser.parse(source.encode())
    chunks = []

    for node in tree.root_node.children:
        if node.type in ("function_definition", "class_definition"):
            chunk_text = source[node.start_byte : node.end_byte]
            chunks.append(
                {
                    "content": chunk_text,
                    "chunk_type": "function" if node.type == "function_definition" else "class",
                    "file_path": file_path,
                    "start_line": node.start_point[0] + 1,
                    "end_line": node.end_point[0] + 1,
                }
            )

    if not chunks:
        chunks.append(
            {
                "content": source,
                "chunk_type": "module",
                "file_path": file_path,
                "start_line": 1,
                "end_line": source.count("\n") + 1,
            }
        )

    return chunks


def chunk_markdown(content: str, file_path: str) -> list[dict]:
    """Split markdown by headings into semantic chunks."""
    chunks = []
    current_chunk: list[str] = []
    current_start = 1

    for i, line in enumerate(content.split("\n"), 1):
        if line.startswith("#") and current_chunk:
            chunks.append(
                {
                    "content": "\n".join(current_chunk),
                    "chunk_type": "doc_section",
                    "file_path": file_path,
                    "start_line": current_start,
                    "end_line": i - 1,
                }
            )
            current_chunk = [line]
            current_start = i
        else:
            current_chunk.append(line)

    if current_chunk:
        chunks.append(
            {
                "content": "\n".join(current_chunk),
                "chunk_type": "doc_section",
                "file_path": file_path,
                "start_line": current_start,
                "end_line": current_start + len(current_chunk) - 1,
            }
        )

    return chunks
