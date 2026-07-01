import gzip
import json
import os

def load_candidates(filepath):
    """
    Generator that yields parsed candidate dictionaries from a .jsonl or .jsonl.gz file.
    Also supports standard .json arrays for the sample.
    """
    if filepath.endswith('.json'):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    yield item
            else:
                yield data
        return

    if filepath.endswith('.gz'):
        open_fn = lambda f: gzip.open(f, 'rt', encoding='utf-8')
    else:
        open_fn = lambda f: open(f, 'r', encoding='utf-8')
        
    with open_fn(filepath) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)

def build_candidate_document(candidate):
    """
    Creates a single text document representing the candidate for BM25/Semantic search.
    """
    doc_parts = []
    
    # Title
    if 'current_title' in candidate and candidate['current_title']:
        doc_parts.append(f"Title: {candidate['current_title']}")
        
    # Skills
    if 'skills' in candidate and isinstance(candidate['skills'], list):
        skills = [s.get('skill_name', '') for s in candidate['skills'] if isinstance(s, dict)]
        doc_parts.append(f"Skills: {', '.join(skills)}")
        
    # Experience
    if 'experience' in candidate and isinstance(candidate['experience'], list):
        for exp in candidate['experience']:
            if isinstance(exp, dict):
                title = exp.get('title', '')
                desc = exp.get('description', '')
                if title or desc:
                    doc_parts.append(f"Experience: {title}. {desc}")
                    
    return " ".join(doc_parts)
