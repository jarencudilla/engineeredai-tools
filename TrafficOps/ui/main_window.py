"""
ui/main_window.py

Top-level window for the MVP slice: pick a site, sync it, see the
Queries table populate. No sidebar, no Inspector, no multi-select
yet — those come in Phase 2 once this loop is proven.

This class wires UI events to app/sync.py and database/db.py, but
contains no business logic itself — it only reacts to clicks and
tells other modules what to do.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QPushButton, QLabel, QStatusBar, QMessageBox
)

from config.sites import SITES
from app.sync import sync_site
from database.db import get_connection, fetch_all_queries
from ui.queries_table import QueriesTable


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TrafficOps — MVP")
        self.resize(900, 600)

        self._build_ui()
        self._load_selected_site()

    def _build_ui(self):
        central = QWidget()
        layout = QVBoxLayout(central)

        # --- Toolbar row: site selector + sync button ---
        toolbar_row = QHBoxLayout()

        self.site_selector = QComboBox()
        for site_id, config in SITES.items():
            self.site_selector.addItem(config["label"], userData=site_id)
        self.site_selector.currentIndexChanged.connect(self._load_selected_site)

        self.sync_button = QPushButton("Sync")
        self.sync_button.clicked.connect(self._run_sync)

        self.status_label = QLabel("")

        toolbar_row.addWidget(QLabel("Site:"))
        toolbar_row.addWidget(self.site_selector)
        toolbar_row.addWidget(self.sync_button)
        toolbar_row.addWidget(self.status_label)
        toolbar_row.addStretch()

        # --- Table ---
        self.table = QueriesTable()

        layout.addLayout(toolbar_row)
        layout.addWidget(self.table)

        self.setCentralWidget(central)
        self.setStatusBar(QStatusBar())

    def _current_site_id(self) -> str:
        return self.site_selector.currentData()

    def _load_selected_site(self):
        """Load whatever's already stored for the selected site — no API call."""
        site_id = self._current_site_id()
        site_config = SITES[site_id]

        conn = get_connection(site_config["db_path"])
        rows = fetch_all_queries(conn)
        conn.close()

        self.table.load_rows(rows)
        self.statusBar().showMessage(f"{len(rows)} rows loaded for {site_config['label']}")

    def _run_sync(self):
        """Trigger a live GSC sync for the selected site, then reload the table."""
        site_id = self._current_site_id()
        self.sync_button.setEnabled(False)
        self.status_label.setText("Syncing…")

        try:
            # NOTE: MVP runs sync on the main thread — acceptable for
            # now since GSC calls are quick. Move to a worker thread
            # (per spec's Performance section) once sites are combined
            # or date ranges grow.
            result = sync_site(site_id)
            self.status_label.setText(
                f"Synced {result['rows_written']} rows "
                f"({result['start_date']} to {result['end_date']})"
            )
            self._load_selected_site()
        except Exception as exc:
            QMessageBox.critical(self, "Sync failed", str(exc))
            self.status_label.setText("Sync failed")
        finally:
            self.sync_button.setEnabled(True)
