import json
import toml
import xml.etree.ElementTree as ET
import sys
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
import re
from datetime import datetime
import argparse

CONFIG_FILE = "policy_config.json"
JSON_REPORT_FILE = "compliance_report.json"

@dataclass
class Dependency:
    name: str
    version: str
    ecosystem: str
    scope: str = 'compile'
    source: str = 'unknown'
    license: str = "unknown"
    implementations: int = 1
    vendor_specific: bool = False
    documentation: bool = False
    migration_path: bool = False

    def __hash__(self): return hash((self.name, self.ecosystem))
    def __eq__(self, other):
        return isinstance(other, Dependency) and (self.name, self.ecosystem) == (other.name, other.ecosystem)

class Config:
    def __init__(self, file_path: str):
        try:
            with open(file_path, 'r') as f: data = json.load(f)
            self.diversity_threshold: float = data.get("diversity_threshold", 0.7)
            self.exceptions: List[Dict] = self._parse_exceptions(data.get("exceptions", []))
        except (FileNotFoundError, json.JSONDecodeError):
            self.diversity_threshold, self.exceptions = 0.7, []

    def _parse_exceptions(self, exceptions: List[Dict]) -> List[Dict]:
        for exc in exceptions:
            if exc.get("expires_on") and isinstance(exc["expires_on"], str):
                exc["expires_on"] = datetime.strptime(exc["expires_on"], "%Y-%m-%d")
        return exceptions

    def get_active_exception(self, dep: Dependency) -> Optional[Dict]:
        today = datetime.now()
        for exc in self.exceptions:
            if dep.name == exc.get("dependency") and dep.ecosystem == exc.get("ecosystem"):
                expires_on = exc.get("expires_on")
                if expires_on is None or (isinstance(expires_on, datetime) and today <= expires_on):
                    return exc
        return None

