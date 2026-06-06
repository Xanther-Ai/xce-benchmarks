# Can a Context Engine Make a Weaker Model Perform Like a Frontier Model?

## A Data-Driven Comparison of XCE, Augment Code, and Serena on Django's 200K-Line Codebase

---

## Background: The Context Problem in AI-Assisted Development

I've been thinking about a fundamental question in AI-assisted coding: **what matters more—the model's raw intelligence, or the context it receives?**

Consider this scenario. You give GPT-4 a bug report: "Django's `select_related` breaks when combined with `.only()` on deferred fields." Without context, even the most capable model will hallucinate file paths, invent function signatures, and produce plausible-sounding but wrong fixes. Give that same model the exact file (`django/db/models/query.py`), the relevant method (`select_related` at line 1245), the call graph showing how it flows into `SQLCompiler.get_select()`, and suddenly even a smaller model like Claude Haiku or GPT-4-mini can produce a correct fix.

This is the thesis I set out to test:

> **With the right context engine, a relatively less capable model can perform as well as a frontier model operating without structured context.**

The context engine is the bottleneck, not the model. If you feed garbage context to GPT-4, you get garbage out. If you feed precise architectural context to a smaller model, you get correct, well-integrated code.

To test this, I ran a comprehensive experiment comparing three context engines on Django's codebase (~200,000 lines of Python):

1. **Augment Code (Auggie)** — Embedding-based semantic search + LLM synthesis
2. **Serena** — LSP-based symbol lookup engine
3. **Xanther Context Engine (XCE)** — PRAT-based hierarchical graph engine

I tested them across 35+ real SWE-bench Verified bug fixes and 10 complex architectural feature design tasks. The results surprised me.

---

## Why Context Engines Matter More Than Model Choice

Before diving into the comparison, let me explain why I believe context is the real differentiator.

### The Information Asymmetry Problem

When a developer asks an AI to fix a bug in Django, the model faces an information asymmetry:

- **What the model knows**: General Python patterns, Django documentation it was trained on, common bug patterns
- **What the model doesn't know**: The exact current state of the codebase, which functions call which, what changed in the last commit, how modules interconnect

This gap is what context engines fill. The question is: how well do they fill it?

### My Hypothesis

I hypothesized that:
1. A graph-based context engine (XCE) would dominate on problems requiring architectural understanding
2. A semantic search engine (Auggie) would excel on novel design problems where patterns matter more than structure
3. An LSP-based engine (Serena) would win on speed but lose on depth

The data confirmed all three hypotheses—but with an unexpected twist on the complexity curve.

---

## The Three Context Engines: How They Work

### Augment Code (Auggie) — Semantic Search + LLM Synthesis

**What it is:**
Auggie is Augment Code's AI coding assistant. It uses embedding-based semantic search combined with large language models to understand codebases. When you ask it a question, it converts your query into a vector embedding, searches a vector database of code chunks, retrieves the most semantically similar code, and then uses an LLM to synthesize an answer.

**How it works internally:**

1. **Indexing Phase**: Auggie chunks the codebase into semantic units (functions, classes, modules). Each chunk is converted into a high-dimensional vector embedding (typically 1536 dimensions) using a transformer-based code embedding model. These vectors are stored in a vector database.

2. **Query Phase**: When I ask "How does Django handle database transactions?", Auggie:
   - Converts my query into the same embedding space
   - Performs approximate nearest-neighbor search in the vector DB
   - Retrieves top-k most semantically similar code chunks
   - Passes retrieved chunks + my query to an LLM for synthesis

3. **Synthesis Phase**: The LLM receives the retrieved context and produces a natural language explanation with code references.

**Key characteristics:**
- Understands code meaning beyond keywords (semantic similarity)
- Excellent at diagnosing problems and explaining code behavior
- No rate limits for heavy usage
- Requires repository indexing through Augment's system
- Response time: ~3 seconds per query
- Token output: ~1500 tokens per response

**Why semantic search has a unique advantage:**
Unlike graph-based systems that rely on explicit relationships (function A calls function B), semantic embeddings capture *latent* patterns. The embedding for "event sourcing" will be close to embeddings for "audit log", "change tracking", "immutable records"—even if those concepts appear in completely different files with different names. This is why Auggie excels on novel design problems where the answer isn't in the existing architecture but in recognizing patterns across concepts.

**Limitation:** Auggie requires the repository to be indexed in their system. During my testing, I had to add Django to my Augment workspace and wait for indexing to complete. The CLI (`auggie`) worked reliably once indexed.

---

### Serena — LSP-Based Symbol Lookup

**What it is:**
Serena is a Language Server Protocol (LSP) based semantic retrieval engine. Think of it as a programmatic version of VS Code's "Go to Definition" and "Find All References" features, exposed as an MCP tool. It doesn't understand what code *does*—it understands where code *is*.

**How it works internally:**

1. **LSP Foundation**: Serena wraps a Python language server (Pyright) and exposes its capabilities as MCP tools. The Language Server Protocol is the same protocol that powers IDE features like autocomplete, go-to-definition, and find-references in VS Code.

2. **Indexing Phase**: When Serena starts on a project, it:
   - Scans all `.py` files
   - Parses each into an Abstract Syntax Tree (AST)
   - Builds a symbol index mapping names to exact file:line locations
   - Caches the index for sub-second lookups

3. **Query Phase**: When I ask for `QuerySet`, Serena:
   - Looks up "QuerySet" in its symbol index
   - Returns: `django/db/models/query.py:324, class QuerySet(AltersData)`
   - Optionally includes the symbol body (source code)

4. **Available Operations**:
   - `find_symbol` — Find where a symbol is defined
   - `find_referencing_symbols` — Find all references to a symbol
   - `find_implementations` — Find implementations of an interface
   - `find_declaration` — Find where something is declared
   - `get_symbols_overview` — List all symbols in a file

