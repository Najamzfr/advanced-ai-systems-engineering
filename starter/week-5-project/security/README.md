# Fixed security pack

`scripts/fetch_data.py` is the canonical, versioned source for `attack-pack-v1`. It materialises 20 fixed attacks across prompt injection, indirect injection, credential exfiltration, destructive action, unauthorized transfer, privacy boundary, argument tampering, social engineering, policy bypass and availability abuse, then adds distinct benign controls. The generated `data/manifest.json` records the exact SHA-256.

Do not replace attack rows with repeated copies: the checker requires unique case IDs and separate attack/benign denominators.
