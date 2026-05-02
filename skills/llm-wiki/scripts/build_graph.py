#!/usr/bin/env python3
"""
build_graph.py — LLM Wiki Knowledge Graph Builder

Three-layer edge architecture:
  Layer 1: Parse all [[wikilinks]] in wiki pages → EXTRACTED edges
  Layer 2: Same-directory co-occurrence + shared tags → TOPIC edges
  Layer 3: Call Claude to infer implicit semantic relations → INFERRED edges

Supports SHA256 caching, only processes changed pages.
Output: graph/graph.json + graph/graph.html (vis.js self-contained)

Usage:
  python build_graph.py              # EXTRACTED + TOPIC (default, no API needed)
  python build_graph.py --infer      # + INFERRED (requires ANTHROPIC_API_KEY)
  python build_graph.py --no-topic   # EXTRACTED only (legacy mode)
  python build_graph.py --open       # Open browser after build
"""

import argparse
import hashlib
import json
import os
import re
import sys
import webbrowser
from datetime import date
from pathlib import Path

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

try:
    import community as community_louvain
    import networkx as nx
    HAS_NX = True
except ImportError:
    HAS_NX = False

GRAPH_DIR = Path("graph")
CACHE_FILE = GRAPH_DIR / ".graph_cache.json"
GRAPH_JSON = GRAPH_DIR / "graph.json"
GRAPH_HTML = GRAPH_DIR / "graph.html"
LOG_FILE   = Path("log.md")
TEMPLATE_FILE = Path(__file__).parent.parent / "templates" / "wiki-graph-template.html"

PAGE_DIRS = [
    Path("sources"),
    Path("entities"),
    Path("concepts"),
    Path("comparisons"),
    Path("queries"),
    Path("archive"),
]

NODE_COLORS = {
    "source":     "#4A90D9",
    "entity":     "#E8A838",
    "concept":    "#5BA85A",
    "comparison": "#E74C3C",
    "query":      "#1ABC9C",
}

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+?)(?:\|[^\]]+?)?\]\]")
FRONTMATTER_RE = re.compile(r"^---\n(.+?)\n---", re.DOTALL)
TITLE_RE = re.compile(r'^title:\s*["\']?(.+?)["\']?\s*$', re.MULTILINE)
TYPE_RE  = re.compile(r'^type:\s*(\S+)',  re.MULTILINE)
TAGS_RE  = re.compile(r'^tags:\s*\[([^\]]*)\]', re.MULTILINE)


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def slug_to_id(path: Path) -> str:
    return path.as_posix()


def parse_frontmatter(content: str) -> dict:
    m = FRONTMATTER_RE.match(content)
    if not m:
        return {}
    fm = m.group(1)
    title = TITLE_RE.search(fm)
    typ   = TYPE_RE.search(fm)
    tags_m = TAGS_RE.search(fm)
    tags = []
    if tags_m:
        tags = [t.strip().strip("'\"") for t in tags_m.group(1).split(",") if t.strip()]
    return {
        "title": title.group(1).strip() if title else None,
        "type":  typ.group(1).strip()   if typ   else "source",
        "tags":  tags,
    }


def collect_pages() -> list[Path]:
    skip = {"index.md", "log.md", "overview.md", "lint-report.md"}
    seen_stems = set()
    pages = []
    for d in PAGE_DIRS:
        if d.exists():
            for p in d.rglob("*.md"):
                if p.name not in skip and p.stem not in seen_stems:
                    seen_stems.add(p.stem)
                    pages.append(p)
    return pages


def extract_wikilinks(content: str) -> list[str]:
    return WIKILINK_RE.findall(content)


def resolve_link(link_text: str, all_page_labels: dict[str, str]) -> str | None:
    for pid, label in all_page_labels.items():
        if label.lower() == link_text.lower():
            return pid
    for subdir in ("entities", "concepts", "comparisons", "queries", "sources", "archive"):
        guess = Path(subdir) / f"{link_text}.md"
        if guess.exists():
            return slug_to_id(guess)
    return None