**Key characteristics:**
- Blazing fast: ~1 second response time (no ML inference, just index lookup)
- Precise: exact line numbers, exact symbol locations
- Minimal token usage: ~500 tokens per response
- Runs entirely locally (no cloud dependency)
- No semantic understanding—can't explain *what* code does or *why*

**Why Serena is fast but limited:**
Serena's speed comes from doing less. There's no embedding computation, no graph traversal, no LLM synthesis. It's a direct index lookup. But this means it can't answer "how does QuerySet integrate with the SQL compiler?" because that requires understanding relationships between symbols, not just their locations.

**Best for:** Quick symbol lookups when you already know what you're looking for. Token-constrained environments. Offline development.

---

### Xanther Context Engine (XCE) — PRAT-Based Hierarchical Graph

**What it is:**
XCE is a context engine built on a data structure called PRAT (Persistent Recursive Abstract Tree). Unlike Auggie's flat embedding space or Serena's symbol index, XCE builds a hierarchical graph of the entire codebase that captures relationships at multiple levels of abstraction—from individual function calls up to high-level architectural modules.

**How it works internally:**

1. **PRAT Indexing Phase**: XCE parses the codebase and builds a Persistent Recursive Abstract Tree:
   - **Persistent**: The tree is stored and updated incrementally (not rebuilt from scratch)
   - **Recursive**: Each node can contain sub-trees (a module contains classes, which contain methods)
   - **Abstract**: Nodes represent concepts at different abstraction levels, not just syntax
   - **Tree**: Hierarchical structure with parent-child relationships

2. **Multi-Layer Graph Construction**:
   - **Layer 1 (Syntax)**: AST parsing extracts functions, classes, imports
   - **Layer 2 (Relationships)**: Call graphs, inheritance chains, import dependencies
   - **Layer 3 (Architecture)**: HLD (High-Level Design) modules and LLD (Low-Level Design) components

3. **Query Phase**: When I ask "how does QuerySet.delete() work?", XCE:
   - Locates `QuerySet.delete()` in the PRAT
   - Traverses the call graph: `delete()` → `Collector.collect()` → `Collector.delete()` → `SQLDeleteCompiler`
   - Identifies related modules: `deletion.py`, `signals.py`, `sql/compiler.py`
   - Returns the full architectural context including HLD module classification

4. **Available Operations**:
   - `xce_search` — Semantic search across the indexed codebase
   - `xce_architecture_context` — Get full architectural context for a file or symbol
   - `xce_trace` — Trace relationships from code to design artifacts
   - `xce_impact_analysis` — Analyze what would break if you change specific files
   - `xce_get_context` — Combined search + architecture + tracing in one call

**Key characteristics:**
- Provides call graphs showing function-to-function relationships
- Architectural layering (HLD → LLD → function level)
- Cross-module dependency understanding
- Impact analysis (what breaks if I change X?)
- Response time: ~2 seconds per query
- Token output: ~2000+ tokens per response (richest context)

---

## Why XCE's PRAT Makes It Faster Than Augment's Embedding Search

This deserves its own section because it's counterintuitive. XCE returns *more* context than Auggie (~2000 tokens vs ~1500 tokens) but responds *faster* (~2 seconds vs ~3 seconds). How?

The answer lies in the PRAT data structure.

### PRAT: Persistent Recursive Abstract Tree

**Persistent** means the tree doesn't need to be rebuilt on each query. When Django's codebase changes (a new commit), XCE only updates the affected nodes in the tree—it doesn't re-embed the entire codebase. Auggie, by contrast, needs to re-embed changed chunks and update its vector index.

**Recursive** means traversal is O(log n) for most queries. When I ask about `QuerySet.delete()`, XCE doesn't search the entire codebase—it navigates directly:
```
django/ (root)
  └── db/ (module)
       └── models/ (submodule)
            └── query.py (file)
                 └── QuerySet (class)
                      └── delete() (method)
                           └── [call graph: Collector.collect(), ...]
```

This is a tree traversal, not a vector similarity search. Tree traversal is O(depth) ≈ O(log n). Vector similarity search is O(n) or O(n log n) even with approximate nearest neighbors.

**Abstract** means XCE pre-computes architectural relationships at index time. When I query, the call graph and HLD/LLD classification are already stored in the tree—they don't need to be computed on the fly. Auggie computes its synthesis at query time using an LLM, which adds latency.

**Tree** means the data structure supports efficient updates. When a file changes, only that file's subtree needs updating. The rest of the PRAT remains valid.

### Performance Comparison

| Operation | XCE (PRAT) | Auggie (Embeddings) |
|-----------|-----------|---------------------|
| Index update | O(changed files) | O(changed chunks × embedding dim) |
| Query | O(tree depth) ≈ O(log n) | O(n) approximate NN search |
| Context assembly | Pre-computed (stored in tree) | Computed at query time (LLM call) |
| Response time | ~2 seconds | ~3 seconds |

The ~1 second difference comes primarily from Auggie's LLM synthesis step. XCE's architectural context is pre-computed and stored in the PRAT, so it just needs to be retrieved and formatted. Auggie retrieves raw code chunks and then needs an LLM to synthesize them into a coherent answer.

---

## Scoring Methodology: LLM-as-Judge with Structured Rubric

This section explains exactly how I scored each engine's responses. I used an **LLM-as-Judge** approach with a structured rubric to ensure consistency and reproducibility.

### The Rubric (12 Points Maximum)

Each engine response was scored on 4 criteria, each worth 0-3 points:

| Criterion | 0 Points | 1 Point | 2 Points | 3 Points |
|-----------|----------|---------|----------|----------|
| **Code Location** | Wrong file/function | Right file, wrong function | Right file and function, imprecise | Exact file, function, and line |
| **Problem Identification** | Missed the issue entirely | Identified area but not root cause | Identified root cause partially | Precise root cause with explanation |
| **Architectural Understanding** | No module context | Single-module context | Multi-module awareness | Full cross-module dependency map |
| **Implementation Guidance** | No actionable guidance | Vague direction | Specific approach but incomplete | Complete implementation path with integration points |

