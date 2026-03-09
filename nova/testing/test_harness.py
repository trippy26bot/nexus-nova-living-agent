#!/usr/bin/env python3
"""
Full Test Harness - Run all system tests
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from nova.testing.system_validator import validate_modules, print_results as print_module_results
from nova.testing.security_scanner import scan_directory as scan_security, print_security_report
from nova.testing.file_integrity import check_integrity, print_integrity_report
from nova.testing.bug_finder import scan_directory as scan_bugs, print_bug_report

def run_full_system_test(nova_root: str = "nova") -> dict:
    """Run complete system validation"""
    report = {
        "timestamp": None,
        "module_validation": {},
        "security_scan": {},
        "integrity_check": {},
        "bug_scan": {},
        "overall_passed": False
    }
    
    print("\n" + "=" * 60)
    print("🧪 NOVA FULL SYSTEM TEST")
    print("=" * 60 + "\n")
    
    # 1. Module validation
    print("📦 Testing module imports...")
    report["module_validation"] = validate_modules()
    print_module_results(report["module_validation"])
    
    # 2. Security scan
    print("\n🔐 Running security scan...")
    report["security_scan"] = scan_security(nova_root)
    print_security_report(report["security_scan"])
    
    # 3. Integrity check
    print("\n📁 Checking file integrity...")
    report["integrity_check"] = check_integrity(nova_root)
    print_integrity_report(report["integrity_check"])
    
    # 4. Bug scan
    print("\n🐛 Scanning for bugs...")
    report["bug_scan"] = scan_bugs(nova_root)
    print_bug_report(report["bug_scan"])
    
    # Overall result
    modules_ok = all(r["status"] == "OK" for r in report["module_validation"].values())
    security_ok = len(report["security_scan"]["issues"]) == 0
    integrity_ok = (len(report["integrity_check"]["modified_files"]) == 0 and 
                   len(report["integrity_check"]["deleted_files"]) == 0)
    bugs_ok = len(report["bug_scan"]["issues"]) == 0
    
    report["overall_passed"] = modules_ok and security_ok and integrity_ok and bugs_ok
    
    print("\n" + "=" * 60)
    print("📊 OVERALL RESULTS")
    print("=" * 60)
    print(f"✅ Module validation: {'PASS' if modules_ok else 'FAIL'}")
    print(f"🔐 Security scan: {'PASS' if security_ok else 'FAIL'}")
    print(f"📁 File integrity: {'PASS' if integrity_ok else 'FAIL'}")
    print(f"🐛 Bug scan: {'PASS' if bugs_ok else 'FAIL'}")
    print("=" * 60)
    print(f"\n🎯 OVERALL: {'✅ ALL TESTS PASSED' if report['overall_passed'] else '❌ SOME TESTS FAILED'}")
    print("=" * 60 + "\n")
    
    return report


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "nova"
    report = run_full_system_test(root)
    sys.exit(0 if report["overall_passed"] else 1)
