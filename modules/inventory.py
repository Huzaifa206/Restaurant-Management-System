from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QTableWidget, QTableWidgetItem, QLineEdit,
                              QDialog, QFormLayout, QDoubleSpinBox, QComboBox, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from database.connection import execute_query


class InventoryWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.branch_id = user.get("branch_id", 1)
        self.setup_ui()
        self.load_inventory()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QHBoxLayout()
        title = QLabel("📦 Inventory Management")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.addWidget(title)
        header.addStretch()

        add_btn = QPushButton("+ Add Item")
        add_btn.setStyleSheet("background:#2ecc71; color:white; padding:8px 15px; border-radius:6px;")
        add_btn.clicked.connect(self.add_item_dialog)
        header.addWidget(add_btn)

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_inventory)
        header.addWidget(refresh_btn)
        layout.addLayout(header)

        # Low stock alert banner
        self.alert_label = QLabel("")
        self.alert_label.setStyleSheet("background:#ffeaa7; padding:8px; border-radius:5px; color:#d35400;")
        self.alert_label.setVisible(False)
        layout.addWidget(self.alert_label)

        # Inventory table
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Item Name", "Unit", "In Stock", "Reorder Level", "Status"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        # Action buttons
        btn_row = QHBoxLayout()
        edit_btn = QPushButton("✏️ Edit Selected")
        edit_btn.clicked.connect(self.edit_item)
        update_stock_btn = QPushButton("📥 Update Stock")
        update_stock_btn.setStyleSheet("background:#3498db; color:white; border-radius:5px; padding:6px;")
        update_stock_btn.clicked.connect(self.update_stock_dialog)
        btn_row.addWidget(edit_btn)
        btn_row.addWidget(update_stock_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

    def load_inventory(self):
        items = execute_query(
            "SELECT inventory_id, item_name, unit, quantity_in_stock, reorder_level "
            "FROM inventory WHERE branch_id = ? ORDER BY item_name",
            (self.branch_id,), fetch=True
        )

        low_stock_count = 0
        self.table.setRowCount(len(items))

        for row, item in enumerate(items):
            is_low = item["quantity_in_stock"] <= item["reorder_level"]
            if is_low:
                low_stock_count += 1

            status = "⚠️ LOW STOCK" if is_low else "✅ OK"
            values = [
                str(item["inventory_id"]),
                item["item_name"],
                item["unit"] or "",
                str(item["quantity_in_stock"]),
                str(item["reorder_level"]),
                status
            ]
            for col, val in enumerate(values):
                cell = QTableWidgetItem(val)
                if is_low:
                    cell.setBackground(QColor("#ffcccc"))
                self.table.setItem(row, col, cell)

        if low_stock_count > 0:
            self.alert_label.setText(f"⚠️ {low_stock_count} item(s) are running low on stock!")
            self.alert_label.setVisible(True)
        else:
            self.alert_label.setVisible(False)

    def add_item_dialog(self):
        dialog = InventoryDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            execute_query(
                "INSERT INTO inventory (branch_id, item_name, unit, quantity_in_stock, reorder_level) "
                "VALUES (?, ?, ?, ?, ?)",
                (self.branch_id, data["name"], data["unit"], data["qty"], data["reorder"])
            )
            self.load_inventory()

    def update_stock_dialog(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select Item", "Please select an inventory item.")
            return
        item_id = int(self.table.item(row, 0).text())
        item_name = self.table.item(row, 1).text()

        dialog = UpdateStockDialog(self, item_name)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            amount = dialog.get_amount()
            execute_query(
                "UPDATE inventory SET quantity_in_stock = quantity_in_stock + ?, "
                "last_updated = GETDATE() WHERE inventory_id = ?",
                (amount, item_id)
            )
            self.load_inventory()

    def edit_item(self):
        row = self.table.currentRow()
        if row < 0:
            return
        QMessageBox.information(self, "Edit", "Edit functionality — extend as needed.")


class InventoryDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Add Inventory Item")
        self.setFixedSize(350, 250)
        layout = QFormLayout(self)

        self.name_input = QLineEdit()
        self.unit_input = QComboBox()
        self.unit_input.addItems(["kg", "liters", "pieces", "grams", "packs"])
        self.qty_input = QDoubleSpinBox()
        self.qty_input.setMaximum(99999)
        self.reorder_input = QDoubleSpinBox()
        self.reorder_input.setMaximum(99999)
        self.reorder_input.setValue(10)

        layout.addRow("Item Name:", self.name_input)
        layout.addRow("Unit:", self.unit_input)
        layout.addRow("Initial Quantity:", self.qty_input)
        layout.addRow("Reorder Level:", self.reorder_input)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        layout.addRow(save_btn)

    def get_data(self):
        return {
            "name": self.name_input.text(),
            "unit": self.unit_input.currentText(),
            "qty": self.qty_input.value(),
            "reorder": self.reorder_input.value()
        }


class UpdateStockDialog(QDialog):
    def __init__(self, parent, item_name):
        super().__init__(parent)
        self.setWindowTitle(f"Update Stock — {item_name}")
        self.setFixedSize(280, 150)
        layout = QFormLayout(self)
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMaximum(99999)
        layout.addRow("Add Quantity:", self.amount_input)
        save_btn = QPushButton("Update")
        save_btn.clicked.connect(self.accept)
        layout.addRow(save_btn)

    def get_amount(self):
        return self.amount_input.value()