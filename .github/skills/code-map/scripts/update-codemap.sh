#!/usr/bin/env bash
set -euo pipefail

SCOPE="${1:-src}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"

OUT_ROOT="$REPO_ROOT/artifacts/code-map"
TS="$(date +%Y%m%d-%H%M%S)"
RUN_DIR="$OUT_ROOT/history/$TS"
LATEST_DIR="$OUT_ROOT/latest"

EFFECTIVE_SCOPE="src"
if [[ "$SCOPE" != "src" && "$SCOPE" != "./src" ]]; then
  echo "INFO: force scope to src/ (requested: $SCOPE)"
fi

if [[ ! -d "$REPO_ROOT/$EFFECTIVE_SCOPE" ]]; then
  echo "ERROR: scope directory not found: $EFFECTIVE_SCOPE"
  exit 1
fi

mkdir -p "$RUN_DIR" "$LATEST_DIR"

STRUCTURE_FILE="$RUN_DIR/structure-map.txt"
LANG_STATS_FILE="$RUN_DIR/language-stats.txt"
PY_IMPORTS_FILE="$RUN_DIR/imports-python.txt"
TSJS_IMPORTS_FILE="$RUN_DIR/imports-tsjs.txt"
CONTEXT_FILE="$RUN_DIR/context-cards.md"
IMPACT_FILE="$RUN_DIR/impact-analysis.md"
TRACK_FILE="$RUN_DIR/change-tracking.md"
MANIFEST_FILE="$RUN_DIR/manifest.json"
SEMANTIC_CORPUS_FILE="$RUN_DIR/semantic-corpus.jsonl"
SEMANTIC_VECTORS_FILE="$RUN_DIR/semantic-vectors.jsonl"
SEMANTIC_STANDARD_FILE="$RUN_DIR/semantic-standard.json"

PREV_STRUCTURE="$LATEST_DIR/structure-map.txt"

generate_structure() {
  if command -v rg >/dev/null 2>&1; then
    (
      cd "$REPO_ROOT"
      rg --files "$EFFECTIVE_SCOPE" 2>/dev/null \
        -g "!artifacts/**" \
        -g "!.git/**" \
        -g "!.venv/**" \
        -g "!venv/**" \
        -g "!.env/**" \
        -g "!env/**" \
        -g "!node_modules/**" \
        -g "!.github/skills/skills-skills/scripts/.venv-skill-seekers/**" \
        | sort > "$STRUCTURE_FILE"
    ) || true
  fi

  if [[ ! -s "$STRUCTURE_FILE" ]]; then
    if [[ "$EFFECTIVE_SCOPE" == "." ]]; then
      (
        cd "$REPO_ROOT"
        find . -type f \
          ! -path "./artifacts/*" \
          ! -path "./.git/*" \
          ! -path "./.venv/*" \
          ! -path "./venv/*" \
          ! -path "./.env/*" \
          ! -path "./env/*" \
          ! -path "./node_modules/*" \
          ! -path "./.github/skills/skills-skills/scripts/.venv-skill-seekers/*" \
          | sed 's#^./##' | sort > "$STRUCTURE_FILE"
      )
    else
      (
        cd "$REPO_ROOT"
        find "$EFFECTIVE_SCOPE" -type f \
          ! -path "*/artifacts/*" \
          ! -path "*/.git/*" \
          ! -path "*/.venv/*" \
          ! -path "*/venv/*" \
          ! -path "*/.env/*" \
          ! -path "*/env/*" \
          ! -path "*/node_modules/*" \
          ! -path "*/.venv-skill-seekers/*" \
          | sed 's#^./##' | sort > "$STRUCTURE_FILE"
      )
    fi
  fi
}

generate_stats() {
  awk -F. '
    NF > 1 { ext = $NF; cnt[ext]++ }
    NF == 1 { cnt["NO_EXT"]++ }
    END { for (e in cnt) printf "%s %d\n", e, cnt[e] }
  ' "$STRUCTURE_FILE" | sort > "$LANG_STATS_FILE"
}

