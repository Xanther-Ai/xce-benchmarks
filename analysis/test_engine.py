#!/usr/bin/env python3
"""
Test runner for SWE-bench context engine comparison.

This script tests each engine's ability to find relevant code for each issue.
For each issue, we:
1. Extract key search terms from the problem statement
2. Query each engine with those terms
3. Record metrics about the results
"""

import json
import time
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

RESULTS_DIR = Path(__file__).parent

def load_test_issues():
    with open(RESULTS_DIR / "test-issues.json") as f:
        return json.load(f)

def load_problem_statements():
    with open(RESULTS_DIR / "problem_statements.json") as f:
        return {item['instance_id']: item for item in json.load(f)}

def extract_search_terms(problem_statement, instance_id):
    """Extract key search terms from the problem statement."""
    # Add the instance ID as it's often descriptive
    terms = [instance_id.replace("django__django-", "django-")]
    
    # Add key phrases from problem statement
    lines = problem_statement.split('\n')
    for line in lines[:10]:  # First 10 lines are usually most relevant
        line = line.strip()
        if line and len(line) > 10 and not line.startswith('http'):
            # Extract key words
            words = line.split()
            for word in words:
                word = word.strip('.,;:()[]{}')
                if len(word) > 4 and word.lower() not in ['description', 'the', 'this', 'that', 'have', 'been', 'with', 'from', 'will', 'would', 'could', 'should', 'there', 'their', 'these', 'those']:
                    if not word.isupper():  # Skip acronyms
                        terms.append(word)
    
    # Dedupe and return top terms
    terms = list(set(terms))[:5]
    return " ".join(terms)

def record_result(engine, instance_id, result):
    """Record result to JSON file."""
    engine_dir = RESULTS_DIR / engine
    engine_dir.mkdir(exist_ok=True)
    
    result_file = engine_dir / f"{instance_id}.json"
    with open(result_file, 'w') as f:
        json.dump(result, f, indent=2)

def load_result(engine, instance_id):
    """Load previous result."""
    result_file = RESULTS_DIR / engine / f"{instance_id}.json"
    if result_file.exists():
        with open(result_file) as f:
            return json.load(f)
    return None

def get_issues_to_test():
    """Get list of issues that haven't been tested yet for all engines."""
    issues = load_test_issues()
    tested = {'xanther': set(), 'auggie': set(), 'serena': set()}
    
    for engine in tested:
        engine_dir = RESULTS_DIR / engine
        if engine_dir.exists():
            for f in engine_dir.glob("*.json"):
                tested[engine].add(f.stem)
    
    # Find issues that need testing
    pending = []
    for issue in issues:
        instance_id = issue['instance_id']
        needs_test = []
        for engine in ['xanther', 'auggie', 'serena']:
            if instance_id not in tested[engine]:
                needs_test.append(engine)
        if needs_test:
            pending.append((instance_id, needs_test))
    
    return pending

def print_summary():
    """Print summary of test results."""
    issues = load_test_issues()
    
    print("\n" + "="*100)
    print("SWE-bench Verified Context Engine Comparison - Summary")
    print("="*100)
    
    for engine in ['xanther', 'auggie', 'serena']:
        engine_dir = RESULTS_DIR / engine
        count = 0
        if engine_dir.exists():
            count = len(list(engine_dir.glob("*.json")))
        print(f"  {engine}: {count}/{len(issues)} issues tested")
    
    print("="*100)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", choices=["xanther", "auggie", "serena", "all"])
    parser.add_argument("--issue", help="Specific issue ID")
    parser.add_argument("--list", action="store_true", help="List pending tests")
    parser.add_argument("--summary", action="store_true", help="Show summary")
    args = parser.parse_args()
    
    if args.list:
        pending = get_issues_to_test()
        print(f"\nPending tests: {len(pending)}")
        for instance_id, engines in pending[:10]:
            print(f"  {instance_id}: needs {engines}")
    
    elif args.summary:
        print_summary()
    
    else:
        print("Use --list to see pending tests or --summary for overview")