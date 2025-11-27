import json
import toml
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, field

# --- Data Structures ---

@dataclass
class Dependency:
    name: str
    version: str
    ecosystem: str
    scope: Optional[str] = None
    source_file: Optional[str] = None
    license: Optional[str] = None

# --- Dependency Parsers ---

class DependencyParser:
    @staticmethod
    def parse_pyproject_toml(file_path="pyproject.toml") -> List[Dependency]:
        deps = []
        try:
            data = toml.load(file_path)
            for scope_name, deps_section in [("main", "dependencies"), ("dev", "dev-dependencies")]:
                dep_group = data.get('tool', {}).get('poetry', {}).get(deps_section, {})
                for name, value in dep_group.items():
                    if name == "python": continue
                    version = value if isinstance(value, str) else value.get('version', 'unknown')
                    license_val = value.get('license') if isinstance(value, dict) else None
                    deps.append(Dependency(
                        name=name, version=version, ecosystem="python",
                        scope=scope_name, source_file=file_path, license=license_val
                    ))
        except FileNotFoundError: pass
        return deps

    @staticmethod
    def parse_package_json(file_path="package.json") -> List[Dependency]:
        deps = []
        try:
            with open(file_path, 'r') as f: data = json.load(f)
            for scope_name, dep_key in [("main", "dependencies"), ("dev", "devDependencies")]:
                for name, version in data.get(dep_key, {}).items():
                    deps.append(Dependency(
                        name=name, version=version, ecosystem="node",
                        scope=scope_name, source_file=file_path
                    ))
        except FileNotFoundError: pass
        return deps

    @staticmethod
    def parse_pom_xml(file_path="pom.xml") -> List[Dependency]:
        deps = []
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            ns = {'m': 'http://maven.apache.org/POM/4.0.0'}

            properties = {p.tag.replace(f'{{{ns["m"]}}}', ''): p.text for p in root.findall('m:properties/*', ns)}

            managed_versions = {}
            for dep in root.findall('m:dependencyManagement/m:dependencies/m:dependency', ns):
                key = f"{dep.find('m:groupId', ns).text}:{dep.find('m:artifactId', ns).text}"
                managed_versions[key] = dep.find('m:version', ns).text

            for dep_node in root.findall('m:dependencies/m:dependency', ns):
                group = dep_node.find('m:groupId', ns).text
                artifact = dep_node.find('m:artifactId', ns).text
                key = f"{group}:{artifact}"

                version_node = dep_node.find('m:version', ns)
                version_text = version_node.text if version_node is not None else managed_versions.get(key)

                if not version_text: continue

                if version_text.startswith('${') and version_text.endswith('}'):
                    version = properties.get(version_text[2:-1], version_text)
                else:
                    version = version_text

                scope = dep_node.find('m:scope', ns)
                deps.append(Dependency(
                    name=key, version=version, ecosystem="java",
                    scope=scope.text if scope is not None else "compile",
                    source_file=file_path
                ))
        except (FileNotFoundError, ET.ParseError): pass
        return deps

    @staticmethod
    def load_all() -> List[Dependency]:
        return DependencyParser.parse_pyproject_toml() + \
               DependencyParser.parse_package_json() + \
               DependencyParser.parse_pom_xml()

# --- Reporting ---

@dataclass
class Report:
    violations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    passed: List[str] = field(default_factory=list)
    exceptions: List[str] = field(default_factory=list)

    def export_json(self, file_path="policy_report.json"):
        report_data = {
            "summary": {k: len(v) for k, v in self.__dict__.items()},
            "results": self.__dict__
        }
        with open(file_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        print(f"\n📄 Report exported to {file_path}")

# --- License Resolution ---

class LicenseResolver:
    _KNOWN_LICENSES = {
        "requests": "Apache-2.0", "express": "MIT", "pytest": "MIT",
        "org.apache.commons:commons-lang3": "Apache-2.0", "junit:junit": "EPL-1.0",
        "com.microsoft.signalr": "MIT", "com.example:legacy-framework": "Proprietary"
    }
    def resolve(self, dep: Dependency) -> str:
        return dep.license or self._KNOWN_LICENSES.get(dep.name, "unknown")

# --- Policy Enforcement ---

class PolicyEnforcer:
    OSI_APPROVED = ["MIT", "Apache-2.0", "BSD-3-Clause", "GPL-3.0"]
    VENDOR_IDENTIFIERS = ["com.oracle", "com.amazonaws"]

    def __init__(self, license_resolver: LicenseResolver, exceptions_file="policy_exceptions.json"):
        self.report = Report()
        self.license_resolver = license_resolver
        self.exceptions = self._load_exceptions(exceptions_file)

    def _load_exceptions(self, file_path: str) -> List[Dict]:
        try:
            with open(file_path, 'r') as f: data = json.load(f)
            return [exc for exc in data.get("exceptions", []) if "expires_on" in exc]
        except (FileNotFoundError, json.JSONDecodeError): return []

    def _is_exception(self, dep: Dependency) -> Optional[Dict]:
        today = datetime.now()
        for exc in self.exceptions:
            if dep.name == exc.get("dependency") and dep.ecosystem == exc.get("ecosystem"):
                try:
                    if today <= datetime.strptime(exc["expires_on"], "%Y-%m-%d"):
                        return exc
                except (ValueError, TypeError): continue
        return None

    def check_license(self, dep: Dependency):
        license = self.license_resolver.resolve(dep)
        if license not in self.OSI_APPROVED:
            self.report.violations.append(f"License '{license}' for '{dep.name}' is not OSI approved.")
        else:
            self.report.passed.append(f"License check for '{dep.name}'")

    def check_vendor_lock_in(self, dep: Dependency):
        if any(dep.name.startswith(v) for v in self.VENDOR_IDENTIFIERS):
            self.report.violations.append(f"Dependency '{dep.name}' is from a restricted vendor.")
        else:
            self.report.passed.append(f"Vendor check for '{dep.name}'")

    def run_checks(self, deps: List[Dependency]):
        print("🔍 Scanning dependencies...")
        for dep in deps:
            if dep.scope in ["test", "dev"]: continue

            exception = self._is_exception(dep)
            if exception:
                self.report.exceptions.append(f"Exception for '{dep.name}': {exception.get('reason')}")
                continue

            self.check_license(dep)
            self.check_vendor_lock_in(dep)

        if self.report.exceptions:
            print("\n--- Policy Exceptions Honored ---")
            for msg in self.report.exceptions: print(f"   {msg}")

        if self.report.violations:
            print("\n❌ Violations Detected:")
            for v in self.report.violations: print(f"   - {v}")
            self.report.export_json()
            sys.exit(1)
        else:
            print("\n✅ All dependencies comply with policies.")
            self.report.export_json()

def main():
    enforcer = PolicyEnforcer(LicenseResolver())
    enforcer.run_checks(DependencyParser.load_all())

if __name__ == "__main__":
    main()
