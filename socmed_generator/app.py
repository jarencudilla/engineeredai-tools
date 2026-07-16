"""
app.py

Standalone local browser UI. No connection to EAI Workstation, runs
entirely on its own against local Ollama.

    python app.py

Then open http://localhost:5050 in a browser. Fill the form, hit Generate,
review results on the page. Files are written to outputs/ exactly like
the CLI version, since both call the same cycle_runner.run_cycle().
"""

from flask import Flask, request, render_template_string
from cycle_runner import run_cycle

app = Flask(__name__)

FORM_TEMPLATE = """
<!doctype html>
<html><head><title>CAS Social Generator</title>
<style>
  body { font-family: sans-serif; max-width: 700px; margin: 40px auto; }
  textarea { width: 100%; height: 70px; margin-bottom: 16px; }
  label { font-weight: bold; display: block; margin-top: 12px; }
  .result { background: #f4f4f4; padding: 16px; margin-bottom: 16px; border-radius: 6px; }
  .result img { max-width: 200px; display: block; margin-top: 8px; }
  button { padding: 10px 20px; font-size: 16px; }
</style></head>
<body>
  <h1>CAS Social Generator</h1>
  <form method="POST">
    <label>Break/Verify note (leave blank to skip)</label>
    <textarea name="break_verify">{{ notes.get('break_verify', '') }}</textarea>

    <label>Not Quite Sentient note</label>
    <textarea name="not_quite_sentient">{{ notes.get('not_quite_sentient', '') }}</textarea>

    <label>CAS note</label>
    <textarea name="cas">{{ notes.get('cas', '') }}</textarea>

    <label>Personal note</label>
    <textarea name="personal_note">{{ notes.get('personal_note', '') }}</textarea>

    <label>Personal mode</label>
    <select name="personal_mode">
      <option value="original">Original</option>
      <option value="share_from_page">Share from page</option>
    </select>

    <button type="submit">Generate</button>
  </form>

  {% if results %}
    <h2>Results</h2>
    {% for key, data in results.items() %}
      {% if not key.startswith('_') %}
        <div class="result">
          <strong>{{ key }}</strong>{% if data.slot %} — {{ data.slot }}{% endif %}
          <p>{{ data.text }}</p>
          <img src="/svg/{{ data.svg_path.split('/')[-1] }}">
        </div>
      {% endif %}
    {% endfor %}
    <p>Markdown file: {{ results['_markdown_path'] }}</p>
  {% endif %}
</body></html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    notes = {}
    if request.method == "POST":
        notes = {
            "break_verify": request.form.get("break_verify", ""),
            "not_quite_sentient": request.form.get("not_quite_sentient", ""),
            "cas": request.form.get("cas", ""),
            "personal": {
                "mode": request.form.get("personal_mode", "original"),
                "note": request.form.get("personal_note", ""),
                "platforms": ["facebook", "instagram", "threads"],
            },
        }
        results = run_cycle(notes)
    return render_template_string(FORM_TEMPLATE, results=results, notes=notes)


@app.route("/svg/<filename>")
def serve_svg(filename):
    from pathlib import Path
    from flask import Response
    svg_path = Path(__file__).parent / "outputs" / filename
    return Response(svg_path.read_text(), mimetype="image/svg+xml")


if __name__ == "__main__":
    app.run(port=5050, debug=False)
