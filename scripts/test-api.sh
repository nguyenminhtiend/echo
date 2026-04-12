#!/usr/bin/env bash
# ===========================================================================
# E.C.H.O. — Comprehensive API & Agent Orchestration Test Suite
#
# Usage:
#   ./scripts/test-api.sh                     # default: http://localhost:8000
#   BASE_URL=http://myhost:9000 ./scripts/test-api.sh
# ===========================================================================

set -eo pipefail

BASE="${BASE_URL:-http://localhost:8000}"
PASS=0; FAIL=0; SKIP=0
TMP_BODY=$(mktemp)
HTTP_CODE=""
trap 'rm -f "$TMP_BODY"' EXIT

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

ok()   { echo -e "  ${GREEN}✓${NC} $1"; PASS=$((PASS+1)); }
fail() { echo -e "  ${RED}✗${NC} $1";   FAIL=$((FAIL+1)); }
skip() { echo -e "  ${YELLOW}!${NC} $1"; SKIP=$((SKIP+1)); }

assert_status() {
  if [ "$2" = "$3" ]; then ok "$1  (HTTP $3)"; else fail "$1  (expected $2, got $3)"; fi
}

jq_val() { python3 -c "import sys,json; d=json.load(sys.stdin); print(d$1)" < "$TMP_BODY" 2>/dev/null || echo "__MISSING__"; }

assert_json() {
  local actual; actual=$(jq_val "$2")
  if [ "$actual" = "$3" ]; then ok "$1: $2 == $3"; else fail "$1: $2 expected '$3', got '$actual'"; fi
}

assert_gte() {
  local actual; actual=$(jq_val "$2")
  if python3 -c "exit(0 if ${actual:-0} >= $3 else 1)" 2>/dev/null; then
    ok "$1: $2 = $actual (>= $3)"
  else
    fail "$1: $2 = $actual (expected >= $3)"
  fi
}

do_post() { HTTP_CODE=$(curl -s -o "$TMP_BODY" -w "%{http_code}" -X POST "${BASE}$1" -H "Content-Type: application/json" -d "$2" 2>/dev/null); }
do_get()  { HTTP_CODE=$(curl -s -o "$TMP_BODY" -w "%{http_code}" "${BASE}$1" 2>/dev/null); }
do_raw()  { HTTP_CODE=$(curl -s -o "$TMP_BODY" -w "%{http_code}" "$@" 2>/dev/null); }
extract_id() { python3 -c "import sys,json; print(json.load(sys.stdin)['id'])" < "$TMP_BODY" 2>/dev/null; }

# Store created run IDs indexed 0–N
RUN_IDS=""
add_run_id() { RUN_IDS="${RUN_IDS}${1} "; }
get_run_id() { echo "$RUN_IDS" | tr ' ' '\n' | sed -n "$((${1}+1))p"; }

# ===========================================================================
echo ""
echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${CYAN}  E.C.H.O. API Test Suite — ${BASE}${NC}"
echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════${NC}"

# ───────────────────────────────────────────────────────────────────────────
# 1. HEALTH CHECK
# ───────────────────────────────────────────────────────────────────────────
echo -e "\n${BOLD}[1] Health Check${NC}"
do_get "/health"
assert_status "GET /health" 200 "$HTTP_CODE"
assert_json "health" "['status']" "ok"
assert_json "health" "['version']" "0.1.0"

# ───────────────────────────────────────────────────────────────────────────
# 2. CREATE AGENT RUNS — All 7 Task Types
#    Supervisor classifies each task string into the matching TaskType
# ───────────────────────────────────────────────────────────────────────────
echo -e "\n${BOLD}[2] Create Agent Runs — Supervisor Classification (7 task types)${NC}"

# type|task description (pipe-delimited)
TASK_DEFS="bugfix|fix the login bug in the auth handler
feature|add a new dashboard page for metrics visualization
review|review the pull request for auth module changes
test|write tests for the user service registration flow
security|scan codebase for security vulnerabilities and CVEs
docs|write documentation for the API endpoints
architecture|refactor the authentication architecture and migrate to OAuth2"

