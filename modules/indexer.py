"""Indexing and search utilities for the GPT Export & Index tool."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Tuple
from nltk.stem import PorterStemmer
import re
from .legacy_tool_v6_3 import _build_generic_index, search_with_persistent_index

__all__ = [
    "build_index",
    "search",
    "search_with_context",
    "export_results_with_context",
    "nlp_search_with_persistent_index",
    "search_semantic",
    "semantic_search",
]

def build_index(
    folder: str | Path,
    cfg: dict,
    patterns: Iterable[str],
    index_file: str | Path,
    progress_widget,
    is_json: bool,
    existing: dict | None = None,
    tags: list | None = None,
):
    """Thin wrapper around the legacy index builder."""
    return _build_generic_index(folder, cfg, patterns, index_file, progress_widget, is_json, existing, tags)


def search(phrase: str, loaded_index: dict, case_sensitive: bool = False, search_logic: str = "AND"):
    """Search the persistent index and return matched files."""
    return search_with_persistent_index(phrase, loaded_index, case_sensitive, search_logic)


def nlp_search_with_persistent_index(
    search_phrase: str,
    loaded_index: dict,
    case_sensitive: bool = False,
    search_logic: str = "AND",
    similarity_cutoff: float = 0.8,
) -> Tuple[List[tuple], str | None]:
    """Search using fuzzy token matching with ``difflib``."""

    if not loaded_index or not isinstance(loaded_index.get("index"), dict):
        return [], "Index is not loaded or invalid."

    index_tokens_map = loaded_index["index"].get("tokens", {})
    files_id_to_path_map = loaded_index["index"].get("files", {})
    files_id_to_details_map = loaded_index["index"].get("file_details", {})

    indexed_folder = Path(loaded_index.get("metadata", {}).get("indexed_folder_path", "."))

    from difflib import get_close_matches, SequenceMatcher

    terms = search_phrase.split()
    processed = terms if case_sensitive else [t.lower() for t in terms]
    if not processed:
        return [], "No search terms entered."

    token_keys = list(index_tokens_map.keys())
    result_sets = []
    for term in processed:
        candidates = set(get_close_matches(term, token_keys, n=5, cutoff=similarity_cutoff))
        if term not in candidates:
            candidates.add(term)
        term_file_ids: set[str] = set()
        for cand in candidates:
            key = cand if case_sensitive else cand.lower()
            if key in index_tokens_map:
                term_file_ids.update(index_tokens_map[key])

        for fid, details in files_id_to_details_map.items():
            fname = details.get("filename", "")
            comp = fname if case_sensitive else fname.lower()
            if SequenceMatcher(None, term, comp).ratio() >= similarity_cutoff:
                term_file_ids.add(fid)

        if not term_file_ids and search_logic == "AND":
            return [], f"Term '{term}' yields no results with AND logic."
        result_sets.append(term_file_ids)

    if not result_sets:
        return [], "No documents found for any search terms."

    file_ids = set.intersection(*result_sets) if search_logic == "AND" else set.union(*result_sets)
    if not file_ids:
        return [], "Tokens found, but no single document satisfies the search logic."

    results: List[tuple] = []
    for fid in file_ids:
        rel = files_id_to_path_map.get(fid)
        details = files_id_to_details_map.get(fid, {})
        if not rel:
            continue
        full_path = indexed_folder / rel
        display = details.get("filename", Path(rel).name)
        start = details.get("chat_started_at", "")
        end = details.get("chat_ended_at", "")
        results.append((display, start, end, full_path, fid, details))

    return sorted(results, key=lambda x: x[0].lower()), None

def _extract_snippets(
    file_path: Path, phrase: str, context_lines: int = 1, case_sensitive: bool = False
) -> List[str]:
    """Return text snippets around matches of *phrase* in *file_path*."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception:
        return []

    search_term = phrase if case_sensitive else phrase.lower()
    snippets: List[str] = []
    for idx, line in enumerate(lines):
        check = line if case_sensitive else line.lower()
        if search_term in check:
            start = max(0, idx - context_lines)
            end = min(len(lines), idx + context_lines + 1)
            snippets.append("".join(lines[start:end]).strip())
    return snippets


