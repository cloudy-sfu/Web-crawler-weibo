import json

lines = []
while (not lines) or lines[-1]:
    lines.append(input())
header = {}
i = 0
n = len(lines)
while i < n - 1:
    key = lines[i]
    value = lines[i+1]
    i += 2
    if key[0] == ':':
        continue
    key = key.rstrip(':')
    header[key] = value
with open("_https_header.json", "w") as f:
    json.dump(header, f, indent=4)
