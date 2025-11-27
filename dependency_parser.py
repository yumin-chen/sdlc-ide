import json
import toml
import xml.etree.ElementTree as ET
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import re

@dataclass
class Dependency:
    """Unified dependency representation across ecosystems"""
    name: str
    version: str
    ecosystem: str  # python, nodejs, java
    license: str = "unknown"
    implementations: int = 1
    vendor_specific: bool = False
    documentation: bool = False
    migration_path: bool = False

    def __hash__(self):
        return hash((self.name, self.ecosystem))

class DependencyParser:
    """Parse dependencies from multiple package managers"""

    OSI_APPROVED = [
        "MIT", "Apache-2.0", "Apache License 2.0",
        "BSD-3-Clause", "BSD-2-Clause",
        "GPL-3.0", "GPL-3.0-or-later", "LGPL-3.0",
        "ISC", "MPL-2.0", "CDDL-1.0", "EPL-1.0"
    ]

    @staticmethod
    def parse_python_dependencies() -> List[Dependency]:
        """Parse Python dependencies from pyproject.toml or requirements.txt"""
        deps = []

        # Try pyproject.toml (Poetry)
        pyproject_path = Path("pyproject.toml")
        if pyproject_path.exists():
            try:
                config = toml.load(pyproject_path)
                py_deps = config.get('tool', {}).get('poetry', {}).get('dependencies', {})
                for name, spec in py_deps.items():
                    if name == "python":
                        continue
                    version = spec if isinstance(spec, str) else spec.get("version", "*")
                    deps.append(Dependency(
                        name=name,
                        version=version,
                        ecosystem="python"
                    ))
            except Exception as e:
                print(f"⚠ Warning: Failed to parse pyproject.toml: {e}")

        # Try requirements.txt
        req_path = Path("requirements.txt")
        if req_path.exists():
            try:
                with open(req_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            match = re.match(r'^([a-zA-Z0-9\-_.]+)([><=!~]*.*)?$', line)
                            if match:
                                deps.append(Dependency(
                                    name=match.group(1),
                                    version=match.group(2) or "*",
                                    ecosystem="python"
                                ))
            except Exception as e:
                print(f"⚠ Warning: Failed to parse requirements.txt: {e}")

        return deps

    @staticmethod
    def parse_nodejs_dependencies() -> List[Dependency]:
        """Parse Node.js dependencies from package.json"""
        deps = []

        package_path = Path("package.json")
        if not package_path.exists():
            return deps

        try:
            with open(package_path, 'r') as f:
                package_json = json.load(f)

            # Parse production dependencies
            for name, version in package_json.get('dependencies', {}).items():
                deps.append(Dependency(
                    name=name,
                    version=version,
                    ecosystem="nodejs"
                ))

            # Parse dev dependencies (optional flag: can be excluded)
            for name, version in package_json.get('devDependencies', {}).items():
                deps.append(Dependency(
                    name=name,
                    version=version,
                    ecosystem="nodejs"
                ))

        except Exception as e:
            print(f"⚠ Warning: Failed to parse package.json: {e}")

        return deps

    @staticmethod
    def parse_java_dependencies() -> List[Dependency]:
        """Parse Java dependencies from pom.xml (Maven)"""
        deps = []

        pom_path = Path("pom.xml")
        if not pom_path.exists():
            return deps

        try:
            tree = ET.parse(pom_path)
            root = tree.getroot()

            # Handle Maven namespace
            ns = {'m': 'http://maven.apache.org/POM/4.0.0'}

            # Try with namespace first, then without
            dependencies = root.findall('.//m:dependency', ns)
            if not dependencies:
                dependencies = root.findall('.//dependency')

            for dep in dependencies:
                # Skip dependencies with scope=test (optional)
                scope = dep.findall('scope')
                if scope and scope[0].text == 'test':
                    continue

                artifact_id_elem = dep.find('m:artifactId', ns) or dep.find('artifactId')
                version_elem = dep.find('m:version', ns) or dep.find('version')
                group_id_elem = dep.find('m:groupId', ns) or dep.find('groupId')

                if artifact_id_elem is not None and artifact_id_elem.text:
                    group_id = group_id_elem.text if group_id_elem is not None else ""
                    # Combine groupId:artifactId for unique identification
                    full_name = f"{group_id}:{artifact_id_elem.text}" if group_id else artifact_id_elem.text
                    version = version_elem.text if version_elem is not None else "*"

                    deps.append(Dependency(
                        name=full_name,
                        version=version,
                        ecosystem="java"
                    ))

        except ET.ParseError as e:
            print(f"⚠ Warning: Failed to parse pom.xml (XML error): {e}")
        except Exception as e:
            print(f"⚠ Warning: Failed to parse pom.xml: {e}")

        return deps

    @staticmethod
    def load_all_dependencies() -> List[Dependency]:
        """Load dependencies from all supported package managers"""
        all_deps = []

        all_deps.extend(DependencyParser.parse_python_dependencies())
        all_deps.extend(DependencyParser.parse_nodejs_dependencies())
        all_deps.extend(DependencyParser.parse_java_dependencies())

        # Deduplicate by name and ecosystem
        seen = set()
        unique_deps = []
        for dep in all_deps:
            key = (dep.name, dep.ecosystem)
            if key not in seen:
                seen.add(key)
                unique_deps.append(dep)

        return unique_deps

class PolicyEnforcer:
    """Enforce Technology Recommendation Policy rules"""

    @staticmethod
    def check_license(dep: Dependency) -> Tuple[bool, str]:
        """Verify OSI-approved or open-standard license"""
        if dep.license == "unknown":
            return False, f"License unknown for {dep.name}"

        if dep.license not in DependencyParser.OSI_APPROVED:
            return False, f"{dep.name}: License '{dep.license}' not OSI-approved"

        return True, f"✓ {dep.name}: License compliant"

    @staticmethod
    def check_implementations(dep: Dependency) -> Tuple[bool, str]:
        """Verify multiple independent implementations exist"""
        if dep.implementations < 2:
            return False, f"{dep.name}: Only {dep.implementations} implementation(s) found (need ≥2)"

        return True, f"✓ {dep.name}: Multiple implementations verified"

    @staticmethod
    def check_vendor_lock_in(dep: Dependency) -> Tuple[bool, str]:
        """Ensure vendor-specific deps have migration paths"""
        if not dep.vendor_specific:
            return True, f"✓ {dep.name}: Not vendor-specific"

        if not (dep.documentation and dep.migration_path):
            missing = []
            if not dep.documentation:
                missing.append("documentation")
            if not dep.migration_path:
                missing.append("migration path")

            return False, f"{dep.name}: Vendor-specific but missing {', '.join(missing)}"

        return True, f"✓ {dep.name}: Vendor-specific with migration path & docs"

    @staticmethod
    def check_ecosystem_diversity(deps: List[Dependency]) -> Tuple[bool, str]:
        """Warn if ecosystem is overly concentrated"""
        ecosystem_counts = {}
        for dep in deps:
            ecosystem_counts[dep.ecosystem] = ecosystem_counts.get(dep.ecosystem, 0) + 1

        total = len(deps)
        warnings = []
        for eco, count in ecosystem_counts.items():
            percentage = (count / total * 100) if total > 0 else 0
            if percentage > 70:
                warnings.append(f"{eco}: {percentage:.0f}% of dependencies")

        if warnings:
            return False, f"Ecosystem concentration risk: {', '.join(warnings)}"

        return True, f"✓ Ecosystem diversity acceptable"

class Report:
    """Generate formatted compliance report"""

    def __init__(self):
        self.violations = []
        self.warnings = []
        self.passed = []

    def add_violation(self, msg: str):
        self.violations.append(msg)

    def add_warning(self, msg: str):
        self.warnings.append(msg)

    def add_passed(self, msg: str):
        self.passed.append(msg)

    def print_report(self):
        print("\n" + "="*70)
        print("TECHNOLOGY POLICY COMPLIANCE REPORT")
        print("="*70 + "\n")

        if self.passed:
            print("✅ PASSED CHECKS:")
            for msg in self.passed[:5]:  # Show first 5
                print(f"   {msg}")
            if len(self.passed) > 5:
                print(f"   ... and {len(self.passed) - 5} more")
            print()

        if self.warnings:
            print("⚠ WARNINGS:")
            for msg in self.warnings:
                print(f"   {msg}")
            print()

        if self.violations:
            print("❌ VIOLATIONS (CI WILL FAIL):")
            for msg in self.violations:
                print(f"   {msg}")
            print()
            return False
        else:
            print("✅ ALL COMPLIANCE CHECKS PASSED\n")
            return True

def main():
    print("🔍 Scanning for dependencies across all ecosystems...\n")

    # Parse dependencies
    deps = DependencyParser.load_all_dependencies()

    if not deps:
        print("⚠ No dependencies found. Skipping policy checks.")
        sys.exit(0)

    print(f"Found {len(deps)} unique dependencies:\n")

    # Group by ecosystem
    by_ecosystem = {}
    for dep in deps:
        if dep.ecosystem not in by_ecosystem:
            by_ecosystem[dep.ecosystem] = []
        by_ecosystem[dep.ecosystem].append(dep)

    for eco, eco_deps in sorted(by_ecosystem.items()):
        print(f"  {eco.upper()}: {len(eco_deps)} dependencies")
    print()

    # Run policy enforcement
    report = Report()

    for dep in deps:
        passed, msg = PolicyEnforcer.check_license(dep)
        if passed:
            report.add_passed(msg)
        else:
            report.add_violation(msg)

        passed, msg = PolicyEnforcer.check_implementations(dep)
        if passed:
            report.add_passed(msg)
        else:
            report.add_warning(msg)  # Warning, not violation

        passed, msg = PolicyEnforcer.check_vendor_lock_in(dep)
        if passed:
            report.add_passed(msg)
        else:
            report.add_violation(msg)

    # Check ecosystem diversity
    passed, msg = PolicyEnforcer.check_ecosystem_diversity(deps)
    if passed:
        report.add_passed(msg)
    else:
        report.add_warning(msg)

    # Print report and exit with appropriate code
    success = report.print_report()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()