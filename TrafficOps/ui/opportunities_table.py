"""
ui/opportunities_table.py

Displays the output of analyzers.gsc_opportunities.find_ctr_opportunities.
Rendering only — the filtering/scoring logic lives entirely in the
analyzer, not here.
"""

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
from PySide6.QtGui import QColor

COLUMNS = ["Severity", "Query", "Page", "Impressions", "Clicks", "CTR", "Position"]


class OpportunitiesTable(QTableWidget):
    """Read-only table of CTR opportunity rows, highest-impression first."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(len(COLUMNS))
        self.setHorizontalHeaderLabels(COLUMNS)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSortingEnabled(True)

    def load_opportunities(self, opportunities):
        """
        @param opportunities  list[analyzers.gsc_opportunities.Opportunity]
        """
        self.setSortingEnabled(False)
        self.setRowCount(len(opportunities))

        for row_index, opp in enumerate(opportunities):
            values = [
                opp.severity.upper(),
                opp.query,
                opp.page,
                str(opp.impressions),
                str(opp.clicks),
                f"{opp.ctr:.2%}",
                f"{opp.position:.1f}",
            ]
            for col_index, value in enumerate(values):
                item = QTableWidgetItem(value)
                # NOTE: visual flag for "high" severity rows — the
                # ones worth acting on first. Color only, no logic
                # here; severity itself was decided in the analyzer.
                if opp.severity == "high":
                    item.setForeground(QColor("#ff6b6b"))
                self.setItem(row_index, col_index, item)

        self.setSortingEnabled(True)
        self.resizeColumnsToContents()
