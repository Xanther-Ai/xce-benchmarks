# XCE Benchmarks: Comparative Analysis of Context Engines

**Can a context engine make a weaker model perform like a frontier model?**

This repository contains comprehensive benchmarking results comparing three context engines on Django's 200K-line codebase.

## Quick Start

👉 **Start here**: Read the [BLOG_POST_context_engines_comparison.md](BLOG_POST_context_engines_comparison.md) for the full analysis with visualizations.

📊 **TL;DR Results**:
- **XCE wins overall** (10.4/12 avg) on standard complexity problems
- **Auggie wins on novel complexity** (9.3/12 on Features 7-10) where new patterns matter
- **Serena wins on speed** (1 second response time) but loses on architectural depth
- **Key finding**: There's a complexity crossover where Auggie surpasses XCE as problems become more novel

## What's In This Repository

### 📖 Documentation

| File | Purpose |
|------|---------|
| [BLOG_POST_context_engines_comparison.md](BLOG_POST_context_engines_comparison.md) | **Main analysis** — Full blog post with methodology, results, and visualizations |
| [INDEX.md](INDEX.md) | **Navigation guide** — Organized index of all files by purpose |
| [SWE_BENCH_RESULTS.md](SWE_BENCH_RESULTS.md) | **Bug fix results** — 35+ SWE-bench verified Django issues |
| [complex_feature_test_results.md](complex_feature_test_results.md) | **Feature design results** — 10 architectural feature design tasks |
| [10_complex_features.md](10_complex_features.md) | **Feature specifications** — Detailed descriptions of all 10 test features |
| [EXPERIMENT_README.md](EXPERIMENT_README.md) | **Setup & methodology** — Experimental configuration and approach |

### 📊 Results Data

All data in JSON format for machine learning and statistical analysis:

| File | Contains |
|------|----------|
| [results/full_test_results.json](results/full_test_results.json) | All scoring data (35+ issues × 3 engines) |
| [results/problem_statements.json](results/problem_statements.json) | All 10 feature specifications |
| [results/test-issues.json](results/test-issues.json) | All 35+ SWE-bench issue IDs and metadata |
| [results/all_django_issues.json](results/all_django_issues.json) | Complete Django issue database |

### 📈 Visualizations

8 high-quality PNG diagrams in [assets/](assets/):

1. **diagram_1_feature_results.png** — Feature scores for all 10 problems
2. **diagram_2_complexity_curve.png** — Performance vs complexity (shows crossover)
3. **diagram_3_response_time.png** — Speed comparison
4. **diagram_4_overall_scores.png** — Overall performance summary
5. **diagram_5_token_usage.png** — Context richness comparison
6. **diagram_6_architecture.png** — How each engine works internally
7. **diagram_7_when_to_use.png** — Decision matrix for engine selection
8. **diagram_8_wins_summary.png** — Wins by problem category

All diagrams hosted on AWS S3 CDN for web distribution.

### 🔬 Analysis & Scripts

Python scripts in [analysis/](analysis/) for reproducibility:

| Script | Purpose |
|--------|---------|
| `create_diagrams.py` | Regenerate all PNG visualizations from results JSON |
| `generate_prompts.py` | Create test prompts from feature specifications |
| `test_engine.py` | Framework used to benchmark each engine |

## Key Results

### Overall Scores (12-point scale)

```
XCE:    10.4/12  ████████████ 86.7%  ← Overall winner
Auggie: 10.1/12  ███████████  84.2%
Serena:  8.7/12  ██████████   72.5%
```

### By Problem Type

| Problem Type | XCE | Auggie | Serena | Winner |
|--------------|-----|--------|--------|--------|
| **SWE-bench (35+ bugs)** | 10.5/12 | 10.5/12 | 11.0/12 | Serena |
| **Standard features (1-6)** | 11.0/12 | 9.8/12 | 6.2/12 | XCE |
| **Novel features (7-10)** | 8.3/12 | **9.3/12** | N/A | Auggie ⭐ |

### The Complexity Crossover (Key Finding)

As problem complexity increases beyond existing Django patterns, Auggie (semantic search) surpasses XCE (graph-based):

```
Performance vs Novelty
│
│   XCE ╱╱╱╱╱╱╱╱
│      ╱        ╲
│     ╱          ╲
│    ╱            ╲╱╱╱╱╱ Auggie
│   ╱            ╱
│  ╱____________╱
│  Standard              Novel
└─────────────────────────────

Crossover at: Feature 6-7 boundary
```

### Response Time & Context Quality

| Engine | Response Time | Tokens/Query | Tokens/Second | Best For |
|--------|--------------|-------------|---------------|----------|
| Serena | ~1 second | ~500 | ~500 | Quick lookups |
| XCE | ~2 seconds | ~2000+ | ~1000 | Architecture |
| Auggie | ~3 seconds | ~1500 | ~500 | Novel design |

## Scoring Methodology

Each response scored on 4 criteria (3 points each = 12 points max):

1. **Code Location** (0-3 pts)
   - 0: Wrong file/function
   - 3: Exact file, function, and line

2. **Problem Identification** (0-3 pts)
   - 0: Missed the issue entirely
   - 3: Precise root cause with explanation

3. **Architectural Understanding** (0-3 pts)
   - 0: No module context
   - 3: Full cross-module dependency map

4. **Implementation Guidance** (0-3 pts)
   - 0: No actionable guidance
   - 3: Complete implementation path with integration points

**Methodology**: LLM-as-Judge with fixed rubric + manual verification (~20% sample)

