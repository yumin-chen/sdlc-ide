import json
import sys
import yaml

def normalize(data, mapping):
    """
    Recursively traverses a data structure and replaces keys and values
    with their canonical IDs from the mapping.
    """
    if isinstance(data, dict):
        return {mapping.get(k, k): normalize(v, mapping) for k, v in data.items()}
    elif isinstance(data, list):
        return [normalize(i, mapping) for i in data]
    else:
        return mapping.get(data, data)

if __name__ == "__main__":
    try:
        with open("mappings/canonical_map.json") as f:
            mapping = json.load(f)
    except FileNotFoundError:
        print("Error: mappings/canonical_map.json not found.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: mappings/canonical_map.json is not a valid JSON file.", file=sys.stderr)
        sys.exit(1)

    try:
        input_yaml = sys.stdin.read()
        data = yaml.safe_load(input_yaml)
    except yaml.YAMLError as e:
        print(f"Error parsing input YAML: {e}", file=sys.stderr)
        sys.exit(1)

    normalized_data = normalize(data, mapping)
    print(json.dumps(normalized_data, indent=2))
