import os
import time
from datetime import datetime, timezone

import frontmatter
import markdown
from flask import Flask, render_template, request, url_for, abort, redirect
from feedgen.feed import FeedGenerator
from pygments.formatters import HtmlFormatter

app = Flask(__name__)
POSTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "posts")
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
BLOG_AUTHOR = "Joey Chow"
BLOG_DESCRIPTION = "A personal dev blog"

_cache = {"posts": None, "time": 0}


def load_posts():
    posts = []
    if not os.path.isdir(POSTS_DIR):
        return posts
    for filename in os.listdir(POSTS_DIR):
        if not filename.endswith(".md"):
            continue
        filepath = os.path.join(POSTS_DIR, filename)
        post = frontmatter.load(filepath)
        slug = filename[:-3]
        raw_tags = post.get("tags", [])
        if isinstance(raw_tags, str):
            tags = [t.strip() for t in raw_tags.split(",") if t.strip()]
        else:
            tags = list(raw_tags) if raw_tags else []

        raw_date = post.get("date")
        if isinstance(raw_date, datetime):
            dt = raw_date
        elif isinstance(raw_date, str):
            dt = datetime.fromisoformat(raw_date)
        else:
            dt = datetime.now(timezone.utc)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        posts.append({
            "slug": slug,
            "title": post.get("title", slug.replace("-", " ").title()),
            "date": dt,
            "tags": tags,
            "category": post.get("category", "uncategorized"),
            "content": post.content,
            "html": render_markdown(post.content),
        })

    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def get_posts():
    now = time.time()
    if _cache["posts"] is None or now - _cache["time"] > 5:
        _cache["posts"] = load_posts()
        _cache["time"] = now
    return _cache["posts"]


def render_markdown(content):
    return markdown.markdown(
        content,
        extensions=["fenced_code", "codehilite", "tables", "nl2br"],
        extension_configs={"codehilite": {"guess_lang": False}},
    )


def get_all_tags(posts):
    tags = set()
    for p in posts:
        for t in p["tags"]:
            tags.add(t)
    return sorted(tags)


def get_all_categories(posts):
    return sorted({p["category"] for p in posts})


@app.context_processor
def inject_sidebar():
    posts = get_posts()
    avatar_path = os.path.join(STATIC_DIR, "avatar.png")
    has_avatar = os.path.isfile(avatar_path)
    initials = "".join(w[0].upper() for w in BLOG_AUTHOR.split()[:2])
    return {
        "all_tags": get_all_tags(posts),
        "all_categories": get_all_categories(posts),
        "blog_author": BLOG_AUTHOR,
        "blog_description": BLOG_DESCRIPTION,
        "has_avatar": has_avatar,
        "author_initials": initials,
    }


# ── Routes ──────────────────────────

@app.route("/")
def index():
    return render_template("index.html", posts=get_posts())


@app.route("/post/<slug>")
def post_view(slug):
    post = next((p for p in get_posts() if p["slug"] == slug), None)
    if not post:
        abort(404)
    return render_template("post.html", post=post)


@app.route("/tag/<tag>")
def tag_view(tag):
    filtered = [p for p in get_posts() if tag in p["tags"]]
    return render_template("tag.html", posts=filtered, filter_name=tag, filter_type="tag")


@app.route("/category/<cat>")
def category_view(cat):
    filtered = [p for p in get_posts() if p["category"].lower() == cat.lower()]
    return render_template("tag.html", posts=filtered, filter_name=cat, filter_type="category")


@app.route("/feed.xml")
def feed():
    posts = get_posts()[:20]
    fg = FeedGenerator()
    fg.title("My Blog")
    fg.link(href=request.url_root, rel="alternate")
    fg.description("A personal dev blog")
    fg.id(request.url_root)

    for p in posts:
        fe = fg.add_entry()
        fe.title(p["title"])
        url = request.url_root.rstrip("/") + url_for("post_view", slug=p["slug"])
        fe.link(href=url)
        fe.id(url)
        fe.description(p["html"])
        fe.published(p["date"])

    return fg.rss_str(), 200, {"Content-Type": "application/rss+xml"}


@app.route("/pygments.css")
def pygments_css():
    css = HtmlFormatter(style="monokai").get_style_defs(".codehilite")
    return css, 200, {"Content-Type": "text/css"}


@app.route("/admin", methods=["GET", "POST"])
def admin():
    avatar_path = os.path.join(STATIC_DIR, "avatar.png")
    message = None
    if request.method == "POST":
        file = request.files.get("avatar")
        if file and file.filename:
            ext = os.path.splitext(file.filename)[1].lower()
            if ext not in (".png", ".jpg", ".jpeg", ".gif", ".webp"):
                message = ("error", "Only PNG, JPG, GIF, or WebP images allowed.")
            else:
                if os.path.exists(avatar_path):
                    os.remove(avatar_path)
                file.save(avatar_path)
                message = ("ok", "Avatar updated.")
        else:
            message = ("error", "No file selected.")
    has_avatar = os.path.isfile(avatar_path)
    return render_template("admin.html", has_avatar=has_avatar, message=message)


@app.route("/admin/remove", methods=["POST"])
def admin_remove_avatar():
    avatar_path = os.path.join(STATIC_DIR, "avatar.png")
    if os.path.exists(avatar_path):
        os.remove(avatar_path)
    return redirect("/admin")


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True, port=5001)