See full methodology in [BLOG_POST_context_engines_comparison.md](BLOG_POST_context_engines_comparison.md#scoring-methodology-llm-as-judge-with-structured-rubric).

## Test Coverage

### SWE-bench Verified Bug Fixes
- **35+ real Django bugs** from SWE-bench
- **3 engines tested** (XCE, Auggie, Serena)
- **Includes**: ForeignKey CASCADE deletion bug (unfixed in Django main), transaction handling, ORM edge cases

### Complex Architectural Features
- **10 features** requiring novel design
- **3 engines tested** (XCE, Auggie, Serena for first 6; XCE/Auggie for 7-10)
- **All traces included** — Complete query/response pairs in blog post appendix

**Features tested**:
1. QuerySet Pipeline API
2. Cross-Database Transaction Coordinator
3. Dynamic Model Schema Evolution
4. Unified Caching Layer
5. Real-time QuerySet Observations
6. Multi-Tenant Row-Level Security
7. GraphQL QuerySet Integration ⭐ Auggie wins
8. Automatic Query Optimization
9. Distributed Lock Manager ⭐ Auggie wins
10. Event Sourcing Backend ⭐ Auggie wins

## How to Use This Repository

### 🎓 For Researchers
```bash
# 1. Download results data
# results/full_test_results.json contains all scoring

# 2. Run statistical analysis
python analysis/create_diagrams.py  # Regenerate visualizations

# 3. Compare with your own benchmarks
# Use the 12-point rubric as a standard
```

### 👨‍💻 For Developers
```bash
# 1. Decide which engine to use
# See: assets/diagram_7_when_to_use.png

# 2. Understand the decision matrix
# Read: BLOG_POST section "Practical Recommendations"

# 3. Check if your problem type was tested
# See: complex_feature_test_results.md
```

### 🔧 For Tool Builders
```bash
# 1. Study the scoring methodology
# Read: BLOG_POST "Scoring Methodology" section

# 2. Understand context engine architectures
# See: BLOG_POST sections on Auggie, Serena, XCE

# 3. Use JSON data as a benchmark standard
# Format: results/full_test_results.json
```

### 📊 For Data Scientists
```bash
# 1. Load the results
import json
with open('results/full_test_results.json') as f:
    results = json.load(f)

# 2. Analyze by category
# Features 1-6: Standard complexity
# Features 7-10: Novel complexity
# Plus: 35+ SWE-bench bug fixes

# 3. Examine the complexity curve
# Plot engine performance vs novelty
```

## Files by Purpose

### To Understand the Experiment
1. Start: [EXPERIMENT_README.md](EXPERIMENT_README.md)
2. Read: [BLOG_POST_context_engines_comparison.md](BLOG_POST_context_engines_comparison.md) (Background + Methodology sections)
3. Reference: [10_complex_features.md](10_complex_features.md) for test specifications

### To Analyze the Results
1. Check: [SWE_BENCH_RESULTS.md](SWE_BENCH_RESULTS.md) — Bug fix scores
2. Review: [complex_feature_test_results.md](complex_feature_test_results.md) — Feature design scores
3. Visualize: [assets/](assets/) — All diagrams with S3 CDN URLs

### To Reproduce the Experiment
1. Load: `results/*.json` — All benchmark data
2. Generate: `python analysis/generate_prompts.py`
3. Test: `python analysis/test_engine.py`
4. Visualize: `python analysis/create_diagrams.py`

### To Use in Machine Learning
```python
import json

# Load scoring data
with open('results/full_test_results.json') as f:
    scores = json.load(f)

# Load test cases
with open('results/test-issues.json') as f:
    issues = json.load(f)

# Load problem statements
with open('results/problem_statements.json') as f:
    problems = json.load(f)

# Ready for ML evaluation framework
```

## Key Insights

### 1. Context Matters More Than Model Size
With proper context, a smaller model performs like a frontier model. The context engine is the bottleneck, not the model.

### 2. Different Engines Excel at Different Problems
- **XCE**: Dominates on standard problems (extending existing patterns)
- **Auggie**: Wins on novel problems (creating new patterns)
- **Serena**: Fastest but shallowest—good for quick lookups

### 3. The Complexity Crossover (Surprising Finding)
As problems become more novel (beyond existing Django architecture), Auggie's embedding-based semantic search actually outperforms XCE's graph-based hierarchical approach. This suggests a phase transition in how reasoning about code changes as we move from "extending existing patterns" to "inventing new patterns."

### 4. PRAT Makes XCE Faster Despite Richer Output
XCE returns 4× more context than Serena (~2000 tokens vs ~500) but responds 2× faster (2s vs ~3s for Auggie). This is because PRAT pre-computes architectural relationships at index time, enabling O(log n) query time instead of O(n) vector search.

## Citation

If you use this benchmark, please cite:

```bibtex
@benchmark{xce-benchmarks-2026,
  title={Context Engine Comparison: XCE vs Auggie vs Serena on Django},
  author={Bhattacharya, Raj},
  year={2026},
  repository={https://github.com/Xanther-Ai/xce-benchmarks},
  note={35+ SWE-bench issues, 10 architectural features, 12-point rubric}
}
```

## License

MIT License — See [LICENSE](LICENSE) for details.

## Navigation

- 📖 **Full Analysis**: [BLOG_POST_context_engines_comparison.md](BLOG_POST_context_engines_comparison.md)
- 📇 **File Index**: [INDEX.md](INDEX.md)
- 📊 **Results Data**: [results/](results/)
- 📈 **Visualizations**: [assets/](assets/)
- 🔬 **Scripts**: [analysis/](analysis/)

---

**Benchmark Date**: May-June 2026  
**Codebase**: Django 5.0+ main branch (~200,000 lines)  
**Engines Tested**: Xanther Context Engine (XCE), Augment Code (Auggie), Serena (LSP-based)  
**Issues Evaluated**: 35+ SWE-bench + 10 complex architectural features  
**Scoring**: 12-point rubric with LLM-as-Judge validation
