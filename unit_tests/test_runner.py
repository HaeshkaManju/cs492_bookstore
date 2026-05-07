#!/usr/bin/env python3
"""
Test Runner with Grouped Reporting

This script runs pytest with categorized test groups and produces
a formatted report showing pass/fail status for each category.

Usage:
    python test_runner.py                    # Run all tests
    python test_runner.py --group auth       # Run only auth tests
    python test_runner.py --group database   # Run only database tests
    python test_runner.py --verbose          # Show detailed output
    python test_runner.py --report           # Generate HTML report

Test Groups:
    - auth: Authentication and authorization tests
    - database: Database schema and model tests
    - inventory: Inventory management tests
    - sales: Sales and invoice tests
    - orders: Purchase order tests
    - integration: Cross-module integration tests
    - all: Run all test groups
"""

import argparse
import subprocess
import sys
import json
import os
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional
from pathlib import Path


@dataclass
class TestResult:
    """Result of a test group execution."""
    group: str
    passed: int
    failed: int
    skipped: int
    errors: int
    duration: float
    failed_tests: List[str]


@dataclass
class TestReport:
    """Complete test report."""
    timestamp: str
    total_passed: int
    total_failed: int
    total_skipped: int
    total_errors: int
    total_duration: float
    groups: List[TestResult]
    overall_status: str


# Test group definitions
TEST_GROUPS = {
    'structure': {
        'path': 'tests/unit/test_structure.py',
        'description': 'Project structure validation',
        'markers': [],
    },
    'environment': {
        'path': 'tests/unit/test_environment.py',
        'description': 'Development environment tests',
        'markers': [],
    },
    'auth': {
        'path': 'tests/unit/test_auth.py tests/integration/test_auth_flow.py',
        'description': 'Authentication and authorization',
        'markers': ['auth'],
    },
    'database': {
        'path': 'tests/unit/test_models.py tests/integration/test_database.py',
        'description': 'Database schema and models',
        'markers': ['database'],
    },
    'inventory': {
        'path': 'tests/unit/test_inventory.py tests/integration/test_inventory.py',
        'description': 'Inventory management',
        'markers': ['inventory'],
    },
    'sales': {
        'path': 'tests/unit/test_sales.py tests/integration/test_invoice.py',
        'description': 'Sales and invoicing',
        'markers': ['sales'],
    },
    'orders': {
        'path': 'tests/unit/test_orders.py tests/integration/test_purchase_orders.py',
        'description': 'Purchase orders',
        'markers': ['orders'],
    },
    'requests': {
        'path': 'tests/unit/test_requests.py tests/integration/test_book_requests.py',
        'description': 'Book request system',
        'markers': ['requests'],
    },
    'integration': {
        'path': 'tests/integration/',
        'description': 'Cross-module integration',
        'markers': ['integration'],
    },
    'security': {
        'path': 'tests/security/',
        'description': 'Security tests',
        'markers': ['security'],
    },
}