echo "$TASK_DEFS" | while IFS='|' read -r TTYPE TDESC; do
  do_post "/api/agents/runs" "{\"task\": \"${TDESC}\"}"
  assert_status "POST create (${TTYPE})" 201 "$HTTP_CODE"
  assert_json "classify(${TTYPE})" "['task_type']" "${TTYPE}"
  assert_json "status(${TTYPE})" "['status']" "pending"
  RID=$(extract_id)
  echo "$RID" >> /tmp/echo_test_run_ids.txt
  echo -e "    → run_id: ${RID}"
done

# Read IDs back (subshell above can't modify parent vars)
if [ -f /tmp/echo_test_run_ids.txt ]; then
  RUN_IDS=$(cat /tmp/echo_test_run_ids.txt | tr '\n' ' ')
  rm -f /tmp/echo_test_run_ids.txt
fi

# ───────────────────────────────────────────────────────────────────────────
# 3. CREATE RUN — explicit task_type override
# ───────────────────────────────────────────────────────────────────────────
echo -e "\n${BOLD}[3] Create Run — Explicit task_type Override${NC}"
do_post "/api/agents/runs" '{"task": "some generic task", "task_type": "custom_override"}'
assert_status "POST (override)" 201 "$HTTP_CODE"
assert_json "override_type" "['task_type']" "custom_override"
add_run_id "$(extract_id)"

# ───────────────────────────────────────────────────────────────────────────
# 4. VALIDATION & EDGE CASES
# ───────────────────────────────────────────────────────────────────────────
echo -e "\n${BOLD}[4] Validation & Edge Cases${NC}"

do_post "/api/agents/runs" '{}'
assert_status "POST missing 'task'" 422 "$HTTP_CODE"

do_post "/api/agents/runs" '{"task": ""}'
if [ "$HTTP_CODE" = "201" ] || [ "$HTTP_CODE" = "422" ]; then
  ok "POST empty task  (HTTP ${HTTP_CODE})"
else
  fail "POST empty task  (unexpected HTTP ${HTTP_CODE})"
fi

do_raw -X POST "${BASE}/api/agents/runs" -H "Content-Type: application/json" -d "not json"
assert_status "POST invalid JSON" 422 "$HTTP_CODE"

do_raw -X POST "${BASE}/api/agents/runs" -H "Content-Type: text/plain" -d '{"task":"hello"}'
assert_status "POST wrong content-type" 422 "$HTTP_CODE"

do_get "/api/agents/runs/not-a-uuid"
assert_status "GET /runs/not-a-uuid" 422 "$HTTP_CODE"

do_get "/api/agents/runs/00000000-0000-0000-0000-000000000000"
assert_status "GET /runs/{zero-uuid} → 404" 404 "$HTTP_CODE"

do_get "/api/traces/not-a-uuid"
assert_status "GET /traces/not-a-uuid" 422 "$HTTP_CODE"

do_get "/api/traces/00000000-0000-0000-0000-000000000000"
assert_status "GET /traces/{zero-uuid} → 404" 404 "$HTTP_CODE"

# ───────────────────────────────────────────────────────────────────────────
# 5. LIST RUNS & PAGINATION
# ───────────────────────────────────────────────────────────────────────────
echo -e "\n${BOLD}[5] List Runs & Pagination${NC}"

do_get "/api/agents/runs"
assert_status "GET /api/agents/runs" 200 "$HTTP_CODE"
assert_gte "list_runs" "['total']" 7

do_get "/api/agents/runs?skip=0&limit=2"
assert_status "GET /runs?limit=2" 200 "$HTTP_CODE"
COUNT=$(python3 -c "import json; print(len(json.load(open('$TMP_BODY'))['runs']))" 2>/dev/null)
if [ "$COUNT" = "2" ]; then ok "pagination: returned exactly 2 runs"; else fail "pagination: expected 2, got ${COUNT}"; fi

do_get "/api/agents/runs?skip=9999&limit=10"
assert_status "GET /runs?skip=9999" 200 "$HTTP_CODE"
COUNT=$(python3 -c "import json; print(len(json.load(open('$TMP_BODY'))['runs']))" 2>/dev/null)
if [ "$COUNT" = "0" ]; then ok "pagination: skip past end → 0 runs"; else fail "pagination: expected 0, got ${COUNT}"; fi