def build_extracted_edges(pages: list[Path]) -> tuple[dict, list[dict]]:
    nodes_map: dict[str, dict] = {}
    raw_edges: list[tuple[str, str]] = []

    for p in pages:
        content = p.read_text(encoding="utf-8")
        fm = parse_frontmatter(content)
        pid = slug_to_id(p)
        nodes_map[pid] = {
            "id":           pid,
            "label":        fm.get("title") or p.stem,
            "type":         fm.get("type",  "source"),
            "tags":         fm.get("tags", []),
            "content_hash": sha256(content),
        }
        for link in extract_wikilinks(content):
            raw_edges.append((pid, link))

    label_map = {pid: n["label"] for pid, n in nodes_map.items()}
    edges: list[dict] = []
    for src, link_text in raw_edges:
        tgt = resolve_link(link_text, label_map)
        if tgt and tgt in nodes_map and tgt != src:
            edges.append({"source": src, "target": tgt, "type": "EXTRACTED"})

    return nodes_map, edges


def build_topic_edges(nodes_map: dict, extracted_edges: list[dict]) -> list[dict]:
    existing_pairs = set()
    for e in extracted_edges:
        pair = tuple(sorted([e["source"], e["target"]]))
        existing_pairs.add(pair)

    topic_edges: list[dict] = []

    dir_groups: dict[str, list[str]] = {}
    for pid in nodes_map:
        parts = pid.split("/")
        if len(parts) >= 2:
            dir_name = parts[0]
            dir_groups.setdefault(dir_name, []).append(pid)

    for dir_name, pids in dir_groups.items():
        if len(pids) <= 1:
            continue
        max_edges = min(10, len(pids) * 2)
        count = 0
        for i in range(len(pids)):
            if count >= max_edges:
                break
            for j in range(i + 1, len(pids)):
                if count >= max_edges:
                    break
                pair = tuple(sorted([pids[i], pids[j]]))
                if pair not in existing_pairs:
                    topic_edges.append({
                        "source": pids[i],
                        "target": pids[j],
                        "type": "TOPIC",
                        "label": f"same {dir_name}",
                    })
                    existing_pairs.add(pair)
                    count += 1

    tag_groups: dict[str, list[str]] = {}
    for pid, node in nodes_map.items():
        for tag in node.get("tags", []):
            tag_groups.setdefault(tag, []).append(pid)

    for tag, pids in tag_groups.items():
        if len(pids) < 2 or len(pids) > 10:
            continue
        for i in range(len(pids)):
            for j in range(i + 1, min(i + 4, len(pids))):
                pair = tuple(sorted([pids[i], pids[j]]))
                if pair not in existing_pairs:
                    topic_edges.append({
                        "source": pids[i],
                        "target": pids[j],
                        "type": "TOPIC",
                        "label": f"shared tag: {tag}",
                    })
                    existing_pairs.add(pair)

    return topic_edges


INFER_PROMPT = """You are analyzing a wiki knowledge base. Given a list of wiki pages and their types,
identify implicit semantic relationships that are NOT already captured by explicit wikilinks or topic co-occurrence.

For each relationship found, output JSON array entries:
{{"source": "<page_id>", "target": "<page_id>", "label": "<short relationship>", "confidence": 0.0-1.0}}

Only include confidence >= 0.6. Output ONLY a valid JSON array, nothing else.

Pages:
{pages_json}
"""