def run_test_group(group_name: str, group_config: dict, verbose: bool = False) -> TestResult:
    """
    Run a single test group and parse results.
    
    Args:
        group_name: Name of the test group
        group_config: Configuration for the test group
        verbose: Whether to show detailed output
    
    Returns:
        TestResult with pass/fail counts
    """
    print(f"\n{'='*60}")
    print(f"Running: {group_name} - {group_config['description']}")
    print(f"{'='*60}")
    
    # Build pytest command
    cmd = ['pytest', '--tb=short', '-q']
    
    # Add JSON report for parsing
    json_file = f'/tmp/pytest_{group_name}.json'
    cmd.extend(['--json-report', f'--json-report-file={json_file}'])
    
    # Add paths
    for path in group_config['path'].split():
        if os.path.exists(path):
            cmd.append(path)
    
    # Add markers if specified
    for marker in group_config.get('markers', []):
        cmd.extend(['-m', marker])
    
    if verbose:
        cmd.append('-v')
    
    # Run pytest
    start_time = datetime.now()
    try:
        result = subprocess.run(
            cmd,
            capture_output=not verbose,
            text=True
        )
    except FileNotFoundError:
        print(f"Error: pytest not found. Install with: pip install pytest pytest-json-report")
        return TestResult(
            group=group_name,
            passed=0, failed=0, skipped=0, errors=1,
            duration=0, failed_tests=['pytest not found']
        )
    
    duration = (datetime.now() - start_time).total_seconds()
    
    # Parse JSON report if available
    passed = failed = skipped = errors = 0
    failed_tests = []
    
    if os.path.exists(json_file):
        try:
            with open(json_file) as f:
                report = json.load(f)
                summary = report.get('summary', {})
                passed = summary.get('passed', 0)
                failed = summary.get('failed', 0)
                skipped = summary.get('skipped', 0)
                errors = summary.get('error', 0)
                
                # Get failed test names
                for test in report.get('tests', []):
                    if test.get('outcome') == 'failed':
                        failed_tests.append(test.get('nodeid', 'unknown'))
            
            os.remove(json_file)
        except (json.JSONDecodeError, KeyError):
            pass
    
    # Print summary
    status = '✓ PASSED' if (failed + errors) == 0 else '✗ FAILED'
    print(f"\n{status}: {passed} passed, {failed} failed, {skipped} skipped")
    
    if failed_tests:
        print("\nFailed tests:")
        for test in failed_tests[:5]:  # Show first 5
            print(f"  - {test}")
        if len(failed_tests) > 5:
            print(f"  ... and {len(failed_tests) - 5} more")
    
    return TestResult(
        group=group_name,
        passed=passed,
        failed=failed,
        skipped=skipped,
        errors=errors,
        duration=duration,
        failed_tests=failed_tests
    )


def run_all_tests(groups: List[str], verbose: bool = False) -> TestReport:
    """
    Run specified test groups and compile report.
    
    Args:
        groups: List of group names to run
        verbose: Whether to show detailed output
    
    Returns:
        Complete TestReport
    """
    results = []
    
    for group_name in groups:
        if group_name in TEST_GROUPS:
            result = run_test_group(group_name, TEST_GROUPS[group_name], verbose)
            results.append(result)
        else:
            print(f"Warning: Unknown test group '{group_name}'")
    
    # Compile totals
    total_passed = sum(r.passed for r in results)
    total_failed = sum(r.failed for r in results)
    total_skipped = sum(r.skipped for r in results)
    total_errors = sum(r.errors for r in results)
    total_duration = sum(r.duration for r in results)
    
    overall_status = 'PASSED' if (total_failed + total_errors) == 0 else 'FAILED'
    
    return TestReport(
        timestamp=datetime.now().isoformat(),
        total_passed=total_passed,
        total_failed=total_failed,
        total_skipped=total_skipped,
        total_errors=total_errors,
        total_duration=total_duration,
        groups=results,
        overall_status=overall_status
    )


def print_report(report: TestReport) -> None:
    """Print formatted test report to console."""
    print("\n" + "="*60)
    print("TEST REPORT")
    print("="*60)
    print(f"Timestamp: {report.timestamp}")
    print(f"Duration: {report.total_duration:.2f}s")
    print()
    
    # Group results table
    print(f"{'Group':<15} {'Passed':<10} {'Failed':<10} {'Skipped':<10} {'Status':<10}")
    print("-"*60)
    
    for result in report.groups:
        status = '✓' if (result.failed + result.errors) == 0 else '✗'
        print(f"{result.group:<15} {result.passed:<10} {result.failed:<10} {result.skipped:<10} {status:<10}")
    
    print("-"*60)
    print(f"{'TOTAL':<15} {report.total_passed:<10} {report.total_failed:<10} {report.total_skipped:<10}")
    print()
    
    # Overall status
    if report.overall_status == 'PASSED':
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
        print("\nFailed tests by group:")
        for result in report.groups:
            if result.failed_tests:
                print(f"\n  {result.group}:")
                for test in result.failed_tests:
                    print(f"    - {test}")
    
    print()


