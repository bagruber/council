"""Generate compressed WebP variants of member profile images.

Source: img/members/<id>.png  (huge originals, 1-8 MB each)
Output: img/members/<id>.webp  (~360px wide, ~30-50KB)
        img/members/<id>@2x.webp (~720px wide, retina, ~80-150KB)

Used by the profile view via image-set() in CSS for screen-density-aware loading.
"""
import os
from PIL import Image

SRC_DIR = "img/members"
SIZES = [
    ("",     360, 78),   # 1x — base
    ("@2x",  720, 78),   # 2x retina
]

png_files = sorted(f for f in os.listdir(SRC_DIR) if f.lower().endswith(".png"))
print(f"processing {len(png_files)} PNGs")

before_total = 0
after_total = 0
for fname in png_files:
    src = os.path.join(SRC_DIR, fname)
    name = os.path.splitext(fname)[0]
    before_total += os.path.getsize(src)
    img = Image.open(src).convert("RGB")
    w, h = img.size
    for suffix, target_w, quality in SIZES:
        if w <= target_w:
            scaled = img
        else:
            ratio = target_w / w
            scaled = img.resize((target_w, int(h * ratio)), Image.LANCZOS)
        out_path = os.path.join(SRC_DIR, f"{name}{suffix}.webp")
        scaled.save(out_path, "WEBP", quality=quality, method=6)
        after_total += os.path.getsize(out_path)
    print(f"  {name}: {os.path.getsize(src)/1024:.0f}K png → "
          f"{os.path.getsize(os.path.join(SRC_DIR, name+'.webp'))/1024:.0f}K + "
          f"{os.path.getsize(os.path.join(SRC_DIR, name+'@2x.webp'))/1024:.0f}K webp")

print(f"\ntotal: {before_total/1024/1024:.1f} MB (PNG) → {after_total/1024/1024:.1f} MB (WebP both sizes)")
