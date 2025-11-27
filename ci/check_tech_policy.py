import json
import toml
import sys
import xml.etree.ElementTree as ET

# --- Dependency Parsers ---

def parse_pyproject_toml():
    """Parses pyproject.toml to extract dependencies."""
    deps = []
    try:
        pyproject = toml.load("pyproject.toml")
        py_deps = pyproject.get('tool', {}).get('poetry', {}).get('dependencies', {})
        for name, value in py_deps.items():
            if name == "python":
                continue
            if isinstance(value, str):
                deps.append({'name': name, 'version': value, 'source': 'pyproject.toml'})
            elif isinstance(value, dict):
                # We can extract more details here if needed
                dep_info = {'name': name, 'version': value.get('version', 'unknown'), 'source': 'pyproject.toml'}
                if 'license' in value:
                    dep_info['license'] = value['license']
                deps.append(dep_info)
    except FileNotFoundError:
        pass  # No pyproject.toml file found
    except Exception as e:
        print(f"❌ Error parsing pyproject.toml: {e}")
    return deps

def parse_package_json():
    """Parses package.json to extract dependencies."""
    deps = []
    try:
        with open("package.json", "r") as f:
            data = json.load(f)
            for name, ver in data.get("dependencies", {}).items():
                deps.append({'name': name, 'version': ver, 'source': 'package.json'})
            for name, ver in data.get("devDependencies", {}).items():
                deps.append({'name': name, 'version': ver, 'source': 'package.json'})
    except FileNotFoundError:
        pass  # No package.json file found
    except json.JSONDecodeError:
        print("❌ Error: Could not decode package.json.")
    return deps

def parse_pom_xml():
    """Parses pom.xml to extract dependencies."""
    deps = []
    try:
        tree = ET.parse("pom.xml")
        root = tree.getroot()
        ns = {'m': 'http://maven.apache.org/POM/4.0.0'}
        for dep_node in root.findall('.//m:dependency', ns):
            group_id = dep_node.find('m:groupId', ns).text
            artifact_id = dep_node.find('m:artifactId', ns).text
            version = dep_node.find('m:version', ns).text
            dep = {'name': f"{group_id}:{artifact_id}", 'version': version, 'source': 'pom.xml'}
            # Check for custom vendor-specific flag
            if dep_node.find('m:vendor_specific', ns) is not None and dep_node.find('m:vendor_specific', ns).text == 'true':
                dep['vendor_specific'] = True
            deps.append(dep)
    except FileNotFoundError:
        pass  # No pom.xml file found
    except ET.ParseError:
        print("❌ Error: Could not parse pom.xml.")
    return deps

def load_dependencies():
    """Loads dependencies from all supported package managers."""
    deps = parse_pyproject_toml()
    deps.extend(parse_package_json())
    deps.extend(parse_pom_xml())
    return deps

# --- Policy Enforcement Rules ---

OSI_APPROVED = ["MIT", "Apache-2.0", "BSD-3-Clause", "GPL-3.0"]

# Mock database of known licenses for our test dependencies
KNOWN_LICENSES = {
    "requests": "Apache-2.0",
    "express": "MIT",
    "lodash": "MIT",
    "jest": "MIT",
    "eslint": "MIT",
    "junit:junit": "EPL-1.0", # Example of a non-OSI approved license for testing
    "org.apache.commons:commons-lang3": "Apache-2.0"
}

def check_license(dep):
    """
    Checks if a dependency has an OSI-approved license.
    This is a mock implementation. In a real scenario, this function would
    query a license database or use a dedicated tool.
    """
    # Prioritize license info embedded in the dependency data
    license = dep.get('license')
    if not license:
        # Fallback to our mock database
        license = KNOWN_LICENSES.get(dep['name'], 'unknown')

    return license in OSI_APPROVED

def check_implementations(dep):
    """Mock check for at least two independent implementations."""
    # In a real implementation, this might check a curated list.
    return dep.get('implementations', 2) >= 2

def check_vendor(dep):
    """Mock check for vendor-specific dependencies."""
    if dep.get('vendor_specific', False):
        # In a real implementation, check for linked ADRs or other docs.
        doc = dep.get('documentation', False)
        mig = dep.get('migration_path', False)
        return doc and mig
    return True

# --- Main Execution ---

def main():
    deps = load_dependencies()
    violations = []

    print("🔍 Scanning dependencies for policy compliance...")
    for dep in deps:
        if not check_license(dep):
            violations.append(f"Dependency '{dep['name']}' has a non-OSI approved or unknown license.")
        if not check_implementations(dep):
            violations.append(f"Dependency '{dep['name']}' lacks at least two independent implementations.")
        if not check_vendor(dep):
            violations.append(f"Dependency '{dep['name']}' is vendor-specific without a documented migration path.")

    if violations:
        print("\n❌ Technology Policy Violations Detected:")
        for v in violations:
            print(f"   - {v}")
        sys.exit(1)
    else:
        print("\n✅ All dependencies comply with the Technology Recommendation Policy.")

if __name__ == "__main__":
    main()
