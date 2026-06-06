#!/usr/bin/env python3
"""
Generate prompts for each test issue.
Run this and copy the output to Kiro to test each issue.
"""

import json
import sys
from pathlib import Path

RESULTS_DIR = Path(__file__).parent

def load_issue_details():
    """Load all issue data."""
    with open(RESULTS_DIR / "test-issues.json") as f:
        issues = json.load(f)
    with open(RESULTS_DIR / "problem_statements.json") as f:
        problems = {item['instance_id']: item for item in json.load(f)}
    return issues, problems

def generate_prompt(instance_id):
    """Generate a detailed prompt for an issue."""
    issues, problems = load_issue_details()
    
    # Find the issue
    issue = None
    for i in issues:
        if i['instance_id'] == instance_id:
            issue = i
            break
    
    if not issue:
        print(f"Issue {instance_id} not found")
        return None
    
    problem = problems.get(instance_id, {})
    
    prompt = f"""You are fixing a bug in Django. Here is the issue:

Issue: {instance_id}
Title: {issue['description']}

Problem Statement:
{problem.get('problem_statement', 'No problem statement available.')}

Area: {issue['area']}
Difficulty: {issue['difficulty']}

Use the available context tools to understand the relevant code,
then produce a patch that fixes the issue.

Do NOT modify test files. Only fix the source code.
IMPORTANT: After providing your fix:
1. Verify the fix addresses the root cause
2. Check for any edge cases
3. Ensure no regressions are introduced"""
    
    return prompt

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue", required=True, help="Instance ID")
    parser.add_argument("--show-commit", action="store_true", help="Show base commit")
    args = parser.parse_args()
    
    prompt = generate_prompt(args.issue)
    if prompt:
        print(prompt)
        
        if args.show_commit:
            _, problems = load_issue_details()
            prob = problems.get(args.issue, {})
            print(f"\n\n[Base Commit: {prob.get('base_commit', 'N/A')}]")

if __name__ == "__main__":
    main()