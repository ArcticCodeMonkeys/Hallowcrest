import os, shutil, re
import yaml

VAULT_DIR   = "."
WIKI_CONTENT = "wiki/content"
IMAGE_EXTS  = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
referenced_images = set()

def parse_frontmatter(text):
    if text.startswith("---"):
        try:
            end = text.index("---", 3)
            fm = yaml.safe_load(text[3:end])
            body = text[end + 3:].strip()
            return fm or {}, body
        except Exception:
            pass
    return {}, text

def should_publish(fm):
    return str(fm.get("publish", "false")).lower() == "true"

def collect_images(content):
    wiki_imgs = re.findall(r'!\[\[([^\]]+\.\w+)\]\]', content)
    md_imgs   = re.findall(r'!\[.*?\]\(([^)]+)\)', content)
    for img in wiki_imgs + md_imgs:
        referenced_images.add(os.path.basename(img))

def redact_censor_block(match):
    block = match.group(0)
    line_count = block.count("\n") + 1
    return "\n".join(["█████"] * line_count)

def process_markdown(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    fm, body = parse_frontmatter(text)
    if not should_publish(fm):
        return None
    collect_images(body)
    
    # Replace censored blocks with redacted text
    body = re.sub(r'%%CENSOR%%.*?%%/CENSOR%%', redact_censor_block, body, flags=re.DOTALL)
    
    fm.pop("publish", None)
    out_fm = yaml.dump(fm, allow_unicode=True).strip() if fm else ""
    if out_fm:
        return f"---\n{out_fm}\n---\n\n{body}"
    return body

def copy_images():
    for root, dirs, files in os.walk(VAULT_DIR):
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext in IMAGE_EXTS and fname in referenced_images:
                src  = os.path.join(root, fname)
                dest = os.path.join(WIKI_CONTENT, fname)
                if os.path.abspath(src) != os.path.abspath(dest):
                    shutil.copy2(src, dest)

shutil.rmtree(WIKI_CONTENT, ignore_errors=True)
os.makedirs(WIKI_CONTENT)

# Always copy index.md if it exists
index = os.path.join(VAULT_DIR, "index.md")
if os.path.exists(index):
    shutil.copy2(index, os.path.join(WIKI_CONTENT, "index.md"))

for root, dirs, files in os.walk(VAULT_DIR):
    dirs[:] = [d for d in dirs if not d.startswith(".") and d != "_templates"]
    for fname in files:
        if not fname.endswith(".md"):
            continue
        path = os.path.join(root, fname)
        rel  = os.path.relpath(path, VAULT_DIR)
        result = process_markdown(path)
        if result is None:
            continue
        dest = os.path.join(WIKI_CONTENT, rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f:
            f.write(result)

copy_images()
print("Done!")