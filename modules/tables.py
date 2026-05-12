from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QGridLayout, QFrame, QDialog, QFormLayout,
                              QSpinBox, QComboBox, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from database.connection import execute_query


# Colour for each table status
STATUS_COLORS = {
    "Available": "#2ecc71",   # green
    "Occupied":  "#e74c3c",   # red
    "Reserved":  "#f39c12",   # orange
}


class TableWindow(QWidget):
    """Visual grid of all restaurant tables with live status."""

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.branch_id = user.get("branch_id", 1)
        self.setup_ui()
        self.load_tables()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QHBoxLayout()
        title = QLabel("🪑 Table Management")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.addWidget(title)
        header.addStretch()

        add_btn = QPushButton("+ Add Table")
        add_btn.setStyleSheet("background:#3498db; color:white; padding:8px 15px; border-radius:6px;")
        add_btn.clicked.connect(self.add_table_dialog)
        header.addWidget(add_btn)

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_tables)
        header.addWidget(refresh_btn)
        layout.addLayout(header)

        # Legend
        legend = QHBoxLayout()
        for status, color in STATUS_COLORS.items():
            dot = QLabel(f"⬤  {status}")
            dot.setStyleSheet(f"color: {color}; font-size: 13px;")
            legend.addWidget(dot)
        legend.addStretch()
        layout.addLayout(legend)

        # Scrollable grid of table cards
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(15)
        layout.addWidget(self.grid_widget)
        layout.addStretch()

    def load_tables(self):
        # Clear old cards
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        tables = execute_query(
            "SELECT table_id, table_number, capacity, status "
            "FROM restaurant_tables WHERE branch_id = ? ORDER BY table_number",
            (self.branch_id,), fetch=True
        )

        for idx, t in enumerate(tables):
            card = self.create_table_card(t)
            row, col = divmod(idx, 5)   # 5 cards per row
            self.grid_layout.addWidget(card, row, col)

    def create_table_card(self, table):
        color = STATUS_COLORS.get(table["status"], "#95a5a6")
        card = QFrame()
        card.setFixedSize(130, 130)
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 3px solid {color};
                border-radius: 12px;
            }}
            QFrame:hover {{ background: #f8f9fa; }}
        """)
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        num_label = QLabel(f"Table {table['table_number']}")
        num_label.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        num_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        cap_label = QLabel(f"👥 {table['capacity']} seats")
        cap_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cap_label.setStyleSheet("color: #666; font-size: 11px;")

        status_label = QLabel(table["status"])
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 12px;")

        # Change status button
        change_btn = QPushButton("Change")
        change_btn.setFixedHeight(24)
        change_btn.setStyleSheet(f"""
            QPushButton {{
                background: {color}; color: white;
                border: none; border-radius: 4px; font-size: 11px;
            }}
        """)
        change_btn.clicked.connect(
            lambda _, tid=table["table_id"], ts=table["status"]: self.change_status_dialog(tid, ts)
        )

        layout.addWidget(num_label)
        layout.addWidget(cap_label)
        layout.addWidget(status_label)
        layout.addWidget(change_btn)
        return card

    def change_status_dialog(self, table_id, current_status):
        dialog = ChangeStatusDialog(self, current_status)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_status = dialog.get_status()
            execute_query(
                "UPDATE restaurant_tables SET status = ? WHERE table_id = ?",
                (new_status, table_id)
            )
            self.load_tables()

    def add_table_dialog(self):
        dialog = AddTableDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            number, capacity = dialog.get_data()
            # Check if table number already exists
            existing = execute_query(
                "SELECT COUNT(*) as cnt FROM restaurant_tables "
                "WHERE branch_id = ? AND table_number = ?",
                (self.branch_id, number), fetch=True
            )[0]["cnt"]
            if existing:
                QMessageBox.warning(self, "Duplicate", f"Table {number} already exists.")
                return
            execute_query(
                "INSERT INTO restaurant_tables (branch_id, table_number, capacity) VALUES (?, ?, ?)",
                (self.branch_id, number, capacity)
            )
            self.load_tables()


class ChangeStatusDialog(QDialog):
    def __init__(self, parent, current_status):
        super().__init__(parent)
        self.setWindowTitle("Change Table Status")
        self.setFixedSize(260, 130)
        layout = QFormLayout(self)
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Available", "Occupied", "Reserved"])
        self.status_combo.setCurrentText(current_status)
        layout.addRow("New Status:", self.status_combo)
        btn = QPushButton("Update")
        btn.setStyleSheet("background:#3498db; color:white; padding:6px; border-radius:5px;")
        btn.clicked.connect(self.accept)
        layout.addRow(btn)

    def get_status(self):
        return self.status_combo.currentText()


class AddTableDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Add New Table")
        self.setFixedSize(260, 150)
        layout = QFormLayout(self)
        self.number_spin = QSpinBox()
        self.number_spin.setMinimum(1)
        self.number_spin.setMaximum(999)
        self.capacity_spin = QSpinBox()
        self.capacity_spin.setMinimum(1)
        self.capacity_spin.setMaximum(20)
        self.capacity_spin.setValue(4)
        layout.addRow("Table Number:", self.number_spin)
        layout.addRow("Capacity (seats):", self.capacity_spin)
        btn = QPushButton("Add Table")
        btn.setStyleSheet("background:#2ecc71; color:white; padding:6px; border-radius:5px;")
        btn.clicked.connect(self.accept)
        layout.addRow(btn)

    def get_data(self):
        return self.number_spin.value(), self.capacity_spin.value()