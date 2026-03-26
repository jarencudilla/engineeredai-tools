from flask import Flask, render_template, request, redirect
from db import init_db, get_conn
from engine import analyze_url
from discover import discover

app = Flask(__name__)
init_db()

# Dashboard Home
@app.route("/")
def index():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM comments ORDER BY date_added DESC")
    rows = c.fetchall()
    conn.close()
    return render_template("index.html", rows=rows)

# Add URL manually
@app.route("/add", methods=["POST"])
def add():
    url = request.form["url"]
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO comments (url) VALUES (?)", (url,))
    conn.commit()
    conn.close()
    return redirect("/")

# Auto-discover URLs
@app.route("/discover", methods=["POST"])
def auto_discover():
    seed_site = request.form["seed_site"]
    keywords = request.form["keywords"]
    urls = discover(seed_site, keywords)
    conn = get_conn()
    c = conn.cursor()
    for url in urls:
        c.execute("INSERT OR IGNORE INTO comments (url) VALUES (?)", (url,))
    conn.commit()
    conn.close()
    return redirect("/")

# Analyze a URL
@app.route("/process/<int:id>")
def process(id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT url FROM comments WHERE id=?", (id,))
    row = c.fetchone()
    if not row:
        return redirect("/")
    url = row[0]
    result = analyze_url(url)
    if result:
        c.execute("""
        UPDATE comments SET
            summary=?,
            gap=?,
            weakness=?,
            comment1=?,
            comment2=?,
            comment3=?,
            status='ready'
        WHERE id=?
        """, (
            result["summary"],
            result["gap"],
            result["weakness"],
            result["comments"][0],
            result["comments"][1],
            result["comments"][2],
            id
        ))
        conn.commit()
    conn.close()
    return redirect("/")

# Mark as posted
@app.route("/mark/<int:id>")
def mark(id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE comments SET status='posted' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)