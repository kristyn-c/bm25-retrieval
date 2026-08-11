from pathlib import Path        # Path: an object representing a filesystem location
                                # Replaces string-manipulation of paths with methods.
import re
from collections import Counter, defaultdict
import math
import config                   # Your gitignored config.py. Reading a .py file as a module
                                # means CORPUS_PATH arrives as a real Python string

def load(corpus_path):
    root = Path(corpus_path)  
    docs = {}                   # The accumulator. Keys = doc ids, values = raw text
    for p in root.rglob("*.md"):
        if any(part.startswith('_') for part in p.relative_to(root).parts[:-1]):
            continue
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
        text = re.sub(r'^---\n.*?\n---\n', '', text, flags=re.DOTALL)
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

def tokenize(text):
    """str -> list of terms"""
    text = text.lower()
    # crude: no stemming, no stopword removal. revisit later
    terms = re.split(r'[^a-z0-9]+', text.lower())

    return [t for t in terms if t]

def build(chunks):
    """{doc_id: text} -> (index, doc_lengths, avgdl, N)"""
    index = defaultdict(list) # term -> [(doc_id, tf), ...]
    doc_lengths = {} # doc_id -> token count
    for doc_id, text in chunks.items():
        tokens = tokenize(text)
        doc_lengths[doc_id] = len(tokens)

        for term, count in Counter(tokens).items():
            index[term].append((doc_id, count))
    N = len(chunks)
    avgdl = sum(doc_lengths.values()) / N

    return index, doc_lengths, avgdl, N

def score(query, index, doc_lengths, avgdl, N, k1=1.5, b=0.75):
    """query string-> {doc_id: bm25 score}"""
    scores = defaultdict(float)

    for term in tokenize(query):
        if term not in index:
            continue
        df = len(index[term])
        idf = math.log((N - df + 0.5) / (df + 0.5) + 1) # smoothed

        for doc_id, tf in index[term]:
            dl = doc_lengths[doc_id]
            num = tf * (k1+1)
            den = tf + k1 * (1 - b + b * dl / avgdl) # length normalization
            scores[doc_id] += idf * num / den # term frequency saturating (diminishing returns)
    return scores

if __name__ == "__main__":
    docs = load(config.CORPUS_PATH)
    chunks = chunk(docs)
    print(f"{len(docs)} documents -> {len(chunks)} chunks")

    sample = list(chunks.values())[0]
    print(tokenize(sample)[:20])

    index, doc_lengths, avgdl, N = build(chunks)
    print(f"{N} docs, {len(index)} terms, avgdl {avgdl:.1f}")
    cf = Counter({t: sum(c for _, c in postings) for t, postings in index.items()})
    print(cf.most_common(10))

    results = score("spectral clustering", index, doc_lengths, avgdl, N)
    for doc_id, s in sorted(results.items(), key= lambda x: -x[1])[:10]:
        print(f"{s:.2f} {doc_id}")