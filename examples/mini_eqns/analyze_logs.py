#!/usr/bin/env python3
"""
Script to analyze LLM interaction logs from the baseline experiment
to understand feedback loop usage patterns.
"""

import yaml
from pathlib import Path
from collections import defaultdict, Counter


def analyze_single_result(result_file: Path) -> dict:
    """Analyze a single result file."""
    with open(result_file, 'r') as f:
        data = yaml.safe_load(f)

    if not data.get('outcome', {}).get('result', {}).get('success'):
        return {"success": False}

    log = data['outcome']['result'].get('log', [])

    analysis = {
        "success": True,
        "total_requests": 0,
        "parse_errors": 0,
        "feedback_cycles": 0,
        "first_attempt_success": False,
        "budget": data['outcome']['result'].get('spent_budget', {}),
        "equation": data['args']['args']['equality'],
    }

    llm_requests = [entry for entry in log if entry.get('message') == 'llm_request']
    parse_errors = [entry for entry in log if entry.get('message') == 'parse_error']

    analysis["total_requests"] = len(llm_requests)
    analysis["parse_errors"] = len(parse_errors)

    # Count feedback cycles (requests after the first one indicate feedback)
    analysis["feedback_cycles"] = max(0, analysis["total_requests"] - 1)
    analysis["first_attempt_success"] = analysis["feedback_cycles"] == 0

    # Analyze the specific types of errors/feedback
    feedback_reasons = []
    for entry in log:
        if entry.get('message') == 'parse_error':
            error_desc = entry.get('metadata', {}).get('error', {}).get('description', '')
            feedback_reasons.append(f"parse_error: {error_desc[:100]}...")
        # Look for feedback content in requests
        elif entry.get('message') == 'llm_request':
            chat = entry.get('metadata', {}).get('request', {}).get('chat', [])
            for msg in chat:
                if msg.get('role') == 'user' and 'did not check successfully' in msg.get('content', ''):
                    feedback_content = msg['content']
                    # Extract the error message
                    if '```' in feedback_content:
                        error_start = feedback_content.find('```') + 3
                        error_end = feedback_content.find('```', error_start)
                        if error_end > error_start:
                            error_msg = feedback_content[error_start:error_end].strip()
                            feedback_reasons.append(f"checker_error: {error_msg}")

    analysis["feedback_reasons"] = feedback_reasons

    return analysis


def analyze_all_results():
    """Analyze all result files in the experiment output."""
    results_dir = Path("/home/guille/anaconda3/envs/guille/delphyne/examples/mini_eqns/experiments/output/baseline_experiment/configs")

    all_analyses = []
    success_count = 0

    for result_file in results_dir.glob("*/result.yaml"):
        analysis = analyze_single_result(result_file)
        analysis["config_name"] = result_file.parent.name
        all_analyses.append(analysis)
        if analysis["success"]:
            success_count += 1

    print(f"=== Overall Statistics ===")
    print(f"Total experiments: {len(all_analyses)}")
    print(f"Successful experiments: {success_count}")
    print(f"Success rate: {success_count/len(all_analyses)*100:.1f}%")
    print()

    # Analyze feedback patterns
    first_attempt_successes = sum(1 for a in all_analyses if a.get("first_attempt_success"))
    print(f"=== Feedback Loop Analysis ===")
    print(f"First attempt successes: {first_attempt_successes}/{success_count} ({first_attempt_successes/success_count*100:.1f}%)")
    print(f"Required feedback: {success_count - first_attempt_successes}/{success_count} ({(success_count - first_attempt_successes)/success_count*100:.1f}%)")
    print()

    # Distribution of feedback cycles
    feedback_distribution = Counter(a.get("feedback_cycles", 0) for a in all_analyses if a["success"])
    print(f"Distribution of feedback cycles needed:")
    for cycles in sorted(feedback_distribution.keys()):
        count = feedback_distribution[cycles]
        print(f"  {cycles} cycles: {count} experiments ({count/success_count*100:.1f}%)")
    print()

    # Analyze by equation
    equation_stats = defaultdict(list)
    for analysis in all_analyses:
        if analysis["success"]:
            eq = tuple(analysis["equation"])
            equation_stats[eq].append(analysis)

    print(f"=== Per-Equation Analysis ===")
    for eq, analyses in equation_stats.items():
        avg_cycles = sum(a.get("feedback_cycles", 0) for a in analyses) / len(analyses)
        first_attempt_rate = sum(1 for a in analyses if a.get("first_attempt_success")) / len(analyses) * 100
        print(f"{eq[0]} = {eq[1]}")
        print(f"  Avg feedback cycles: {avg_cycles:.1f}")
        print(f"  First attempt success: {first_attempt_rate:.1f}%")
        print(f"  Total runs: {len(analyses)}")
    print()

    # Analyze specific feedback reasons
    all_feedback_reasons = []
    for analysis in all_analyses:
        all_feedback_reasons.extend(analysis.get("feedback_reasons", []))

    if all_feedback_reasons:
        print(f"=== Feedback Reasons Analysis ===")
        reason_types = Counter()
        for reason in all_feedback_reasons:
            if reason.startswith("parse_error"):
                reason_types["Parse Errors"] += 1
            elif reason.startswith("checker_error"):
                reason_types["Checker Errors"] += 1
            else:
                reason_types["Other"] += 1

        for reason_type, count in reason_types.most_common():
            print(f"{reason_type}: {count}")

        # Show some specific examples
        print("\nExample feedback reasons:")
        for reason in all_feedback_reasons[:5]:
            print(f"  - {reason}")
    else:
        print("=== Feedback Reasons Analysis ===")
        print("No feedback reasons found (all first-attempt successes)")

    print()

    # Budget analysis
    total_cost = sum(a.get("budget", {}).get("price", 0) for a in all_analyses if a["success"])
    avg_requests = sum(a.get("total_requests", 0) for a in all_analyses if a["success"]) / success_count

    print(f"=== Budget Analysis ===")
    print(f"Total cost: ${total_cost:.4f}")
    print(f"Average cost per experiment: ${total_cost/success_count:.4f}")
    print(f"Average requests per experiment: {avg_requests:.1f}")

    return all_analyses


if __name__ == "__main__":
    analyses = analyze_all_results()