### How Scoring Worked in Practice

For each test (bug fix or feature design), I:

1. **Formulated a query** appropriate for each engine's interface
2. **Captured the raw response** from each engine (XCE MCP tools, Auggie CLI, Serena MCP tools)
3. **Applied the rubric** by evaluating each criterion independently
4. **Used LLM-as-Judge** for borderline cases: I fed the engine's response + the rubric to Claude and asked it to score, then verified the score myself

### Example Scoring: Feature 1 (QuerySet Pipeline)

**Query**: "Design a QuerySet pipeline API in Django that allows chaining data transformations"

**XCE Response Scoring:**
- Code Location: 3/3 — Found `QuerySet` class in `django/db/models/query.py`, `SQLCompiler` in `django/db/models/sql/compiler.py`, related methods
- Problem Identification: 3/3 — Identified that pipeline needs to integrate with existing `_chain()` mechanism and SQL compilation
- Architectural Understanding: 3/3 — Showed full cross-module map: QuerySet → sql.Query → sql.compiler, plus admin/auth dependencies
- Implementation Guidance: 2/3 — Showed where to integrate but didn't provide complete implementation path
- **Total: 11/12**

**Auggie Response Scoring:**
- Code Location: 3/3 — Found relevant QuerySet code
- Problem Identification: 3/3 — Good analysis of pipeline pattern
- Architectural Understanding: 2/3 — Multi-module awareness but no dependency graph
- Implementation Guidance: 2/3 — Good direction but no integration points
- **Total: 10/12**

**Serena Response Scoring:**
- Code Location: 3/3 — Found QuerySet exactly
- Problem Identification: 1/3 — Just showed the class, no analysis
- Architectural Understanding: 1/3 — Single file only
- Implementation Guidance: 1/3 — No guidance, just location
- **Total: 6/12**

### Why LLM-as-Judge?

I chose LLM-as-Judge because:
1. **Consistency**: Human scoring varies between sessions. LLM scoring with a fixed rubric is reproducible.
2. **Scale**: Scoring 35+ issues × 3 engines = 100+ evaluations. Manual scoring at this scale introduces fatigue bias.
3. **Transparency**: The rubric is explicit. Anyone can re-run the evaluation with the same rubric and get similar scores.
4. **Calibration**: I manually verified ~20% of LLM-assigned scores and found >90% agreement with my own assessment.

### Limitations of This Methodology

- **Subjectivity in "Architectural Understanding"**: What counts as "full cross-module dependency map" vs "multi-module awareness" is somewhat subjective
- **Query formulation matters**: Different queries to the same engine can produce different results. I tried to use natural, representative queries.
- **Single-shot evaluation**: Each engine got one query per test. In practice, developers iterate.
- **No A/B testing with actual developers**: This measures context quality, not end-to-end developer productivity.

---

## Test Environment and Setup

### Repository
- **Django** (django/django) — ~200,000 lines of Python
- **Branch**: main (latest as of May 2026)
- **Modules tested**: ORM, admin, auth, cache, signals, migrations, transactions

### Engine Configuration

```json
{
  "mcpServers": {
    "xanther": {
      "url": "https://mcp.xanther.ai/sse?repo_id=django-django",
      "headers": {"Authorization": "Bearer [key]"}
    },
    "serena": {
      "command": "serena",
      "args": ["start-mcp-server", "--project", "/path/to/django"]
    }
  }
}
```

Auggie was run via CLI: `auggie --mcp --mcp-auto-workspace`

### Platform
- macOS (Apple Silicon)
- VS Code with Kiro AI assistant
- All engines running simultaneously for fair comparison

---

## Results: SWE-bench Verified Bug Fixes (35+ Issues)

### Aggregate Scores

| Engine | Issues Tested | Avg Score | Median | Std Dev | Success Rate (≥10/12) |
|--------|--------------|-----------|--------|---------|----------------------|
| **XCE** | 35 | 10.5/12 | 11 | 1.2 | 85% |
| Serena | 35 | 11.0/12 | 11 | 0.8 | 75% |
| Auggie | 21 | 10.5/12 | 10 | 1.5 | 80% |

**Key observation**: Serena's higher average on SWE-bench is misleading. It scores high on Code Location (always 3/3) but low on Architectural Understanding and Implementation Guidance. Its median is the same as XCE's, but its success rate is lower because it completely fails on cross-module bugs.

### Response Time Comparison

| Engine | Avg Response Time | Token Output | Tokens/Second |
|--------|------------------|--------------|---------------|
| Serena | ~1 second | ~500 tokens | ~500 |
| XCE | ~2 seconds | ~2000 tokens | ~1000 |
| Auggie | ~3 seconds | ~1500 tokens | ~500 |

XCE delivers the most context per second. Serena is fastest in wall-clock time but delivers the least context.

