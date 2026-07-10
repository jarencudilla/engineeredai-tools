"""
ui/main_window.py

Top-level window. Pages (with Inspector) is the primary tab — one
row per page, click to drill into queries/GA4 trend, set a verdict.
Queries/Landing Pages/Opportunities are secondary, raw-data tabs.

Backfill = one-time full history pull, both sources.
Sync Recent = 30-day top-up, both sources, safe to re-run.
Export = dumps the current site's page rollup + verdicts to a file,
for handoff to external AI analysis (EAI Workstation, Claude, etc.)
rather than baking analysis into the app itself.
"""

from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTabWidget,
    QComboBox, QPushButton, QLabel, QStatusBar, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt

from config.sites import SITES, BASE_DIR
from app.sync import (
    backfill_site_gsc, backfill_site_ga4,
    sync_site_gsc_incremental, sync_site_ga4_incremental,
)
from database.db import get_connection, fetch_all_queries, fetch_all_sessions
from database.pages import (
    fetch_page_rollup, fetch_queries_for_page, fetch_sessions_for_page,
    set_verdict, get_verdict,
)
from analyzers.gsc_opportunities import find_ctr_opportunities
from services.export import export_csv, export_json, export_markdown
from ui.pages_table import PagesTable
from ui.inspector_panel import InspectorPanel
from ui.queries_table import QueriesTable
from ui.sessions_table import SessionsTable
from ui.opportunities_table import OpportunitiesTable