def generate_html_report(report: TestReport, output_path: str = 'test_report.html') -> None:
    """Generate HTML test report."""
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Test Report - {report.timestamp}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        .summary {{ background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .passed {{ color: #22863a; }}
        .failed {{ color: #cb2431; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background: #f5f5f5; }}
        tr:nth-child(even) {{ background: #fafafa; }}
        .status-pass {{ background: #dcffe4; }}
        .status-fail {{ background: #ffeef0; }}
    </style>
</head>
<body>
    <h1>Test Report</h1>
    
    <div class="summary">
        <p><strong>Timestamp:</strong> {report.timestamp}</p>
        <p><strong>Duration:</strong> {report.total_duration:.2f}s</p>
        <p><strong>Status:</strong> 
            <span class="{'passed' if report.overall_status == 'PASSED' else 'failed'}">
                {report.overall_status}
            </span>
        </p>
    </div>
    
    <h2>Results by Group</h2>
    <table>
        <tr>
            <th>Group</th>
            <th>Passed</th>
            <th>Failed</th>
            <th>Skipped</th>
            <th>Duration</th>
            <th>Status</th>
        </tr>
        {''.join(f'''
        <tr class="{'status-pass' if r.failed == 0 else 'status-fail'}">
            <td>{r.group}</td>
            <td>{r.passed}</td>
            <td>{r.failed}</td>
            <td>{r.skipped}</td>
            <td>{r.duration:.2f}s</td>
            <td>{'✓ Pass' if r.failed == 0 else '✗ Fail'}</td>
        </tr>
        ''' for r in report.groups)}
        <tr style="font-weight: bold;">
            <td>TOTAL</td>
            <td>{report.total_passed}</td>
            <td>{report.total_failed}</td>
            <td>{report.total_skipped}</td>
            <td>{report.total_duration:.2f}s</td>
            <td></td>
        </tr>
    </table>
    
    {'<h2>Failed Tests</h2><ul>' + ''.join(f'<li>{t}</li>' for r in report.groups for t in r.failed_tests) + '</ul>' if report.total_failed > 0 else ''}
</body>
</html>
"""
    
    with open(output_path, 'w') as f:
        f.write(html)
    
    print(f"HTML report generated: {output_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Run tests with grouped reporting',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python test_runner.py                    # Run all tests
    python test_runner.py --group auth       # Run auth tests only
    python test_runner.py --group auth database  # Run multiple groups
    python test_runner.py --verbose          # Detailed output
    python test_runner.py --report           # Generate HTML report

Available groups:
    """ + '\n    '.join(f'{name}: {cfg["description"]}' for name, cfg in TEST_GROUPS.items())
    )
    
    parser.add_argument(
        '--group', '-g',
        nargs='+',
        default=list(TEST_GROUPS.keys()),
        choices=list(TEST_GROUPS.keys()) + ['all'],
        help='Test group(s) to run'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed test output'
    )
    parser.add_argument(
        '--report', '-r',
        action='store_true',
        help='Generate HTML report'
    )
    parser.add_argument(
        '--output', '-o',
        default='test_report.html',
        help='HTML report output path'
    )
    
    args = parser.parse_args()
    
    # Handle 'all' group
    groups = list(TEST_GROUPS.keys()) if 'all' in args.group else args.group
    
    # Run tests
    report = run_all_tests(groups, args.verbose)
    
    # Print report
    print_report(report)
    
    # Generate HTML if requested
    if args.report:
        generate_html_report(report, args.output)
    
    # Exit with appropriate code
    sys.exit(0 if report.overall_status == 'PASSED' else 1)


if __name__ == '__main__':
    main()
