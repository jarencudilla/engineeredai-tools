"""
ui/sessions_table.py

A QTableWidget that displays GA4 landing-page session rows for
whichever site is selected. Rendering only — no fetch/sync logic,
same split as ui/queries_table.py.
"""

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem

COLUMNS = ["Page", "Sessions", "Engaged", "Bounce Rate", "Avg Engagement (s)", "Date"]


class SessionsTable(QTableWidget):
    """Read-only table of GA4 landing-page performance rows."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(len(COLUMNS))
        self.setHorizontalHeaderLabels(COLUMNS)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSortingEnabled(True)

    def load_rows(self, rows):
        """
        Populate the table from a list of sqlite3.Row objects
        (as returned by database.db.fetch_all_sessions).

        @param rows  list[sqlite3.Row]
        """
        self.setSortingEnabled(False)
        self.setRowCount(len(rows))

        for row_index, row in enumerate(rows):
            values = [
                row["page"],
                str(row["sessions"]),
                str(row["engaged_sessions"]),
                f"{row['bounce_rate']:.2%}",
                f"{row['avg_engagement_time_sec']:.1f}",
                row["date"],
            ]
            for col_index, value in enumerate(values):
                self.setItem(row_index, col_index, QTableWidgetItem(value))

        self.setSortingEnabled(True)
        self.resizeColumnsToContents()