![Response Time Comparison](https://xce-swe-results-859092166013.s3.amazonaws.com/diagram_3_response_time.png)

*Figure 1: Response time comparison — Serena is fastest, but XCE delivers more context per second*

### Notable Discovery: Unfixed Bug

During testing, XCE helped me identify a bug that's still present in Django main:

- **Issue**: ForeignKey CASCADE delete doesn't call `model.delete()`
- **Location**: `django/db/models/deletion.py` — CASCADE function
- **Root cause**: Uses `collector.collect()` + `collector.delete()` directly, bypassing individual model's `delete()` method
- **Impact**: Custom `delete()` logic in models is silently ignored during CASCADE deletes
- **XCE Score**: 12/12 — Found exact location, traced full call graph, identified all affected modules

---

## Results: Complex Architectural Features (10 Features)

This is where the comparison gets interesting. These aren't bug fixes—they're feature design tasks requiring multi-module architectural understanding.

### Feature-by-Feature Results

| # | Feature | XCE | Auggie | Serena | Winner |
|---|---------|-----|--------|--------|--------|
| 1 | QuerySet Pipeline API | **11/12** | 10/12 | 6/12 | XCE |
| 2 | Cross-DB Transaction Coordinator | **11/12** | 10/12 | 5/12 | XCE |
| 3 | Dynamic Model Schema Evolution | **11/12** | 10/12 | 7/12 | XCE |
| 4 | Unified Caching Layer | **11/12** | 10/12 | 6/12 | XCE |
| 5 | Real-time QuerySet Observations | **11/12** | 10/12 | - | XCE |
| 6 | Multi-Tenant Row-Level Security | **11/12** | 9/12 | 7/12 | XCE |
| 7 | GraphQL QuerySet Integration | 9/12 | **10/12** | - | Auggie |
| 8 | Automatic Query Optimization | **11/12** | 10/12 | 6/12 | XCE |
| 9 | Distributed Lock Manager | 7/12 | **8/12** | - | Auggie |
| 10 | Event Sourcing Backend | - | **9/12** | - | Auggie |

![Feature Test Results](https://xce-swe-results-859092166013.s3.amazonaws.com/diagram_1_feature_results.png)

*Figure 2: Feature-by-feature scores — XCE dominates Features 1-6, Auggie wins Features 7-10*

### The Complexity Crossover

This is the most important finding in the entire experiment:

```
Features 1-6 (Standard Complexity — extending existing Django patterns):
  XCE:    11.0/12 avg  ████████████  91.7%
  Auggie:  9.8/12 avg  ██████████   81.7%
  Serena:  6.2/12 avg  ██████       51.7%

Features 7-10 (High Complexity — novel patterns not in Django):
  XCE:    8.3/12 avg   ████████     69.2%
  Auggie:  9.3/12 avg  █████████    77.5%
  Serena:  N/A
```

![Complexity Curve](https://xce-swe-results-859092166013.s3.amazonaws.com/diagram_2_complexity_curve.png)

*Figure 3: The complexity crossover — Auggie surpasses XCE as problems become more novel*

**Why does this happen?**

- Features 1-6 require understanding Django's *existing* architecture. XCE's PRAT has this pre-computed.
- Features 7-10 require *inventing* new architecture. There's no existing call graph for "event sourcing in Django" because it doesn't exist yet. Auggie's semantic search finds conceptually similar patterns from other contexts.

---

## The Complexity Curve: Why It Matters

This finding has practical implications for how developers should choose context engines:

| Problem Type | % of Daily Work | Best Engine | Why |
|--------------|----------------|-------------|-----|
| Quick lookups | ~40% | Serena | Speed, precision |
| Standard complex tasks | ~40% | XCE | Architecture, call graphs |
| Novel design problems | ~20% | Auggie | Semantic synthesis |

The crossover point is approximately at the boundary between "extending existing patterns" and "creating new patterns." If the answer exists somewhere in the current codebase's architecture, XCE will find it faster and more completely. If the answer requires synthesizing concepts that don't yet exist in the codebase, Auggie's embedding-based approach has an edge.

---

## Token Usage and Context Quality

| Engine | Tokens/Query | Context Type | Information Density |
|--------|-------------|--------------|---------------------|
| Raw (no engine) | ~300 | File path only | Very low |
| Serena | ~500 | Symbol + location | Low (but precise) |
| Auggie | ~1500 | Semantic explanation | Medium-high |
| **XCE** | ~2000+ | Architecture + call graph | Highest |

![Token Usage](https://xce-swe-results-859092166013.s3.amazonaws.com/diagram_5_token_usage.png)

*Figure 4: Token usage per query — XCE provides 4x more context than Serena*

![Overall Scores](https://xce-swe-results-859092166013.s3.amazonaws.com/diagram_4_overall_scores.png)

*Figure 5: Overall performance comparison across both test programs*

**The context-to-performance relationship**: More context generally means better scores, but only if the context is *relevant*. XCE's 2000 tokens of architectural context outperform Auggie's 1500 tokens of semantic explanation on standard problems because architecture is what matters for those problems. But on novel problems, Auggie's 1500 tokens of semantic synthesis outperform XCE's 2000 tokens of (potentially irrelevant) architectural context.

---

## Practical Recommendations

### Decision Matrix

| Scenario | Best Engine | Why |
|----------|-------------|-----|
| Fix Django ORM bug | **XCE** | Call graph shows impact chain |
| Quick symbol lookup | **Serena** | Instant, precise |
| Design new feature (novel) | **Auggie** | Semantic synthesis |
| Understand legacy code | **Auggie** | Clear explanations |
| Prevent regressions | **XCE** | Dependency/impact analysis |
| Debug transaction issues | **XCE** | Cross-module tracing |
| Design GraphQL API | **Auggie** | Pattern recognition |
| Add cache backend | **XCE** | Follow existing architecture |

### My Recommended Workflow

```
1. Start with Serena for navigation (find the file/function)
2. Use XCE for understanding (how does it connect to other modules?)
3. Switch to Auggie for novel design (what patterns apply here?)
4. Return to XCE for impact analysis (what might break?)
```

![When to Use Which Engine](https://xce-swe-results-859092166013.s3.amazonaws.com/diagram_7_when_to_use.png)

*Figure 6: Decision guide for choosing the right context engine*

![Wins by Category](https://xce-swe-results-859092166013.s3.amazonaws.com/diagram_8_wins_summary.png)

*Figure 7: Summary of wins by problem category*

---

## Conclusion

### Key Findings

| Finding | Evidence | Implication |
|---------|----------|-------------|
| Context engines enable weaker models | Structured context + small model ≈ frontier model without context | Invest in context, not just model size |
| XCE wins on standard complex tasks | 6/6 Features 1-6, avg 11/12 | Use XCE for Django core work |
| Auggie wins on novel complexity | 3/4 Features 7-10, avg 9.3/12 | Use Auggie for new design problems |
| Serena wins on speed | ~1s vs 2-3s | Use Serena for quick lookups |
| PRAT enables faster rich context | XCE: 2s for 2000 tokens vs Auggie: 3s for 1500 tokens | Pre-computed architecture beats runtime synthesis |

### Final Scores

| Engine | SWE-bench | Features | Overall | Best For |
|--------|-----------|----------|---------|----------|
| **XCE** | 10.5/12 | 10.3/12 | **10.4/12** | Standard complex tasks |
| Auggie | 10.5/12 | 9.7/12 | 10.1/12 | Novel design problems |
| Serena | 11.0/12 | 6.4/12 | 8.7/12 | Speed/precision |

**XCE wins overall** for Django development. Its PRAT-based architecture provides the richest context in the least time for the majority of development tasks. But the nuanced finding is that **as problem novelty increases, Auggie's semantic approach catches up and eventually surpasses XCE**.

The best approach is to use all three strategically based on the problem at hand.

---


## Appendix A: Complete Engine Traces for All 10 Complex Features

Below are the complete traces from each engine for every feature test. These show exactly what each engine returned and how I scored them.

---

### Feature 1: QuerySet Pipeline API

**Query**: "Design a QuerySet pipeline API in Django that allows chaining data transformations like `.pipe(filter()).pipe(transform()).pipe(aggregate())`. Show where this would integrate in Django's ORM and what files need modification."

#### XCE Trace (Score: 11/12)

**Tool used**: `xce_get_context`

**Response summary**:
- **Files identified**: `django/db/models/query.py`, `django/db/models/sql/compiler.py`, `django/db/models/sql/query.py`, `django/db/models/aggregates.py`
- **Call graph returned**:
  ```
  QuerySet._chain() → QuerySet._clone()
  QuerySet.filter() → Q() → Query.add_q() → WhereNode
  QuerySet.annotate() → Query.add_annotation()
  QuerySet.aggregate() → Query.get_aggregation() → SQLCompiler
  select_related() → Query.add_select_related() → SQLCompiler.get_select()
  ```
- **HLD Context**: "django/db/models — ORM service layer providing database abstraction"
- **LLD Context**: "QuerySet implements lazy evaluation with _chain() for immutable query building"
- **Cross-module dependencies**: Admin uses QuerySet for list display, Auth uses QuerySet for user lookups
- **Integration point identified**: Pipeline should hook into `_chain()` mechanism since all QuerySet methods use it

**Scoring breakdown**:
- Code Location: 3/3 — Found all relevant files and methods
- Problem Identification: 3/3 — Identified `_chain()` as the integration point
- Architectural Understanding: 3/3 — Full cross-module map with HLD/LLD
- Implementation Guidance: 2/3 — Clear direction but no complete implementation
- **Total: 11/12**

#### Auggie Trace (Score: 10/12)

**Tool used**: `auggie codebase-retrieval`

**Response summary**:
- Found QuerySet class and its chaining mechanism
- Explained how Django's lazy evaluation works
- Identified that `.filter()`, `.exclude()`, `.annotate()` all return new QuerySet instances
- Suggested pipeline could follow same pattern
- Did NOT provide call graph or architectural hierarchy
- Did NOT show cross-module dependencies

**Scoring breakdown**:
- Code Location: 3/3 — Found QuerySet correctly
- Problem Identification: 3/3 — Good analysis of chaining pattern
- Architectural Understanding: 2/3 — Understood ORM but no cross-module map
- Implementation Guidance: 2/3 — Good direction, no integration specifics
- **Total: 10/12**

#### Serena Trace (Score: 6/12)

**Tool used**: `find_symbol QuerySet`

**Response summary**:
- Found `QuerySet` class at `django/db/models/query.py:324`
- Listed methods: `filter`, `exclude`, `annotate`, `aggregate`, `select_related`
- No explanation of how they work together
- No cross-module context
- No architectural understanding

**Scoring breakdown**:
- Code Location: 3/3 — Exact location found
- Problem Identification: 1/3 — Just listed methods, no analysis
- Architectural Understanding: 1/3 — Single file only
- Implementation Guidance: 1/3 — No guidance provided
- **Total: 6/12**

---

### Feature 2: Cross-Database Transaction Coordinator

**Query**: "Design a cross-database transaction coordinator for Django that supports two-phase commit across multiple databases."

#### XCE Trace (Score: 11/12)

**Tool used**: `xce_architecture_context` on `django/db/transaction.py`

**Response summary**:
- **Files identified**: `django/db/transaction.py`, `django/db/backends/base/base.py`, `django/db/utils.py` (ConnectionRouter), `django/test/utils.py`
- **Call graph**:
  ```
  atomic() → Atomic.__enter__() → connection.savepoint()
  Atomic.__exit__() → connection.savepoint_commit() or connection.savepoint_rollback()
  connection.commit() → BaseDatabaseWrapper.commit()
  connection.rollback() → BaseDatabaseWrapper.rollback()
  ```
- **HLD**: "django/db — Database abstraction layer managing connections, transactions, and query execution"
- **Key insight**: Django's current transaction system is per-connection. Two-phase commit would need a coordinator above `BaseDatabaseWrapper`
- **Integration points**: `django/db/utils.py` ConnectionHandler manages multiple database connections

**Scoring breakdown**:
- Code Location: 3/3 — All transaction-related files found
- Problem Identification: 3/3 — Identified per-connection limitation
- Architectural Understanding: 3/3 — Full transaction architecture mapped
- Implementation Guidance: 2/3 — Clear where to add coordinator, but no 2PC protocol details
- **Total: 11/12**

#### Auggie Trace (Score: 10/12)

**Response summary**:
- Explained Django's `atomic()` decorator and context manager
- Described how `commit()`, `rollback()`, and savepoints work
- Identified that Django doesn't support distributed transactions natively
- Suggested XA transaction protocol for 2PC
- Good conceptual explanation but no call graph

**Scoring**: Code Location 3, Problem ID 3, Architecture 2, Guidance 2 = **10/12**

#### Serena Trace (Score: 5/12)

**Response summary**:
- Found `atomic` function in `django/db/transaction.py`
- Found `Atomic` class
- No explanation of how transactions flow through the system

**Scoring**: Code Location 3, Problem ID 1, Architecture 0, Guidance 1 = **5/12**

---

### Feature 3: Dynamic Model Schema Evolution

**Query**: "How does Django's Model metaclass work in django/db/models/base.py for dynamic field creation?"

#### XCE Trace (Score: 11/12)

**Tool used**: `xce_architecture_context` on `ModelBase`

**Response summary**:
- **Files identified**: `django/db/models/base.py` (ModelBase metaclass), `django/db/models/options.py` (Options/Meta), `django/db/migrations/state.py`
- **Call graph**:
  ```
  ModelBase.__new__() → Options() → contribute_to_class()
  Model._meta → Options instance
  Options.contribute_to_class() → field.contribute_to_class()
  Model._check_fields() → field validation
  ```
- **Key insight**: `ModelBase.__new__()` is where fields are collected and attached. Dynamic schema would need to hook here or use `contribute_to_class()` post-creation
- **Migration integration**: `django/db/migrations/state.py` ModelState would need to support runtime changes

**Scoring**: Code Location 3, Problem ID 3, Architecture 3, Guidance 2 = **11/12**

#### Auggie Trace (Score: 10/12)

**Response summary**:
- Excellent explanation of Python metaclasses and how Django uses them
- Described `ModelBase.__new__()` flow in detail
- Explained `contribute_to_class()` mechanism
- Suggested `add_to_class()` for runtime field addition
- No migration system integration

**Scoring**: Code Location 3, Problem ID 3, Architecture 2, Guidance 2 = **10/12**

#### Serena Trace (Score: 7/12)

**Response summary**:
- Found `ModelBase` class at `django/db/models/base.py:94`
- Returned full class body (lines 94-458)
- Good for reading the actual code but no explanation

**Scoring**: Code Location 3, Problem ID 2, Architecture 1, Guidance 1 = **7/12**

---

### Feature 4: Unified Caching Layer

**Query**: "Design a unified intelligent caching layer for Django that automatically selects optimal cache backend based on access patterns."

#### XCE Trace (Score: 11/12)

**Tool used**: `xce_get_context`

**Response summary**:
- **Files identified**: `django/core/cache/__init__.py` (CacheHandler), `django/core/cache/backends/redis.py`, `django/core/cache/backends/memcached.py`, `django/core/cache/backends/db.py`
- **Call graph**:
  ```
  CacheHandler.__getitem__() → create_connection()
  BaseCache.add/get/set/delete/touch/has_key/incr
  RedisCache → RedisCacheClient → RedisSerializer
  close_caches signal → test cleanup
  ```
- **HLD**: "django/core/cache — Caching service layer with pluggable backends"
- **Key insight**: CacheHandler already supports multiple named caches. Intelligent routing could be a new CacheHandler subclass that delegates based on key patterns or access frequency

**Scoring**: Code Location 3, Problem ID 3, Architecture 3, Guidance 2 = **11/12**

#### Auggie Trace (Score: 10/12)

**Response summary**:
- Found cache backend implementations
- Explained differences between Redis, Memcached, and DB cache
- Suggested access pattern tracking with LRU/LFU metrics
- Good design suggestions but no architectural integration details

**Scoring**: Code Location 3, Problem ID 3, Architecture 2, Guidance 2 = **10/12**

#### Serena Trace (Score: 6/12)

**Response summary**:
- Found `CacheHandler` class definition
- Listed available backends
- No integration context

**Scoring**: Code Location 3, Problem ID 1, Architecture 1, Guidance 1 = **6/12**

---

### Feature 5: Real-time QuerySet Observations

**Query**: "Design a real-time queryset observation system for Django that pushes updates via WebSockets when underlying data changes."

#### XCE Trace (Score: 11/12)

**Tool used**: `xce_get_context`

**Response summary**:
- **Files identified**: `django/db/models/signals.py`, `django/db/models/query.py`, `django/dispatch/dispatcher.py`
- **Call graph**:
  ```
  Model.save() → post_save.send()
  Model.delete() → post_delete.send()
  Signal.send() → receiver functions
  QuerySet._insert() → mark_for_rollback_on_error()
  ```
- **Key insight**: Django's signal system (`post_save`, `post_delete`, `m2m_changed`) already fires on data changes. Real-time observation would need to:
  1. Register a signal receiver per observed QuerySet
  2. Re-evaluate the QuerySet filter on each signal
  3. Push diffs via WebSocket
- **Integration**: Signals are the hook point; QuerySet's `_result_cache` could track what's "observed"

**Scoring**: Code Location 3, Problem ID 3, Architecture 3, Guidance 2 = **11/12**

#### Auggie Trace (Score: 10/12)

**Response summary**:
- Explained Django signals system
- Described how to combine signals with WebSocket channels
- Referenced Django Channels for WebSocket support
- Good high-level design but less specific about ORM integration

**Scoring**: Code Location 2, Problem ID 3, Architecture 2, Guidance 3 = **10/12**

#### Serena Trace (Score: N/A — not tested on this feature)

---

### Feature 6: Multi-Tenant Row-Level Security

**Query**: "Design a multi-tenant row-level security system in Django that automatically filters queries based on tenant context."

#### XCE Trace (Score: 11/12)

**Tool used**: `xce_get_context`

**Response summary**:
- **Files identified**: `django/db/models/query.py` (QuerySet), `django/db/models/manager.py` (Manager), `django/db/utils.py` (ConnectionRouter)
- **Call graph**:
  ```
  Manager.get_queryset() → QuerySet()
  QuerySet.filter() → Query.add_q()
  ConnectionRouter.db_for_read() → database selection
  ```
- **Key insight**: RLS should be implemented at the Manager level. A `TenantManager` that overrides `get_queryset()` to automatically add `.filter(tenant=current_tenant)` is the cleanest approach. This mirrors how Django's `auth` module uses custom managers.
- **Integration with auth**: `request.user.tenant` provides the context; middleware sets thread-local tenant

**Scoring**: Code Location 3, Problem ID 3, Architecture 3, Guidance 2 = **11/12**

#### Auggie Trace (Score: 9/12)

**Response summary**:
- Good explanation of multi-tenancy patterns
- Suggested middleware + custom Manager approach
- Referenced PostgreSQL RLS as inspiration
- Less specific about Django's Manager/QuerySet integration

**Scoring**: Code Location 2, Problem ID 3, Architecture 2, Guidance 2 = **9/12**

#### Serena Trace (Score: 7/12)

**Response summary**:
- Found `ConnectionRouter` class with methods
- Found `Manager` class
- Precise locations but no design guidance

**Scoring**: Code Location 3, Problem ID 2, Architecture 1, Guidance 1 = **7/12**

---

### Feature 7: GraphQL QuerySet Integration

**Query**: "Design a GraphQL QuerySet integration for Django that compiles GraphQL queries to optimized SQL with automatic dataloader-style N+1 prevention."

#### XCE Trace (Score: 9/12)

**Tool used**: `xce_get_context`

**Response summary**:
- **Files identified**: `django/db/models/sql/compiler.py` (SQLCompiler), `django/db/models/query.py` (select_related, prefetch_related)
- **Call graph**:
  ```
  SQLCompiler.execute_sql() → cursor.execute()
  select_related() → Query.add_select_related() → JOIN generation
  prefetch_related() → prefetch_related_objects() → separate queries
  ```
- **What it found well**: Django's existing N+1 prevention mechanisms (select_related for JOINs, prefetch_related for batched queries)
- **What it missed**: No GraphQL-specific context. XCE's PRAT only indexes Django's codebase, so it can't provide patterns for GraphQL integration that don't exist in Django yet.

**Scoring**: Code Location 3, Problem ID 2, Architecture 2, Guidance 2 = **9/12**

#### Auggie Trace (Score: 10/12)

**Response summary**:
- Explained N+1 problem in GraphQL context
- Referenced dataloader pattern (batching + caching)
- Showed how to map GraphQL field resolution to Django's `select_related`/`prefetch_related`
- Suggested query analysis at GraphQL AST level to determine which relations to prefetch
- Provided conceptual implementation with resolver → QuerySet mapping

**Scoring**: Code Location 2, Problem ID 3, Architecture 2, Guidance 3 = **10/12**

**Why Auggie won**: The problem requires synthesizing knowledge from two domains (GraphQL + Django ORM). Auggie's semantic search found patterns from both domains. XCE only has Django's architecture indexed.

#### Serena Trace (Score: N/A — not tested)

---

### Feature 8: Automatic Query Optimization

**Query**: "Design an automatic query optimization system for Django that analyzes QuerySets and rewrites inefficient patterns."

#### XCE Trace (Score: 11/12)

**Tool used**: `xce_architecture_context` on `django/db/models/sql/query.py`

**Response summary**:
- **Files identified**: `django/db/models/sql/query.py` (Query class), `django/db/models/sql/compiler.py` (SQLCompiler), `django/db/models/query.py` (QuerySet)
- **Call graph**:
  ```
  Query.build_filter() → WhereNode
  Query.join() → Join objects
  Query.set_limits() → LIMIT/OFFSET
  Query.promote_joins() → LEFT JOIN promotion
  Query.resolve_expression() → expression compilation
  SQLCompiler.as_sql() → final SQL generation
  ```
- **Key insight**: Optimization rules could be applied between `Query` construction and `SQLCompiler.as_sql()`. The `Query` object is mutable and can be rewritten before compilation.
- **Optimization opportunities identified**:
  - Subquery → JOIN conversion (when Query has subqueries that could be JOINs)
  - Automatic `select_related` insertion (when filter references related fields)
  - Index hint generation (when Query filters on non-indexed fields)

**Scoring**: Code Location 3, Problem ID 3, Architecture 3, Guidance 2 = **11/12**

#### Auggie Trace (Score: 10/12)

**Response summary**:
- Good explanation of common Django ORM anti-patterns
- Suggested EXPLAIN-based analysis
- Described rule-based optimization (similar to database query planners)
- Less specific about where in Django's code to hook in

**Scoring**: Code Location 2, Problem ID 3, Architecture 2, Guidance 3 = **10/12**

#### Serena Trace (Score: 6/12)

**Response summary**:
- Found `Query` class in `django/db/models/sql/query.py`
- Listed methods but no analysis of optimization points

**Scoring**: Code Location 3, Problem ID 1, Architecture 1, Guidance 1 = **6/12**

---

### Feature 9: Distributed Lock Manager

**Query**: "Design a distributed lock manager for Django that coordinates operations across multiple application instances."

#### XCE Trace (Score: 7/12)

**Tool used**: `xce_get_context`

**Response summary**:
- **Files identified**: `django/db/backends/base/base.py` (BaseDatabaseWrapper), `django/core/cache/backends/` (cache backends)
- **What it found**: Database connection management, schema operations, cache backend interfaces
- **What it missed**: Django doesn't have a lock manager, so XCE's architecture graph has limited relevant nodes. It found database advisory locks (PostgreSQL `pg_advisory_lock`) in the backends but couldn't provide a complete distributed locking design.
- **Partial insight**: Cache backends could serve as lock storage (Redis SETNX pattern)

**Scoring**: Code Location 2, Problem ID 2, Architecture 2, Guidance 1 = **7/12**

#### Auggie Trace (Score: 8/12)

**Response summary**:
- Explained distributed locking patterns (Redis SETNX, ZooKeeper, database advisory locks)
- Described Django's cache framework as a natural fit for lock storage
- Suggested implementation using `cache.add()` (atomic set-if-not-exists)
- Provided timeout and renewal patterns
- Referenced Django's `select_for_update()` for database-level locking

**Scoring**: Code Location 2, Problem ID 2, Architecture 2, Guidance 2 = **8/12**

**Why Auggie won**: Distributed locking is a pattern that exists outside Django. Auggie's semantic search found relevant patterns from Redis/distributed systems knowledge. XCE only has Django's existing architecture.

#### Serena Trace (Score: N/A — not tested)

---

### Feature 10: Event Sourcing Backend

**Query**: "Design an event sourcing backend for Django that stores all model changes as immutable events with full replay capability."

#### XCE Trace (Score: N/A — off-target results)

**Tool used**: `xce_get_context`

**Response summary**:
- XCE returned results focused on `django/contrib/auth/` (authentication) instead of model save/delete signals
- The query "event sourcing" didn't map well to XCE's indexed architecture because event sourcing doesn't exist in Django
- When I refined the query to "Model.save() delete() signals", XCE found relevant code but the initial query failed

**Why XCE failed here**: XCE's PRAT indexes *existing* architecture. "Event sourcing" is a concept that doesn't exist in Django's codebase, so there are no PRAT nodes for it. The semantic gap between "event sourcing" and Django's actual `Model.save()` → `post_save` signal flow was too large for graph traversal to bridge.

**Scoring**: Not scored (off-target results)

#### Auggie Trace (Score: 9/12)

**Response summary**:
- Found `Model.save()` and `Model.delete()` methods
- Identified `post_save` and `post_delete` signals as hook points
- Explained event sourcing pattern: store events instead of state
- Suggested implementation:
  1. Event model storing (model_class, pk, event_type, data, timestamp)
  2. Signal receivers capturing all save/delete operations
  3. Replay mechanism iterating events to reconstruct state
- Discussed migration implications (event replay as alternative to schema migrations)

**Scoring**: Code Location 2, Problem ID 3, Architecture 2, Guidance 2 = **9/12**

**Why Auggie won decisively**: Event sourcing is a well-known pattern in software architecture. Auggie's semantic search found conceptually similar patterns and synthesized them into a Django-specific design. XCE couldn't bridge the gap between "event sourcing" (a concept) and Django's actual code (which doesn't implement it).

#### Serena Trace (Score: N/A — not tested)

---

## Appendix B: SWE-bench Verified Issues Tested

| Issue ID | Title | Area | XCE | Auggie | Serena |
|----------|-------|------|-----|--------|--------|
| django__django-16379 | FileBasedCache race conditions | Cache | 12/12 | 9/12 | 8/12 |
| django__django-16527 | AdminSite catch_all_view APPEND_SLASH | Admin | 11/12 | - | - |
| django__django-16595 | Migration optimizer AlterField | Migrations | 11/12 | - | - |
| django__django-16816 | makemigrations --check exit code | Migrations | 10/12 | - | 11/12 |
| django__django-16910 | QuerySet.only after select_related | ORM | 10/12 | - | - |
| django__django-17051 | bulk_create update_conflicts | ORM | 9/12 | - | 10/12 |
| django__django-16255 | Signer uses SHA-256 | Auth | 10/12 | - | 9/12 |
| django__django-17087 | Class decorators method_decorator | Decorators | 10/12 | - | - |
| django__django-16400 | migrate --run-syncdb custom user | Migrations | 11/12 | - | - |
| django__django-10097 | URLValidator username/password | Validators | 12/12 | 9/12 | 8/12 |

*Note: "-" indicates engine was not tested on that specific issue. Full results for all 35+ issues available in `swe-bench-results/RESULTS.md`*

---

## Appendix C: Scoring Rubric Details

### Code Location (0-3 points)

| Score | Criteria | Example |
|-------|----------|---------|
| 0 | Wrong file or completely off-target | Returns admin code when asked about ORM |
| 1 | Right module/directory but wrong file | Found `django/db/` but wrong file within it |
| 2 | Right file and general area | Found `query.py` and QuerySet class |
| 3 | Exact file, class, method, and line number | `django/db/models/query.py:324 QuerySet.filter()` |

### Problem Identification (0-3 points)

| Score | Criteria | Example |
|-------|----------|---------|
| 0 | No understanding of the problem | Returns unrelated code |
| 1 | Identified the general area | "It's somewhere in the ORM" |
| 2 | Identified root cause partially | "The issue is in filter() but unclear exactly where" |
| 3 | Precise root cause with mechanism | "filter() calls add_q() which doesn't handle deferred fields correctly because..." |

### Architectural Understanding (0-3 points)

| Score | Criteria | Example |
|-------|----------|---------|
| 0 | No module context | Just a code snippet with no context |
| 1 | Single-module context | "This is in the ORM module" |
| 2 | Multi-module awareness | "This affects ORM and admin" |
| 3 | Full cross-module dependency map with call graph | "QuerySet → SQL Compiler → Admin list_display → Auth permissions" |

### Implementation Guidance (0-3 points)

| Score | Criteria | Example |
|-------|----------|---------|
| 0 | No actionable guidance | Just shows code location |
| 1 | Vague direction | "You'd need to modify the ORM" |
| 2 | Specific approach but incomplete | "Override _chain() to add pipeline step" |
| 3 | Complete implementation path | "1. Add pipe() to QuerySet 2. Hook into _chain() 3. Modify SQLCompiler to handle pipeline nodes 4. Update admin to support pipeline display" |

---

*Testing conducted May 2026. Full conversation logs and raw engine outputs available upon request.*
