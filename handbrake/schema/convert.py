import yaml
import json

# with open('schema/handbrake.schema.json', 'r') as f:
#     content = json.load(f)

# with open('schema/handbrake.schema.yaml', 'w') as f:
#     yaml.dump(content, f, sort_keys=False, width=float("inf"))

with open('schema/handbrake.schema.yaml', 'r') as f:
    content = yaml.safe_load(f)

with open('schema/handbrake.schema.json', 'w') as f:
    json.dump(content, f, indent=2)