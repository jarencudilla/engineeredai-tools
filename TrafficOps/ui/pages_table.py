"""
ui/pages_table.py

One row per page — the primary view. Replaces staring at query-level
rows to guess what's going on with a given URL. Selecting a row emits
a signal the Inspector panel listens to.
"""

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
from PySide6.QtCore import Signal

COLUMNS = ["Page", "Impressions", "Clicks", "Avg CTR", "Avg Position", "GA4 Sessions", "Engaged", "Verdict"]

VERDICT_LABELS = {
    "rewrite": "Rewrite",
    "delete": "Delete",
    "leave_it": "Leave it",
    "new_post_needed": "New post needed",
    None: "—",
}


class PagesTable(QTableWidget):
    """One row per page, aggregated across all synced GSC + GA4 data."""

    page_selected = Signal(str)  # emits the page URL when a row is clicked

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(len(COLUMNS))
        self.setHorizontalHeaderLabels(COLUMNS)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSortingEnabled(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.itemSelectionChanged.connect(self._on_selection_changed)

    def load_rows(self, rows):
        """
        @param rows  list[sqlite3.Row]  Output of database.pages.fetch_page_rollup
        """
        self.setSortingEnabled(False)
        self.setRowCount(len(rows))

        for row_index, row in enumerate(rows):
            values = [
                row["page"],
                str(row["total_impressions"]),
                str(row["total_clicks"]),
                f"{row['avg_ctr']:.2%}",
                f"{row['avg_position']:.1f}",
                str(row["total_sessions"]),
                str(row["total_engaged_sessions"]),
                VERDICT_LABELS.get(row["verdict"], row["verdict"]),
            ]
            for col_index, value in enumerate(values):
                self.setItem(row_index, col_index, QTableWidgetItem(value))

        self.setSortingEnabled(True)
        self.resizeColumnsToContents()

    def _on_selection_changed(self):
        selected = self.selectedItems()
        if not selected:
            return
        row_index = selected[0].row()
        page_item = self.item(row_index, 0)  # "Page" is column 0
        if page_item:
            self.page_selected.emit(page_item.text())
