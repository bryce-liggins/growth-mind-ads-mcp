"""Small privacy/link check, complementary to a full secret scanner."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".git", ".venv", "__pycache__", "dist", "build"}
ALLOWED_IDS = {"1234567890", "1111111111"}
issues = []
count = 0
for file in ROOT.rglob("*"):
    if not file.is_file() or any(part in SKIP for part in file.relative_to(ROOT).parts):
        continue
    count += 1
    rel = str(file.relative_to(ROOT))
    if file.name == ".env" or (file.name.startswith(".env.") and file.name != ".env.example"):
        issues.append((rel, "private environment file"))
    if file.suffix in {".pem", ".key", ".jsonl"} or file.name.startswith(("client_secret", "application_default_credentials")):
        issues.append((rel, "private/runtime file"))
    text = file.read_text(errors="replace")
    if file.name != "uv.lock":
        for value in re.findall(r"\b\d{10}\b", text):
            if value not in ALLOWED_IDS:
                issues.append((rel, "non-fixture account-like identifier"))
    if re.search(r"/Users/[A-Za-z][^/\s]+/", text):
        issues.append((rel, "personal home path"))
    if file.suffix == ".md":
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if "://" in target or target.startswith("#"):
                continue
            if not (file.parent / target.split("#")[0]).exists():
                issues.append((rel, "broken relative link: " + target))

for rel, kind in issues:
    print(rel + ": " + kind)
print({"files_checked": count, "issues": len(issues)})
sys.exit(1 if issues else 0)
