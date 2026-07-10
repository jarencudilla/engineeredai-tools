"""
ui/inspector_panel.py

Shows everything about one selected page: the queries driving it
(GSC), its GA4 trend, and the verdict control. This is the piece
from the original spec's Inspector diagram (Page → Queries → Traffic
→ Engagement → History → verdict) that turns "a table" into
"an operator tool" — click something, get a full picture.

This widget only renders and emits signals on user action (verdict
save). It does not talk to the database directly — the caller (main
window) wires data in and handles the save.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QComboBox, QPushButton, QTextEdit
)
from PySide6.QtCore import Signal

from ui.pages_table import VERDICT_LABELS

QUERY_COLUMNS = ["Query", "Impressions", "Clicks", "CTR", "Position", "Date"]
GA4_COLUMNS = ["Date", "Sessions", "Engaged", "Bounce Rate"]


class InspectorPanel(QWidget):
    """Detail view for a single page, plus the verdict control."""

    verdict_saved = Signal(str, str, str)  # page, verdict, note

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_page = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self.page_label = QLabel("Select a page to inspect")
        self.page_label.setWordWrap(True)
        layout.addWidget(self.page_label)

        layout.addWidget(QLabel("Queries driving this page:"))
        self.queries_table = QTableWidget()
        self.queries_table.setColumnCount(len(QUERY_COLUMNS))
        self.queries_table.setHorizontalHeaderLabels(QUERY_COLUMNS)
        self.queries_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.queries_table)

        layout.addWidget(QLabel("GA4 trend:"))
        self.ga4_table = QTableWidget()
        self.ga4_table.setColumnCount(len(GA4_COLUMNS))
        self.ga4_table.setHorizontalHeaderLabels(GA4_COLUMNS)
        self.ga4_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.ga4_table)

        # --- Verdict control ---
        verdict_row = QHBoxLayout()
        verdict_row.addWidget(QLabel("Verdict:"))

        self.verdict_selector = QComboBox()
        for key, label in VERDICT_LABELS.items():
            if key is not None:
                self.verdict_selector.addItem(label, userData=key)

        self.save_verdict_button = QPushButton("Save Verdict")
        self.save_verdict_button.clicked.connect(self._on_save_clicked)

        verdict_row.addWidget(self.verdict_selector)
        verdict_row.addWidget(self.save_verdict_button)
        verdict_row.addStretch()
        layout.addLayout(verdict_row)

        self.note_field = QTextEdit()
        self.note_field.setPlaceholderText("Optional note — why this verdict, what to change, etc.")
        self.note_field.setMaximumHeight(60)
        layout.addWidget(self.note_field)

    def load_page(self, page: str, query_rows, ga4_rows, current_verdict: str = None, current_note: str = ""):
        """
        Populate the inspector for a newly selected page.

        @param page             str  The page URL being inspected
        @param query_rows       list[sqlite3.Row]  From database.pages.fetch_queries_for_page
        @param ga4_rows         list[sqlite3.Row]  From database.pages.fetch_sessions_for_page
        @param current_verdict  str | None  Existing verdict key, if any
        @param current_note     str  Existing note, if any
        """
        self._current_page = page
        self.page_label.setText(page)

        self.queries_table.setRowCount(len(query_rows))
        for i, row in enumerate(query_rows):
            values = [
                row["query"], str(row["impressions"]), str(row["clicks"]),
                f"{row['ctr']:.2%}", f"{row['position']:.1f}", row["date"],
            ]
            for col, value in enumerate(values):
                self.queries_table.setItem(i, col, QTableWidgetItem(value))
        self.queries_table.resizeColumnsToContents()

        self.ga4_table.setRowCount(len(ga4_rows))
        for i, row in enumerate(ga4_rows):
            values = [
                row["date"], str(row["sessions"]), str(row["engaged_sessions"]),
                f"{row['bounce_rate']:.2%}",
            ]
            for col, value in enumerate(values):
                self.ga4_table.setItem(i, col, QTableWidgetItem(value))
        self.ga4_table.resizeColumnsToContents()

        if current_verdict:
            index = self.verdict_selector.findData(current_verdict)
            if index >= 0:
                self.verdict_selector.setCurrentIndex(index)
        self.note_field.setPlainText(current_note or "")

    def _on_save_clicked(self):
        if not self._current_page:
            return
        verdict = self.verdict_selector.currentData()
        note = self.note_field.toPlainText()
        self.verdict_saved.emit(self._current_page, verdict, note)