class DependencyParser:
    @staticmethod
    def resolve_license_stub(name: str, ecosystem: str) -> str: return "unknown"

    @staticmethod
    def parse_python_dependencies() -> List[Dependency]:
        deps = []
        if Path("pyproject.toml").exists():
            try:
                config = toml.load("pyproject.toml")
                poetry_deps = config.get('tool', {}).get('poetry', {}).get('dependencies', {})
                for name, spec in poetry_deps.items():
                    if name != "python":
                        deps.append(Dependency(name, spec if isinstance(spec, str) else spec.get("version", "*"), "python", source="PyPI"))
            except Exception as e: print(f"⚠ Warning: Failed to parse pyproject.toml: {e}")
        if Path("requirements.txt").exists():
            try:
                with open("requirements.txt", 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            match = re.match(r'^([a-zA-Z0-9\-_.]+)([><=!~].*)?$', line)
                            if match:
                                deps.append(Dependency(match.group(1), match.group(2) or "*", "python", source="PyPI"))
            except Exception as e: print(f"⚠ Warning: Failed to parse requirements.txt: {e}")
        return deps

    @staticmethod
    def parse_nodejs_dependencies(exclude_dev: bool = False) -> List[Dependency]:
        if not Path("package.json").exists(): return []
        deps = []
        try:
            with open("package.json", 'r') as f: package_json = json.load(f)
            scopes = {"dependencies": "compile"}
            if not exclude_dev: scopes["devDependencies"] = "dev"
            for s, scope_name in scopes.items():
                for name, version in package_json.get(s, {}).items():
                    deps.append(Dependency(name, version, "nodejs", scope=scope_name, source="npm"))
        except Exception as e: print(f"⚠ Warning: Failed to parse package.json: {e}")
        return deps

    @staticmethod
    def parse_java_dependencies() -> List[Dependency]:
        if not Path("pom.xml").exists(): return []
        deps = []
        try:
            # Remove namespaces for simpler parsing
            it = ET.iterparse("pom.xml")
            for _, el in it:
                if '}' in el.tag:
                    el.tag = el.tag.split('}', 1)[1]
            root = it.root

            mgmt_versions = {}
            for dep in root.findall('.//dependencyManagement/dependencies/dependency'):
                g = dep.findtext('groupId')
                a = dep.findtext('artifactId')
                v = dep.findtext('version')
                if g and a and v:
                    mgmt_versions[f"{g}:{a}"] = v

            for dep in root.findall('.//dependencies/dependency'):
                g, a = dep.findtext('groupId'), dep.findtext('artifactId')
                if (scope := dep.findtext('scope', 'compile')) == 'test': continue
                full_name = f"{g}:{a}"
                if full_name not in [d.name for d in deps]:
                    deps.append(Dependency(full_name, dep.findtext('version') or mgmt_versions.get(full_name, "*"), "java", scope=scope, source="Maven Central"))
        except Exception as e: print(f"⚠ Warning: Failed to parse pom.xml: {e}")
        return deps

    @staticmethod
    def load_all(exclude_dev: bool) -> List[Dependency]:
        deps = DependencyParser.parse_python_dependencies() + \
               DependencyParser.parse_nodejs_dependencies(exclude_dev) + \
               DependencyParser.parse_java_dependencies()
        unique_deps = {dep: dep for dep in deps}.values()
        for dep in unique_deps: dep.license = DependencyParser.resolve_license_stub(dep.name, dep.ecosystem)
        return list(unique_deps)

class PolicyEnforcer:
    OSI = ["MIT", "Apache-2.0", "BSD-3-Clause", "GPL-3.0", "LGPL-3.0", "MPL-2.0"]
    @staticmethod
    def check_license(d: Dependency) -> Tuple[bool, str]:
        if d.license == "unknown": return False, f"License for '{d.name}' is unknown."
        if d.license not in PolicyEnforcer.OSI: return False, f"License '{d.license}' for '{d.name}' is not OSI-approved."
        return True, f"License for '{d.name}' is compliant."
    @staticmethod
    def check_implementations(d: Dependency) -> Tuple[bool, str]:
        if d.implementations < 2: return False, f"'{d.name}' has only {d.implementations} impl(s) (need >= 2)."
        return True, "Multiple implementations exist."
    @staticmethod
    def check_vendor_lock_in(d: Dependency) -> Tuple[bool, str]:
        if d.vendor_specific and not (d.documentation and d.migration_path): return False, f"'{d.name}' is vendor-specific and lacks migration path/docs."
        return True, "Vendor lock-in risk acceptable."
    @staticmethod
    def check_diversity(deps: List[Dependency], threshold: float) -> Tuple[bool, str]:
        counts = {}
        for dep in deps: counts[dep.ecosystem] = counts.get(dep.ecosystem, 0) + 1
        total = len(deps)
        if not total: return True, ""
        issues = [f"{eco} at {(cnt/total)*100:.0f}%" for eco, cnt in counts.items() if (cnt/total) > threshold]
        if issues: return False, f"Ecosystem concentration risk: {', '.join(issues)}."
        return True, "Ecosystem diversity is within acceptable limits."

class Report:
    def __init__(self):
        self.results = {"passed": [], "warnings": [], "violations": []}
    def add(self, category: str, check: str, msg: str): self.results[category].append({"check": check, "message": msg})
    def print_console(self):
        print("\n" + "="*70 + "\nTECHNOLOGY POLICY COMPLIANCE REPORT\n" + "="*70 + "\n")
        for cat, items in self.results.items():
            if items:
                print(f"{'✅' if cat=='passed' else '⚠' if cat=='warnings' else '❌'} {cat.upper()}:")
                for item in items[:10]: print(f"  - {item['message']}")
                if len(items) > 10: print(f"  ... and {len(items)-10} more.")
                print()
    def write_json(self, file: str):
        summary = {cat: len(items) for cat, items in self.results.items()}
        summary["status"] = "FAILURE" if summary["violations"] else "SUCCESS"
        with open(file, 'w') as f: json.dump({"summary": summary, "results": self.results}, f, indent=2)
        print(f"📄 JSON report written to {file}")

def main():
    parser = argparse.ArgumentParser(description="Check technology policy compliance.")
    parser.add_argument("--exclude-dev", action="store_true", help="Exclude dev dependencies from Node.js projects.")
    args = parser.parse_args()

    config = Config(CONFIG_FILE)
    deps = DependencyParser.load_all(args.exclude_dev)
    report = Report()

    print(f"🔍 Found {len(deps)} unique dependencies. Running checks...\n")

    for dep in sorted(deps, key=lambda d: (d.ecosystem, d.name)):
        exc = config.get_active_exception(dep)
        if exc:
            report.add("passed", "exception", f"'{dep.name}': Exception approved ({exc.get('reason', 'N/A')}).")
            continue

        passed, msg = PolicyEnforcer.check_license(dep)
        report.add("violations" if not passed else "passed", "license", msg)

        passed, msg = PolicyEnforcer.check_vendor_lock_in(dep)
        report.add("violations" if not passed else "passed", "vendor_lock_in", msg)

        passed, msg = PolicyEnforcer.check_implementations(dep)
        report.add("warnings" if not passed else "passed", "implementations", msg)

    passed, msg = PolicyEnforcer.check_diversity(deps, config.diversity_threshold)
    report.add("warnings" if not passed else "passed", "diversity", msg)

    report.print_console()
    report.write_json(JSON_REPORT_FILE)

    if report.results["violations"]:
        sys.exit(1)

if __name__ == "__main__":
    main()
