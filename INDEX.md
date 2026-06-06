# XCE Benchmarks - Complete Index

This repository contains comprehensive benchmarking results comparing three context engines (XCE, Auggie, Serena) on Django's 200K-line codebase.

## Quick Navigation

### 📊 Main Results & Analysis
- **[BLOG_POST_context_engines_comparison.md](BLOG_POST_context_engines_comparison.md)** — Full blog post with analysis, visualizations, and detailed findings
- **[SWE_BENCH_RESULTS.md](SWE_BENCH_RESULTS.md)** — Results from 35+ SWE-bench verified bug fixes
- **[complex_feature_test_results.md](complex_feature_test_results.md)** — Results from 10 complex architectural feature tests
- **[10_complex_features.md](10_complex_features.md)** — Detailed feature specifications and test cases

### 📁 Data & Results
- **[results/](results/)** — Machine-readable benchmark data
  - `problem_statements.json` — All problem statements used in testing
  - `test-issues.json` — 35+ SWE-bench issues tested
  - `full_test_results.json` — Complete scoring data for all tests
  - `all_django_issues.json` — Full Django issue database

### 📈 Visualizations
All PNG diagrams available in [assets/](assets/):
- `diagram_1_feature_results.png` — Feature-by-feature scores
- `diagram_2_complexity_curve.png` — Performance vs complexity (with Auggie crossover)
- `diagram_3_response_time.png` — Speed comparison
- `diagram_4_overall_scores.png` — Overall performance
- `diagram_5_token_usage.png` — Context richness comparison
- `diagram_6_architecture.png` — Internal engine architecture
- `diagram_7_when_to_use.png` — Decision guide for engine selection
- `diagram_8_wins_summary.png` — Wins by problem category

### 🔬 Analysis Scripts
Available in [analysis/](analysis/):
- `create_diagrams.py` — Generates all visualizations from results JSON
- `generate_prompts.py` — Creates test prompts from feature specifications
- `test_engine.py` — Test framework used for benchmark runs

### 📖 Additional Resources
- **[EXPERIMENT_README.md](EXPERIMENT_README.md)** — Experimental setup and methodology
- **[LICENSE](LICENSE)** — MIT License

## Key Findings

### Overall Performance
| Engine | SWE-bench | Features | Overall |
|--------|-----------|----------|---------|
| **XCE** | 10.5/12 | 10.3/12 | **10.4/12** |
| Auggie | 10.5/12 | 9.7/12 | 10.1/12 |
| Serena | 11.0/12 | 6.4/12 | 8.7/12 |

### The Complexity Crossover
- **Features 1-6 (Standard)**: XCE 11.0/12 avg, Auggie 9.8/12, Serena 6.2/12
- **Features 7-10 (Novel)**: XCE 8.3/12, Auggie 9.3/12 (Auggie wins!)

### Response Time & Context
| Engine | Response Time | Tokens/Query | Context Type |
|--------|--------------|-------------|--------------|
| Serena | ~1s | ~500 | Symbol + location |
| XCE | ~2s | ~2000+ | Architecture + call graph |
| Auggie | ~3s | ~1500 | Semantic explanation |

## Files by Purpose

### For Understanding the Experiment
1. Start with: [EXPERIMENT_README.md](EXPERIMENT_README.md)
2. Then read: [BLOG_POST_context_engines_comparison.md](BLOG_POST_context_engines_comparison.md) (methodology section)
3. Reference: [10_complex_features.md](10_complex_features.md) for test specifications

### For Analyzing Results
1. Check: [SWE_BENCH_RESULTS.md](SWE_BENCH_RESULTS.md) for bug fix results
2. Review: [complex_feature_test_results.md](complex_feature_test_results.md) for feature design results
3. Visualize: View PNG diagrams in [assets/](assets/)

### For Reproducing the Experiment
1. Load data: `results/*.json`
2. Run analysis: `analysis/create_diagrams.py`
3. Generate prompts: `analysis/generate_prompts.py`
4. Test engines: `analysis/test_engine.py`