def infer_edges(nodes_map: dict, do_infer: bool, cache: dict, existing_pairs: set) -> list[dict]:
    if not do_infer or not HAS_ANTHROPIC:
        return []

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("⚠  ANTHROPIC_API_KEY not set — skipping inference pass", file=sys.stderr)
        return []

    changed_ids = [
        pid for pid, n in nodes_map.items()
        if cache.get(pid) != n["content_hash"]
    ]
    if not changed_ids:
        print("✓ No changed pages — reusing cached inferred edges")
        return cache.get("inferred_edges", [])

    pages_json = json.dumps(
        [{"id": pid, "label": nodes_map[pid]["label"], "type": nodes_map[pid]["type"]}
         for pid in list(nodes_map)[:80]],
        ensure_ascii=False,
        indent=2
    )

    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        messages=[{"role": "user", "content": INFER_PROMPT.format(pages_json=pages_json)}],
    )
    raw = msg.content[0].text.strip()
    raw = re.sub(r"^```json\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)

    try:
        inferred = json.loads(raw)
    except json.JSONDecodeError:
        print("⚠  Could not parse inferred edges JSON", file=sys.stderr)
        return []

    edges = [
        {
            "source":     e["source"],
            "target":     e["target"],
            "type":       "INFERRED",
            "label":      e.get("label", ""),
            "confidence": e.get("confidence", 0.7),
        }
        for e in inferred
        if e.get("source") in nodes_map and e.get("target") in nodes_map
        and e.get("confidence", 0) >= 0.6
        and tuple(sorted([e["source"], e["target"]])) not in existing_pairs
    ]
    return edges


def detect_communities(nodes_map: dict, edges: list[dict]) -> dict[str, int]:
    if not HAS_NX:
        return {pid: 0 for pid in nodes_map}

    G = nx.Graph()
    for pid in nodes_map:
        G.add_node(pid)
    for e in edges:
        G.add_edge(e["source"], e["target"])

    partition = community_louvain.best_partition(G)
    return partition


def main():
    parser = argparse.ArgumentParser(description="Build wiki knowledge graph")
    parser.add_argument("--infer", action="store_true",
                        help="Enable AI inference pass (requires ANTHROPIC_API_KEY)")
    parser.add_argument("--no-topic", action="store_true",
                        help="Skip topic co-occurrence edges (legacy mode)")
    parser.add_argument("--open", action="store_true",
                        help="Open graph.html in browser after build")
    args = parser.parse_args()

    GRAPH_DIR.mkdir(exist_ok=True)

    cache: dict = {}
    if CACHE_FILE.exists():
        try:
            cache = json.loads(CACHE_FILE.read_text())
        except Exception:
            pass

    pages = collect_pages()
    if not pages:
        print("No wiki pages found. Run wiki-ingest first.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(pages)} wiki pages")

    nodes_map, extracted_edges = build_extracted_edges(pages)
    print(f"Layer 1: {len(extracted_edges)} extracted edges")

    topic_edges = []
    if not args.no_topic:
        topic_edges = build_topic_edges(nodes_map, extracted_edges)
        print(f"Layer 2: {len(topic_edges)} topic edges")

    existing_pairs = set()
    for e in extracted_edges + topic_edges:
        existing_pairs.add(tuple(sorted([e["source"], e["target"]])))

    inferred_edges = infer_edges(nodes_map, args.infer, cache, existing_pairs)
    print(f"Layer 3: {len(inferred_edges)} inferred edges")

    all_edges = extracted_edges + topic_edges + inferred_edges

    partition = detect_communities(nodes_map, all_edges)

    degree: dict[str, int] = {pid: 0 for pid in nodes_map}
    for e in all_edges:
        degree[e["source"]] = degree.get(e["source"], 0) + 1
        degree[e["target"]] = degree.get(e["target"], 0) + 1

    nodes_out = [
        {
            "id":        n["id"],
            "label":     n["label"],
            "type":      n["type"],
            "community": partition.get(n["id"], 0),
            "degree":    degree.get(n["id"], 0),
        }
        for n in nodes_map.values()
    ]

    graph_data = {
        "build_date": str(date.today()),
        "nodes":      nodes_out,
        "edges":      all_edges,
    }

    GRAPH_JSON.write_text(json.dumps(graph_data, ensure_ascii=False, indent=2))
    print(f"Written {GRAPH_JSON}")

    template = TEMPLATE_FILE.read_text(encoding="utf-8")
    html = template.replace("/* GRAPH_JSON_PLACEHOLDER */", json.dumps(graph_data, ensure_ascii=False))
    GRAPH_HTML.write_text(html, encoding="utf-8")
    print(f"Written {GRAPH_HTML}")

    new_cache = {pid: n["content_hash"] for pid, n in nodes_map.items()}
    new_cache["inferred_edges"] = inferred_edges
    CACHE_FILE.write_text(json.dumps(new_cache, indent=2))

    log_path = LOG_FILE
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_entry = f"\n## [{date.today()}] graph | Knowledge graph rebuilt — {len(nodes_out)} nodes, {len(all_edges)} edges\n"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(log_entry)

    top_hubs = sorted(nodes_out, key=lambda n: n["degree"], reverse=True)[:5]
    print("\n=== Graph Stats ===")
    print(f"Nodes: {len(nodes_out)}")
    print(f"Edges: {len(all_edges)} (extracted={len(extracted_edges)}, topic={len(topic_edges)}, inferred={len(inferred_edges)})")
    print("Top hub pages:")
    for n in top_hubs:
        print(f"  {n['label']} ({n['type']}) — degree {n['degree']}")

    if args.open:
        webbrowser.open(GRAPH_HTML.resolve().as_uri())


if __name__ == "__main__":
    main()
