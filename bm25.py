from pathlib import Path        # Path: an object representing a filesystem location
                                # Replaces string-manipulation of paths with methods.
import re
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

def chunk(docs, min_tokens=30):
    chunks = {}

    for path, text in docs.items():
        # 1. Split the file on heading lines, keeping the headings.
        #    re.split with a capturing group returns:
        #    [preamble, heading1, body1, heading2, body2, ...]
        parts = re.split(r'^(#{1,3} .+)$', text, flags=re.MULTILINE)

        # 2. parts[0] is everything before the first heading (preamble)
        if len(parts[0].split()) >= min_tokens:
            chunks[f"{path}#_preamble"] = parts[0] # key = id, value = text

        # 3. Walk the rest in pairs: heading, then body.
        for i in range(1, len(parts), 2):
            heading = parts[i].lstrip('#').strip() # "## SVD" -> "SVD"
            body = parts[i+1]

            if len(body.split()) < min_tokens:
                continue

            doc_id = f"{path}#{heading}"

            n=2
            while doc_id in chunks:
                doc_id = f"{path}#{heading}-{n}"
                n += 1

            chunks[doc_id] = body
    return chunks

if __name__ == "__main__":
    docs = load(config.CORPUS_PATH)
    chunks = chunk(docs)
    print(f"{len(docs)} documents -> {len(chunks)} chunks")