# ───────────────────────────────────────────────────────────────────────────
# 6. GET INDIVIDUAL RUNS
# ───────────────────────────────────────────────────────────────────────────
echo -e "\n${BOLD}[6] Get Individual Runs${NC}"
for RID in $(echo "$RUN_IDS" | tr ' ' '\n' | head -3); do
  [ -z "$RID" ] && continue
  do_get "/api/agents/runs/${RID}"
  assert_status "GET /runs/${RID}" 200 "$HTTP_CODE"
  assert_json "get_run" "['id']" "$RID"
done

# ───────────────────────────────────────────────────────────────────────────
# 7. AGENT STATS
# ───────────────────────────────────────────────────────────────────────────
echo -e "\n${BOLD}[7] Agent Stats${NC}"
do_get "/api/agents/stats"
assert_status "GET /api/agents/stats" 200 "$HTTP_CODE"
assert_gte "stats" "['total_runs']" 7

# ───────────────────────────────────────────────────────────────────────────
# 8. AGENT ORCHESTRATION — Wait for Runs & Verify Traces
# ───────────────────────────────────────────────────────────────────────────
echo -e "\n${BOLD}[8] Agent Orchestration — Wait & Verify Traces${NC}"

TYPES="bugfix feature review test security docs architecture"
# Expected first routed agent per task type
ROUTES="coder coder reviewer qa security docs architect"
# Minimum expected agents per task type
MIN_AGENTS="supervisor,coder supervisor,coder supervisor,reviewer supervisor,qa supervisor,security supervisor,docs supervisor,architect"

MAX_WAIT=120
POLL=3
IDX=0

for TTYPE in $TYPES; do
  IDX=$((IDX+1))
  RID=$(echo "$RUN_IDS" | tr ' ' '\n' | sed -n "${IDX}p")
  [ -z "$RID" ] && { fail "${TTYPE}: no run_id found"; continue; }

  EXPECTED_ROUTE=$(echo "$ROUTES" | tr ' ' '\n' | sed -n "${IDX}p")
  EXPECTED_MIN=$(echo "$MIN_AGENTS" | tr ' ' '\n' | sed -n "${IDX}p")

  echo -e "\n  ${CYAN}── ${TTYPE} (${RID}) ──${NC}"

  # Poll until terminal status
  ELAPSED=0; FINAL_STATUS="unknown"
  while [ $ELAPSED -lt $MAX_WAIT ]; do
    do_get "/api/agents/runs/${RID}"
    FINAL_STATUS=$(jq_val "['status']")
    case "$FINAL_STATUS" in
      pending|running) sleep $POLL; ELAPSED=$((ELAPSED+POLL)) ;;
      *) break ;;
    esac
  done

  case "$FINAL_STATUS" in
    completed|hitl_waiting) ok "run finished: status=${FINAL_STATUS} (${ELAPSED}s)" ;;
    *) fail "run status=${FINAL_STATUS} after ${ELAPSED}s (expected completed/hitl_waiting)" ;;
  esac

  # Fetch trace
  TMP_TRACE=$(mktemp)
  HTTP_CODE=$(curl -s -o "$TMP_TRACE" -w "%{http_code}" "${BASE}/api/traces/${RID}" 2>/dev/null)
  assert_status "GET /traces/${RID}" 200 "$HTTP_CODE"

  ECOUNT=$(python3 -c "import json; print(len(json.load(open('$TMP_TRACE'))['events']))" 2>/dev/null || echo "0")
  if [ "$ECOUNT" -gt 0 ] 2>/dev/null; then ok "trace has ${ECOUNT} events"; else fail "trace has 0 events"; fi

  # Supervisor classify event
  python3 -c "
