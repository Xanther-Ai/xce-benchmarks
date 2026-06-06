# Context Engine Comparison: SWE-bench Verified Experiment

## Overview

This experiment compares three context engines for AI coding agents on Django bug fixes from SWE-bench Verified:

1. **Xanther Context Engine (XCE)** — PRAT-based hierarchical graph with architectural context
2. **Augment Code (Auggie)** — Embedding-based semantic search with relationship awareness  
3. **Serena** — LSP-based symbol-level understanding

## Hypothesis

XCE should outperform both Augment and Serena on:
- Cross-module issues requiring architectural understanding
- Deeply nested code requiring HLD→LLD→function hierarchy
- Issues requiring impact analysis to prevent regressions

## Metrics Tracked

| Metric | Description |
|--------|-------------|
| **Time to Locate** | Seconds to find correct file/function |
| **Tool Calls** | Number of MCP tool invocations |
| **Tokens Retrieved** | Context tokens retrieved |
| **Correct Fix** | Does patch resolve the issue? |
| **Tests Pass** | Does fix break existing tests? |
| **Edge Cases** | Does fix handle edge cases? |

## Scoring (per issue)

- **3 points** — Correct fix, no regressions, efficient context
- **2 points** — Correct fix but inefficient
- **1 point** — Partial fix or regressions
- **0 points** — Wrong fix or unable to locate

## Repository Structure

```
swe-bench-results/
├── xanther/           # XCE test results
│   └── issues/        # Individual issue results
├── auggie/            # Augment test results  
│   └── issues/
├── serena/            # Serena test results
│   └── issues/
├── comparison/        # Side-by-side comparisons
└── analysis/          # Aggregated analysis
```

## Test Set

We test **50 Django issues** from SWE-bench Verified, selected across difficulty levels:
- Easy: Simple single-file bugs
- Medium: Multi-file, moderate complexity
- Hard: Cross-module, complex dependencies

## Running the Experiment

Each issue is tested by presenting the bug report to Kiro with one MCP tool enabled at a time. Results are recorded in the respective directory.

## Expected Results

Based on XCE's architecture:
- XCE: 24-27 / 30 (avg)
- Augment: 18-22 / 30
- Serena: 16-20 / 30