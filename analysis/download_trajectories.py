#!/usr/bin/env python3
"""Download trajectory files from S3 for XCE benchmark runs.

Trajectory files are large (100MB-600MB) and stored in S3 rather than Git.
This script downloads them to a local directory.

Usage:
    python download_trajectories.py --all
    python download_trajectories.py --run sonnet40-xce
    python download_trajectories.py --run minimax-m25-xce --output ./trajectories
"""

import argparse
import os
import subprocess
import sys

S3_BUCKET = "xce-swe-results-859092166013"
S3_PREFIX = "submissions"
S3_REGION = "us-east-1"

RUNS = {
    "sonnet40-xce": [
        "sonnet40-xce/sonnet40-trajectories.tar.gz",
    ],
    "sonnet45-xce": [
        "sonnet45-xce/sonnet45-trajectories.tar.gz",
        "sonnet45-xce/sonnet46-trajectories.tar.gz",
    ],
    "minimax-m25-xce": [
        "minimax-m25-no-reasoning-xce/trajectories.tar.gz",
        "minimax-m25-no-reasoning-xce/minimax-m25-combined-trajectories.tar.gz",
    ],
    "minimax-m25-high-reasoning": [
        "minimax-m25-high-reasoning/minimax-m25-hr-54-trajectories.tar.gz",
        "minimax-m25-high-reasoning/minimax-m25-hr-67-trajectories.tar.gz",
    ],
    "gemini31-xce": [
        "gemini31-xce/gemini31-trajectories.tar.gz",
    ],
}


def download_file(s3_key: str, output_dir: str) -> None:
    """Download a single file from S3."""
    local_path = os.path.join(output_dir, os.path.basename(s3_key))
    if os.path.exists(local_path):
        print(f"  Already exists: {local_path}")
        return

    s3_url = f"s3://{S3_BUCKET}/{S3_PREFIX}/{s3_key}"
    print(f"  Downloading: {s3_url}")
    print(f"  → {local_path}")

    try:
        subprocess.run(
            ["aws", "s3", "cp", s3_url, local_path, "--region", S3_REGION],
            check=True,
        )
        size_mb = os.path.getsize(local_path) / (1024 * 1024)
        print(f"  Done ({size_mb:.1f} MB)")
    except subprocess.CalledProcessError as e:
        print(f"  Failed: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Download XCE benchmark trajectories")
    parser.add_argument("--all", action="store_true", help="Download all runs")
    parser.add_argument("--run", type=str, help="Download a specific run")
    parser.add_argument("--output", type=str, default="./trajectories", help="Output directory")
    parser.add_argument("--list", action="store_true", help="List available runs")
    args = parser.parse_args()

    if args.list:
        print("Available runs:")
        for name, files in RUNS.items():
            total = len(files)
            print(f"  {name} ({total} file{'s' if total > 1 else ''})")
        return

    if not args.all and not args.run:
        parser.print_help()
        return

    runs_to_download = RUNS if args.all else {args.run: RUNS.get(args.run, [])}

    if args.run and args.run not in RUNS:
        print(f"Unknown run: {args.run}")
        print(f"Available: {', '.join(RUNS.keys())}")
        sys.exit(1)

    for run_name, files in runs_to_download.items():
        run_dir = os.path.join(args.output, run_name)
        os.makedirs(run_dir, exist_ok=True)
        print(f"\n{run_name}:")
        for f in files:
            download_file(f, run_dir)

    print("\nDone!")


if __name__ == "__main__":
    main()
