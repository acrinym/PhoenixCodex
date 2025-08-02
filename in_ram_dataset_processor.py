import os
from pathlib import Path
from multiprocessing import Pool, cpu_count
from tempfile import SpooledTemporaryFile
import orjson

# Worker function to process a single file's content
# and produce an AmandaMap/PhoenixCodex-style entry.
# In a real system, replace the placeholder logic below
# with full parsing and metadata extraction.
def _process_file(args):
    idx, path_str, content = args
    entry = {
        "source": os.path.basename(path_str),
        "content": content.strip(),
    }
    return idx, entry


def process_directory(input_dir: str, output_file: str = "AmandaMap_PhoenixCodex_Output.json", num_workers: int | None = None) -> None:
    """Process all files in input_dir into a single JSON output using in-RAM batching.

    Args:
        input_dir: Directory containing input text/JSON files.
        output_file: Final JSON file written once after all processing.
        num_workers: Number of parallel processes; defaults to CPU count - 1.
    """
    input_path = Path(input_dir)
    file_paths = [p for p in input_path.glob("**/*") if p.is_file()]

    # Load all files into RAM first
    files_in_memory = []
    for idx, path in enumerate(file_paths):
        with path.open("r", encoding="utf-8") as f:
            files_in_memory.append((idx, str(path), f.read()))

    if num_workers is None:
        num_workers = max(1, cpu_count() - 1)

    # Temporary JSON storage entirely in RAM
    with SpooledTemporaryFile(max_size=1024 * 1024 * 100, mode="w+b") as tmpfile:  # 100MB before spooling to disk
        with Pool(processes=num_workers) as pool:
            # Process files in parallel and write results incrementally
            for idx, entry in pool.imap_unordered(_process_file, files_in_memory):
                tmpfile.write(orjson.dumps(entry))
                tmpfile.write(b"\n")
                files_in_memory[idx] = None  # Release memory for processed file

        # Flush once to final JSON array on disk
        tmpfile.seek(0)
        with open(output_file, "wb") as out:
            out.write(b"[")
            first = True
            for line in tmpfile:
                if not first:
                    out.write(b",")
                else:
                    first = False
                out.write(line.strip())
            out.write(b"]")


def _create_dummy_files(directory: Path) -> None:
    """Create small text files for example usage."""
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "file1.txt").write_text("Hello from file 1\n", encoding="utf-8")
    (directory / "file2.txt").write_text("Greetings from file 2\n", encoding="utf-8")
    (directory / "file3.txt").write_text("Another line from file 3\n", encoding="utf-8")


if __name__ == "__main__":
    # Example usage with dummy files
    dummy_dir = Path("dummy_input")
    _create_dummy_files(dummy_dir)
    process_directory(dummy_dir, "AmandaMap_PhoenixCodex_Output.json", num_workers=2)
    print("Processing complete. Output saved to AmandaMap_PhoenixCodex_Output.json")