### For Machine Learning Use Cases
1. Download: `results/full_test_results.json` — Complete scoring data
2. Reference: `results/test-issues.json` — Test case IDs
3. Use with: Any ML model evaluation framework

## Test Coverage

### SWE-bench Verified Issues
- **35+ issues** from Django codebase
- **3 test engines** (XCE, Auggie, Serena)
- **4 scoring criteria** per issue (code location, problem identification, architecture, implementation guidance)
- **12-point rubric** with LLM-as-Judge validation

### Complex Architectural Features
- **10 features** requiring multi-module design
- **3 test engines** (XCE, Auggie, Serena)
- **Complexity crossover analysis** showing where each engine excels
- **Traces & traces** for all 10 features (see blog post appendix)

## How to Use This Repository

### As a Researcher
- Download `results/full_test_results.json` for statistical analysis
- Review scoring rubric in [BLOG_POST_context_engines_comparison.md](BLOG_POST_context_engines_comparison.md#scoring-methodology)
- Cite the experiment using the DOI/reference in the repo

### As a Developer
- Read [BLOG_POST_context_engines_comparison.md](BLOG_POST_context_engines_comparison.md#practical-recommendations) for decision matrix
- Use [assets/diagram_7_when_to_use.png](assets/diagram_7_when_to_use.png) to choose the right engine
- Reference [10_complex_features.md](10_complex_features.md) for design patterns

### As a Tool Builder
- Study the [scoring methodology](BLOG_POST_context_engines_comparison.md#scoring-methodology) for benchmarking context engines
- Review [analysis/](analysis/) scripts for reproducibility
- Use JSON data formats as a standard for context engine evaluation

## Scoring Methodology Summary

**12-Point Rubric** with 4 criteria (3 points each):
1. **Code Location** — Accuracy of file/function identification
2. **Problem Identification** — Root cause analysis depth
3. **Architectural Understanding** — Cross-module dependency mapping
4. **Implementation Guidance** — Completeness of solution path

See full methodology in [BLOG_POST_context_engines_comparison.md#scoring-methodology](BLOG_POST_context_engines_comparison.md#scoring-methodology-llm-as-judge-with-structured-rubric).

## Data Formats

### problem_statements.json
```json
{
  "features": [
    {
      "id": 1,
      "name": "QuerySet Pipeline API",
      "description": "Design a QuerySet pipeline API...",
      "query": "Design a QuerySet pipeline API in Django..."
    }
  ]
}
```

### test-issues.json
```json
{
  "issues": [
    {
      "id": "issue_1",
      "title": "Bug title",
      "description": "Bug description",
      "files": ["django/db/models/query.py"]
    }
  ]
}
```

### full_test_results.json
```json
{
  "results": [
    {
      "test_id": "issue_1",
      "engine": "xce",
      "scores": {
        "code_location": 3,
        "problem_identification": 3,
        "architecture": 3,
        "implementation": 2
      },
      "total": 11,
      "timestamp": "2026-05-24T..."
    }
  ]
}
```

## Citation

If you use this benchmark in your research, please cite:

```bibtex
@benchmark{xce-benchmarks-2026,
  title={Context Engine Comparison: XCE vs Auggie vs Serena on Django},
  author={Bhattacharya, Raj},
  year={2026},
  repository={https://github.com/Xanther-Ai/xce-benchmarks},
  note={35+ SWE-bench issues, 10 architectural features}
}
```

## License

This repository is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Support & Questions

For questions about:
- **Methodology**: See [BLOG_POST_context_engines_comparison.md#scoring-methodology](BLOG_POST_context_engines_comparison.md#scoring-methodology-llm-as-judge-with-structured-rubric)
- **Reproduction**: See [analysis/](analysis/) scripts
- **Results interpretation**: See [complex_feature_test_results.md](complex_feature_test_results.md)

---

**Last Updated**: June 5, 2026  
**Experiment Timeframe**: May-June 2026  
**Codebase**: Django 5.0+ main branch (~200,000 lines)
