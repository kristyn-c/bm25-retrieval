from pathlib import Path        # Path: an object representing a filesystem location
                                # Replaces string-manipulation of paths with methods.
import config                   # Your gitignored config.py. Reading a .py file as a module
                                # means CORPUS_PATH arrives as a real Python string

def load(corpus_path):
    root = Path(corpus_path)  
    docs = {}                   # The accumulator. Keys = doc ids, values = raw text
    for p in root.rglob("*.md"):
        try:
            text = p.read_text(encoding="utf-8") # the value
        except Exception as e:
            print(f"skipped {p}: {e}")
            continue
        doc_id = str(p.relative_to(root))   # the key
        docs[doc_id] = text                 #store the pair
    return docs

if __name__ == "__main__":
    docs = load(config.CORPUS_PATH)
    print(f"{len(docs)} documents loaded")