EXPORTS_DIR = BASE_DIR / "exports"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TrafficOps")
        self.resize(1200, 700)

        self._build_ui()
        self._load_selected_site()

    def _build_ui(self):
        central = QWidget()
        layout = QVBoxLayout(central)

        toolbar_row = QHBoxLayout()

        self.site_selector = QComboBox()
        for site_id, config in SITES.items():
            self.site_selector.addItem(config["label"], userData=site_id)
        self.site_selector.currentIndexChanged.connect(self._load_selected_site)

        self.backfill_button = QPushButton("Backfill (full history)")
        self.backfill_button.clicked.connect(self._run_backfill)

        self.sync_recent_button = QPushButton("Sync Recent (30 days)")
        self.sync_recent_button.clicked.connect(self._run_sync_recent)

        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self._run_export)

        self.status_label = QLabel("")

        toolbar_row.addWidget(QLabel("Site:"))
        toolbar_row.addWidget(self.site_selector)
        toolbar_row.addWidget(self.backfill_button)
        toolbar_row.addWidget(self.sync_recent_button)
        toolbar_row.addWidget(self.export_button)
        toolbar_row.addWidget(self.status_label)
        toolbar_row.addStretch()

        # --- Pages + Inspector, side by side ---
        self.pages_table = PagesTable()
        self.pages_table.page_selected.connect(self._on_page_selected)

        self.inspector = InspectorPanel()
        self.inspector.verdict_saved.connect(self._on_verdict_saved)

        pages_split = QSplitter(Qt.Horizontal)
        pages_split.addWidget(self.pages_table)
        pages_split.addWidget(self.inspector)
        pages_split.setStretchFactor(0, 2)
        pages_split.setStretchFactor(1, 1)

        # --- Secondary raw-data tabs ---
        self.queries_table = QueriesTable()
        self.sessions_table = SessionsTable()
        self.opportunities_table = OpportunitiesTable()

        self.tabs = QTabWidget()
        self.tabs.addTab(pages_split, "Pages")
        self.tabs.addTab(self.opportunities_table, "Opportunities")
        self.tabs.addTab(self.queries_table, "Queries (GSC)")
        self.tabs.addTab(self.sessions_table, "Landing Pages (GA4)")

        layout.addLayout(toolbar_row)
        layout.addWidget(self.tabs)

        self.setCentralWidget(central)
        self.setStatusBar(QStatusBar())

    def _current_site_id(self) -> str:
        return self.site_selector.currentData()

    def _load_selected_site(self):
        """Load whatever's already stored for the selected site — no API call."""
        site_id = self._current_site_id()
        site_config = SITES[site_id]

        conn = get_connection(site_config["db_path"])
        query_rows = fetch_all_queries(conn)
        session_rows = fetch_all_sessions(conn)
        page_rows = fetch_page_rollup(conn)
        conn.close()

        self.pages_table.load_rows(page_rows)
        self.queries_table.load_rows(query_rows)
        self.sessions_table.load_rows(session_rows)

        opportunities = find_ctr_opportunities(query_rows)
        self.opportunities_table.load_opportunities(opportunities)

        self.statusBar().showMessage(
            f"{site_config['label']}: {len(page_rows)} pages, {len(query_rows)} GSC rows, "
            f"{len(session_rows)} GA4 rows, {len(opportunities)} opportunities flagged"
        )

    def _on_page_selected(self, page: str):
        """Populate the Inspector when a page is clicked in the Pages tab."""
        site_config = SITES[self._current_site_id()]
        conn = get_connection(site_config["db_path"])
        query_rows = fetch_queries_for_page(conn, page)
        ga4_rows = fetch_sessions_for_page(conn, page)
        verdict_row = get_verdict(conn, page)
        conn.close()

        self.inspector.load_page(
            page, query_rows, ga4_rows,
            current_verdict=verdict_row["verdict"] if verdict_row else None,
            current_note=verdict_row["note"] if verdict_row else "",
        )

    def _on_verdict_saved(self, page: str, verdict: str, note: str):
        """Persist a verdict, then refresh the Pages table to show it."""
        site_config = SITES[self._current_site_id()]
        conn = get_connection(site_config["db_path"])
        set_verdict(conn, page, verdict, note)
        conn.close()

        self.statusBar().showMessage(f"Verdict saved for {page}")
        self._load_selected_site()

    def _run_export(self):
        """Export the current site's page rollup to a file the user picks."""
        site_id = self._current_site_id()
        site_config = SITES[site_id]

        path_str, selected_filter = QFileDialog.getSaveFileName(
            self, "Export page data",
            str(EXPORTS_DIR / f"{site_id}-pages.json"),
            "JSON (*.json);;CSV (*.csv);;Markdown (*.md)",
        )
        if not path_str:
            return

        output_path = Path(path_str)
        conn = get_connection(site_config["db_path"])
        rollup_rows = fetch_page_rollup(conn)
        conn.close()

        if output_path.suffix == ".csv":
            export_csv(rollup_rows, output_path)
        elif output_path.suffix == ".md":
            export_markdown(rollup_rows, output_path, site_label=site_config["label"])
        else:
            export_json(rollup_rows, output_path)

        self.statusBar().showMessage(f"Exported {len(rollup_rows)} pages to {output_path}")

    def _run_backfill(self):
        self._run_two_source_sync(
            gsc_fn=backfill_site_gsc, ga4_fn=backfill_site_ga4,
            button=self.backfill_button, action_label="Backfill",
        )

    def _run_sync_recent(self):
        self._run_two_source_sync(
            gsc_fn=sync_site_gsc_incremental, ga4_fn=sync_site_ga4_incremental,
            button=self.sync_recent_button, action_label="Sync",
        )

    def _run_two_source_sync(self, gsc_fn, ga4_fn, button: QPushButton, action_label: str):
        """
        Shared logic for running both GSC and GA4 under one button
        click. Each source's failure is reported separately.
        """
        site_id = self._current_site_id()
        button.setEnabled(False)
        self.status_label.setText(f"{action_label} running…")

        results = []
        errors = []

        for source_label, fn in [("GSC", gsc_fn), ("GA4", ga4_fn)]:
            try:
                result = fn(site_id)
                results.append(f"{source_label}: {result['rows_written']} rows")
            except Exception as exc:
                errors.append(f"{source_label}: {exc}")

        if errors:
            QMessageBox.critical(self, f"{action_label} had errors", "\n".join(errors))

        self.status_label.setText(
            f"{action_label} done — " + ", ".join(results) if results else f"{action_label} failed"
        )
        self._load_selected_site()
        button.setEnabled(True)
