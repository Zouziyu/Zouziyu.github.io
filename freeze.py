"""Generate a static copy of the blog in docs/ for GitHub Pages deployment."""
import os
import shutil
import sys

# Add current dir to path so we can import myblog
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from myblog import app, get_posts, get_all_tags, get_all_categories, STATIC_DIR

OUTPUT_DIR = "docs"

# Set to "/repo-name" if deploying to username.github.io/repo-name/
# Leave as "" if deploying to username.github.io or a custom domain
SITE_PREFIX = ""


def freeze():
    app.config["SERVER_NAME"] = None  # disable host matching for test client
    client = app.test_client()

    # Clean and recreate output dir
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    # Copy static files
    if os.path.isdir(STATIC_DIR):
        shutil.copytree(STATIC_DIR, os.path.join(OUTPUT_DIR, "static"))

    def save(url, filepath):
        resp = client.get(url)
        if resp.status_code != 200:
            print(f"  SKIP {url} → {resp.status_code}")
            return
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        html = resp.data.decode("utf-8")
        if SITE_PREFIX:
            html = html.replace('href="/', f'href="{SITE_PREFIX}/')
            html = html.replace('src="/', f'src="{SITE_PREFIX}/')
            html = html.replace('action="/', f'action="{SITE_PREFIX}/')
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  {url} → {filepath}")

    print("Freezing blog...")

    # Index
    save("/", os.path.join(OUTPUT_DIR, "index.html"))

    # Posts
    for post in get_posts():
        slug = post["slug"]
        save(f"/post/{slug}", os.path.join(OUTPUT_DIR, "post", slug, "index.html"))

    # Tags
    for tag in get_all_tags(get_posts()):
        save(f"/tag/{tag}", os.path.join(OUTPUT_DIR, "tag", tag, "index.html"))

    # Categories
    for cat in get_all_categories(get_posts()):
        save(f"/category/{cat}", os.path.join(OUTPUT_DIR, "category", cat, "index.html"))

    # Feed & pygments CSS
    save("/feed.xml", os.path.join(OUTPUT_DIR, "feed.xml"))
    save("/pygments.css", os.path.join(OUTPUT_DIR, "pygments.css"))

    print(f"\nDone — site frozen to {OUTPUT_DIR}/")


if __name__ == "__main__":
    freeze()