def search_with_context(
    phrase: str,
    loaded_index: dict,
    *,
    context_lines: int = 1,
    case_sensitive: bool = False,
    search_logic: str = "AND",
    use_nlp: bool = False,
) -> Tuple[List[tuple], str | None]:
    """Search and also collect context snippets from each matching file."""
    search_fn = (
        nlp_search_with_persistent_index if use_nlp else search_with_persistent_index
    )

    search_fn = nlp_search_with_persistent_index if use_nlp else search_with_persistent_index
    results, err = search_fn(phrase, loaded_index, case_sensitive, search_logic)
    if err:
        return [], err

    results_with_ctx = []
    for display, start, end, path_obj, fid, details in results:
        snippets = _extract_snippets(path_obj, phrase, context_lines, case_sensitive)
        results_with_ctx.append((display, start, end, path_obj, snippets, fid, details))

    return results_with_ctx, None


def export_results_with_context(
    phrase: str,
    loaded_index: dict,
    output_file: str | Path,
    *,
    context_lines: int = 1,
    case_sensitive: bool = False,
    search_logic: str = "AND",
    use_nlp: bool = False,
) -> str | None:
    """Search the index and write results with context to ``output_file``."""

    results, err = search_with_context(
        phrase,
        loaded_index,
        context_lines=context_lines,
        case_sensitive=case_sensitive,
        search_logic=search_logic,
        use_nlp=use_nlp,
    )
    if err:
        return err

    out_path = Path(output_file)
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            for display, start, end, path_obj, snippets, _fid, _details in results:
                f.write(f"FILE: {display}\n")
                if start or end:
                    f.write(f"TIME: {start} - {end}\n")
                for snip in snippets:
                    f.write(snip + "\n---\n")
                f.write("\n")
        return None
    except Exception as exc:  # pragma: no cover - hard to trigger in tests
        return str(exc)


_stemmer = PorterStemmer()


def _stem(text: str) -> List[str]:
    """Return stemmed tokens for *text* using a simple regex tokenizer."""
    tokens = re.findall(r"\b\w+\b", text.lower())
    return [_stemmer.stem(tok) for tok in tokens]


def search_semantic(query: str, loaded_index: dict, *, threshold: float = 0.1):
    """Perform a simple stem-based semantic search across indexed files."""

    folder = Path(loaded_index["metadata"]["indexed_folder_path"])
    files = loaded_index["index"]["files"]
    details_map = loaded_index["index"].get("file_details", {})

    query_stems = set(_stem(query))
    if not query_stems:
        return [], "Query produced no searchable tokens"

    results = []
    for fid, name in files.items():
        path_obj = folder / name
        try:
            text = path_obj.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        doc_stems = set(_stem(text))
        if not doc_stems:
            continue

        score = len(query_stems & doc_stems) / len(query_stems)
        if score >= threshold:
            results.append((name, path_obj, score, fid, details_map.get(fid)))

    results.sort(key=lambda x: x[2], reverse=True)
    return results, None

def semantic_search(
    query: str,
    loaded_index: dict,
    *,
    top_n: int = 5,
    context_lines: int = 1,
) -> Tuple[List[tuple], str | None]:
    """Return top-N files most similar to *query* using stem overlap."""

    ranked, err = search_semantic(query, loaded_index, threshold=0.0)
    if err:
        return [], err

    results = []
    for name, path, _score, fid, details in ranked[:top_n]:
        snippets = _extract_snippets(path, query, context_lines, False)
        results.append(
            (
                details.get("filename", path.name),
                details.get("chat_started_at", ""),
                details.get("chat_ended_at", ""),
                path,
                snippets,
                fid,
                details,
            )
        )
    return results, None
