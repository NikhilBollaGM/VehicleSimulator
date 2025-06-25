import yaml
from models.signal_model import Signal

def load_signals_from_yaml(path):
    with open(path, "r") as f:
        yaml_data = yaml.safe_load(f)

    signals = {}

    def recurse(node, prefix=""):
        for key, val in node.items():
            if not isinstance(val, dict):
                continue
            if val.get("type") == "branch":
                continue
            full_path = f"{prefix}.{key}" if prefix else key
            if "datatype" in val:
                if val.get("datatype") == "string" and "allowed" in val:
                    val["datatype"] = "enum"
                signals[full_path] = Signal(full_path, val)
            else:
                recurse(val, full_path)

    recurse(yaml_data)
    return signals