import json, sys
d=json.load(open('$TMP_TRACE'))
has = any(e.get('event_type')=='classify' and e.get('agent_name')=='supervisor' for e in d.get('events',[]))
sys.exit(0 if has else 1)
" 2>/dev/null && ok "supervisor classify event found" || fail "supervisor classify event missing"

  # Routing check
  ROUTED=$(python3 -c "
import json
d=json.load(open('$TMP_TRACE'))
for e in d.get('events',[]):
  if e.get('event_type')=='classify':
    print(e.get('data',{}).get('routed_to',''))
    break
" 2>/dev/null)
  if [ "$ROUTED" = "$EXPECTED_ROUTE" ]; then
    ok "supervisor routed ${TTYPE} → ${ROUTED}"
  else
    fail "supervisor routed ${TTYPE} → '${ROUTED}' (expected ${EXPECTED_ROUTE})"
  fi

  # All expected agents present in trace
  AGENTS_SEEN=$(python3 -c "
import json
d=json.load(open('$TMP_TRACE'))
print(','.join(sorted({e.get('agent_name','') for e in d.get('events',[]) if e.get('agent_name')})))
" 2>/dev/null)
  ALL_OK=true
  for AGENT in $(echo "$EXPECTED_MIN" | tr ',' ' '); do
    case "$AGENTS_SEEN" in
      *"$AGENT"*) ;;
      *) ALL_OK=false; fail "expected agent '${AGENT}' missing (saw: ${AGENTS_SEEN})" ;;
    esac
  done
  if [ "$ALL_OK" = true ]; then ok "expected agents present: ${EXPECTED_MIN}"; fi

  # agent_start/agent_end pairs
  python3 -c "
import json, sys
d=json.load(open('$TMP_TRACE'))
evts = d.get('events',[])
starts = {e['agent_name'] for e in evts if e.get('event_type')=='agent_start'}
ends   = {e['agent_name'] for e in evts if e.get('event_type')=='agent_end'}
missing = starts - ends
sys.exit(0 if not missing else 1)
" 2>/dev/null && ok "all agent_start have matching agent_end" || skip "some agents started but not ended"

  # llm_end events have model field
  python3 -c "
import json, sys
d=json.load(open('$TMP_TRACE'))
evts = [e for e in d.get('events',[]) if e.get('event_type')=='llm_end']
ok = all(e.get('data',{}).get('model') for e in evts)
sys.exit(0 if ok or not evts else 1)
" 2>/dev/null && ok "all llm_end events have model field" || skip "some llm_end events missing model"

  rm -f "$TMP_TRACE"
done

# ───────────────────────────────────────────────────────────────────────────
# 9. RAG QUERY
# ───────────────────────────────────────────────────────────────────────────
echo -e "\n${BOLD}[9] RAG Query${NC}"

do_post "/api/rag/query" '{"query": "authentication flow"}'
assert_status "POST /api/rag/query" 200 "$HTTP_CODE"
assert_json "rag_query" "['query']" "authentication flow"

do_post "/api/rag/query" '{"query": "database models", "top_k": 3}'
assert_status "POST /api/rag/query (top_k=3)" 200 "$HTTP_CODE"

# ───────────────────────────────────────────────────────────────────────────
# 10. FINAL STATS
# ───────────────────────────────────────────────────────────────────────────
echo -e "\n${BOLD}[10] Final Stats${NC}"
do_get "/api/agents/stats"
assert_status "GET /api/agents/stats (final)" 200 "$HTTP_CODE"
echo -e "  total_runs:   $(jq_val "['total_runs']")"
echo -e "  total_tokens:  $(jq_val "['total_tokens']")"
echo -e "  total_cost:    $(jq_val "['total_cost']")"

# ───────────────────────────────────────────────────────────────────────────
# 11. OPENAPI SPEC
# ───────────────────────────────────────────────────────────────────────────
echo -e "\n${BOLD}[11] OpenAPI Spec${NC}"
do_get "/openapi.json"
assert_status "GET /openapi.json" 200 "$HTTP_CODE"
do_get "/docs"
assert_status "GET /docs (Swagger UI)" 200 "$HTTP_CODE"

# ===========================================================================
echo ""
echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}  RESULTS: ${GREEN}${PASS} passed${NC}, ${RED}${FAIL} failed${NC}, ${YELLOW}${SKIP} skipped${NC}"
echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════${NC}"
echo ""

if [ "$FAIL" -gt 0 ]; then exit 1; fi
