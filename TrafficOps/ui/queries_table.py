"""
ui/queries_table.py

A QTableWidget that displays GSC query rows for whichever site
is currently selected. This widget ONLY renders — it has no idea
how to fetch or sync data, it just takes rows and displays them.
"""

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem

COLUMNS = ["Query", "Page", "Clicks", "Impressions", "CTR", "Position", "Date"]


class QueriesTable(QTableWidget):
    """Read-only table of GSC query performance rows."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(len(COLUMNS))
        self.setHorizontalHeaderLabels(COLUMNS)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSortingEnabled(True)

    def load_rows(self, rows):
        """
        Populate the table from a list of sqlite3.Row objects
        (as returned by database.db.fetch_all_queries).

        @param rows  list[sqlite3.Row]
        """
        self.setSortingEnabled(False)  # avoid re-sort mid-insert
        self.setRowCount(len(rows))

        for row_index, row in enumerate(rows):
            values = [
                row["query"],
                row["page"],
                str(row["clicks"]),
                str(row["impressions"]),
                f"{row['ctr']:.2%}",
                f"{row['position']:.1f}",
                row["date"],
            ]
            for col_index, value in enumerate(values):
                self.setItem(row_index, col_index, QTableWidgetItem(value))

        self.setSortingEnabled(True)
        self.resizeColumnsToContents()