generate_import_scans() {
  if command -v rg >/dev/null 2>&1; then
    (
      cd "$REPO_ROOT"
      rg "^(from |import )" -n "$EFFECTIVE_SCOPE" \
        -g "*.py" \
        -g "!artifacts/**" \
        -g "!.venv/**" \
        -g "!venv/**" \
        -g "!.env/**" \
        -g "!env/**" \
        -g "!.github/skills/skills-skills/scripts/.venv-skill-seekers/**" \
        > "$PY_IMPORTS_FILE"
    ) || true
    (
      cd "$REPO_ROOT"
      rg "^import |require\\(" -n "$EFFECTIVE_SCOPE" \
        -g "*.ts" -g "*.tsx" -g "*.js" -g "*.mjs" -g "*.cjs" \
        -g "!artifacts/**" \
        -g "!.venv/**" \
        -g "!venv/**" \
        -g "!.env/**" \
        -g "!env/**" \
        -g "!.github/skills/skills-skills/scripts/.venv-skill-seekers/**" \
        > "$TSJS_IMPORTS_FILE"
    ) || true
  else
    (
      cd "$REPO_ROOT"
      find "$EFFECTIVE_SCOPE" -type f -name "*.py" \
        ! -path "*/artifacts/*" \
        ! -path "*/.venv/*" \
        ! -path "*/venv/*" \
        ! -path "*/.env/*" \
        ! -path "*/env/*" \
        ! -path "*/.venv-skill-seekers/*" -print0 |
      while IFS= read -r -d '' f; do
        grep -nE "^(from |import )" "$f" || true
      done > "$PY_IMPORTS_FILE"
    ) || true
    (
      cd "$REPO_ROOT"
      find "$EFFECTIVE_SCOPE" -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.mjs" -o -name "*.cjs" \) \
        ! -path "*/artifacts/*" \
        ! -path "*/.venv/*" \
        ! -path "*/venv/*" \
        ! -path "*/.env/*" \
        ! -path "*/env/*" \
        ! -path "*/.venv-skill-seekers/*" -print0 |
      while IFS= read -r -d '' f; do
        grep -nE "^import |require\\(" "$f" || true
      done > "$TSJS_IMPORTS_FILE"
    ) || true
  fi

  [[ -f "$PY_IMPORTS_FILE" ]] || : > "$PY_IMPORTS_FILE"
  [[ -f "$TSJS_IMPORTS_FILE" ]] || : > "$TSJS_IMPORTS_FILE"
}

generate_templates() {
  cat > "$CONTEXT_FILE" <<EOF
# Context Cards

- Module: <name>
- Responsibility: <one sentence>
- Inputs: <public API/params>
- Outputs: <result/side effects>
- Dependencies: <imports/calls>
- Dependents: <callers/importers>
- Risks: <coupling/global state>
- Evidence: <file:line or command>
EOF

  cat > "$IMPACT_FILE" <<EOF
# Impact Analysis

- Change Target: <path or symbol>
- Direct Impact: <direct callers/importers>
- Indirect Impact: <transitive consumers>
- High Risk Paths: <critical flows>
- Suggested Tests: <unit/integration/e2e>
- Rollback Plan: <feature flag/compat mode>
EOF
}

generate_semantic_artifacts() {
  local python_cmd=""
  if command -v python3 >/dev/null 2>&1; then
  python_cmd="python3"
  elif command -v python >/dev/null 2>&1; then
  python_cmd="python"
  else
  echo "ERROR: python/python3 not found, cannot build semantic artifacts"
  exit 1
  fi

  "$python_cmd" - <<'PY' "$STRUCTURE_FILE" "$SEMANTIC_CORPUS_FILE" "$SEMANTIC_VECTORS_FILE" "$SEMANTIC_STANDARD_FILE"
import hashlib
import json
import math
import re
import sys

structure_file, corpus_file, vectors_file, standard_file = sys.argv[1:5]
dim = 256

def tokenize(text: str):
  t = text.lower().replace('\\', '/').replace('_', ' ').replace('-', ' ')
  return [x for x in re.split(r'[^\w\u4e00-\u9fff]+', t) if len(x) >= 2]

def hashed_sparse(tokens):
  buckets = {}
  for tok in tokens:
    idx = int(hashlib.sha1(tok.encode('utf-8')).hexdigest()[:8], 16) % dim
    buckets[idx] = buckets.get(idx, 0.0) + 1.0
  norm = math.sqrt(sum(v * v for v in buckets.values())) or 1.0
  indices = sorted(buckets.keys())
  values = [round(buckets[i] / norm, 6) for i in indices]
  return {"dim": dim, "indices": indices, "values": values}

paths = []
with open(structure_file, 'r', encoding='utf-8') as f:
  for line in f:
    p = line.strip()
    if p:
      paths.append(p)

with open(corpus_file, 'w', encoding='utf-8', newline='\n') as fc, open(vectors_file, 'w', encoding='utf-8', newline='\n') as fv:
  for p in sorted(paths):
    parts = p.split('/')
    title = parts[-1].rsplit('.', 1)[0] if parts else p
    domain = parts[1] if len(parts) >= 2 else 'root'
    ext = parts[-1].rsplit('.', 1)[1] if '.' in parts[-1] else ''
    semantic_text = f"path {p} title {title} domain {domain} extension {ext}"
    tokens = tokenize(semantic_text)
    record_id = 'cm_' + hashlib.sha1(p.encode('utf-8')).hexdigest()[:16]
    corpus = {
      "schema_version": "1.0",
      "id": record_id,
      "type": "file",
      "path": p,
      "title": title,
      "domain": domain,
      "extension": ext,
      "tokens": tokens,
      "text": semantic_text,
      "source": "code-map",
    }
    vector = {
      "schema_version": "1.0",
      "id": record_id,
      "path": p,
      "vector": hashed_sparse(tokens),
    }
    fc.write(json.dumps(corpus, ensure_ascii=False) + "\n")
    fv.write(json.dumps(vector, ensure_ascii=False) + "\n")

standard = {
  "standard_version": "1.0",
  "chunking": {
    "unit": "file",
    "scope": "src",
    "text_template": "path + title + domain + extension",
  },
  "vector": {
    "algorithm": "hashing-tf",
    "dimensions": dim,
    "normalization": "l2",
    "metric": "cosine",
    "tokenizer": "unicode-lower-split-nonalnum",
  },
  "retrieval": {
    "top_k_default": 10,
    "rerank": "none",
  },
}

with open(standard_file, 'w', encoding='utf-8', newline='\n') as fs:
  json.dump(standard, fs, ensure_ascii=False, indent=2)
  fs.write('\n')
PY
}

generate_tracking() {
  if [[ -f "$PREV_STRUCTURE" ]]; then
    PREV_SORTED="$RUN_DIR/.prev-structure.sorted.tmp"
    CURR_SORTED="$RUN_DIR/.curr-structure.sorted.tmp"
    ADDED_TMP="$RUN_DIR/.added.tmp"
    REMOVED_TMP="$RUN_DIR/.removed.tmp"

    sort "$PREV_STRUCTURE" > "$PREV_SORTED"
    sort "$STRUCTURE_FILE" > "$CURR_SORTED"

    comm -13 "$PREV_SORTED" "$CURR_SORTED" > "$ADDED_TMP" || true
    comm -23 "$PREV_SORTED" "$CURR_SORTED" > "$REMOVED_TMP" || true

    ADDED_COUNT=$(wc -l < "$ADDED_TMP" | tr -d ' ')
    REMOVED_COUNT=$(wc -l < "$REMOVED_TMP" | tr -d ' ')

    {
      echo "# Change Tracking"
      echo
      echo "- Scope: $EFFECTIVE_SCOPE"
      echo "- Timestamp: $TS"
      echo "- Added files: $ADDED_COUNT"
      echo "- Removed files: $REMOVED_COUNT"
      echo
      echo "## Added (top 100)"
      head -100 "$ADDED_TMP"
      echo
      echo "## Removed (top 100)"
      head -100 "$REMOVED_TMP"
    } > "$TRACK_FILE"
  else
    {
      echo "# Change Tracking"
      echo
      echo "- Scope: $EFFECTIVE_SCOPE"
      echo "- Timestamp: $TS"
      echo "- Baseline run: no previous snapshot"
    } > "$TRACK_FILE"
  fi
}

generate_manifest() {
  cat > "$MANIFEST_FILE" <<EOF
{
  "timestamp": "$TS",
  "requested_scope": "$SCOPE",
  "scope": "$EFFECTIVE_SCOPE",
  "repo_root": "$REPO_ROOT",
  "commands": [
    "update-codemap.sh $SCOPE",
    "structure scan",
    "imports scan",
    "semantic corpus build",
    "hashed vector build",
    "change tracking"
  ],
  "outputs": [
    "structure-map.txt",
    "language-stats.txt",
    "imports-python.txt",
    "imports-tsjs.txt",
    "context-cards.md",
    "impact-analysis.md",
    "change-tracking.md",
    "semantic-corpus.jsonl",
    "semantic-vectors.jsonl",
    "semantic-standard.json",
    "manifest.json"
  ]
}
EOF
}

sync_latest() {
  rm -rf "$LATEST_DIR"
  mkdir -p "$LATEST_DIR"
  cp -f "$RUN_DIR"/* "$LATEST_DIR"/
}

generate_structure
generate_stats
generate_import_scans
generate_templates
generate_semantic_artifacts
generate_tracking
generate_manifest
sync_latest

echo "OK: code-map updated"
echo "History: $RUN_DIR"
echo "Latest : $LATEST_DIR"
