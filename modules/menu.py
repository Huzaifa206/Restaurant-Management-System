from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QTableWidget, QTableWidgetItem, QDialog,
                              QFormLayout, QLineEdit, QComboBox, QDoubleSpinBox,
                              QTextEdit, QCheckBox, QMessageBox)
from PyQt6.QtGui import QFont, QColor
from database.connection import execute_query


class MenuWindow(QWidget):
    """View, add, edit and toggle availability of menu items."""

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setup_ui()
        self.load_menu()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QHBoxLayout()
        title = QLabel("🍛 Menu Management")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.addWidget(title)
        header.addStretch()

        add_btn = QPushButton("+ Add Item")
        add_btn.setStyleSheet("background:#e67e22; color:white; padding:8px 15px; border-radius:6px;")
        add_btn.clicked.connect(self.add_item_dialog)
        header.addWidget(add_btn)

        add_cat_btn = QPushButton("+ Add Category")
        add_cat_btn.setStyleSheet("background:#9b59b6; color:white; padding:8px 15px; border-radius:6px;")
        add_cat_btn.clicked.connect(self.add_category_dialog)
        header.addWidget(add_cat_btn)

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_menu)
        header.addWidget(refresh_btn)
        layout.addLayout(header)

        # Filter by category
        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Filter by Category:"))
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories", None)
        self.category_filter.currentIndexChanged.connect(self.load_menu)
        filter_row.addWidget(self.category_filter)
        filter_row.addStretch()
        layout.addLayout(filter_row)

        # Menu items table
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Item Name", "Category", "Price (Rs.)", "Description", "Available"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        # Action buttons
        btn_row = QHBoxLayout()
        edit_btn = QPushButton("✏️ Edit Selected")
        edit_btn.clicked.connect(self.edit_item_dialog)

        toggle_btn = QPushButton("🔁 Toggle Availability")
        toggle_btn.setStyleSheet("background:#3498db; color:white; border-radius:5px; padding:6px;")
        toggle_btn.clicked.connect(self.toggle_availability)

        delete_btn = QPushButton("🗑️ Delete Selected")
        delete_btn.setStyleSheet("background:#e74c3c; color:white; border-radius:5px; padding:6px;")
        delete_btn.clicked.connect(self.delete_item)

        btn_row.addWidget(edit_btn)
        btn_row.addWidget(toggle_btn)
        btn_row.addWidget(delete_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.load_categories_into_filter()

    def load_categories_into_filter(self):
        cats = execute_query("SELECT category_id, category_name FROM categories ORDER BY category_name",
                             fetch=True)
        self.category_filter.blockSignals(True)
        # Keep "All Categories" at index 0, add the rest
        while self.category_filter.count() > 1:
            self.category_filter.removeItem(1)
        for c in cats:
            self.category_filter.addItem(c["category_name"], c["category_id"])
        self.category_filter.blockSignals(False)

    def load_menu(self):
        cat_id = self.category_filter.currentData()
        if cat_id:
            items = execute_query(
                "SELECT m.item_id, m.item_name, c.category_name, m.price, "
                "m.description, m.is_available "
                "FROM menu_items m JOIN categories c ON m.category_id = c.category_id "
                "WHERE m.category_id = ? ORDER BY m.item_name",
                (cat_id,), fetch=True
            )
        else:
            items = execute_query(
                "SELECT m.item_id, m.item_name, c.category_name, m.price, "
                "m.description, m.is_available "
                "FROM menu_items m JOIN categories c ON m.category_id = c.category_id "
                "ORDER BY c.category_name, m.item_name",
                fetch=True
            )

        self.table.setRowCount(len(items))
        for row, item in enumerate(items):
            available = "✅ Yes" if item["is_available"] else "❌ No"
            values = [
                str(item["item_id"]),
                item["item_name"],
                item["category_name"],
                f"Rs. {item['price']:.0f}",
                item["description"] or "",
                available
            ]
            for col, val in enumerate(values):
                cell = QTableWidgetItem(val)
                if not item["is_available"]:
                    cell.setForeground(QColor("#aaa"))
                self.table.setItem(row, col, cell)

    def toggle_availability(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select Item", "Please select a menu item first.")
            return
        item_id = int(self.table.item(row, 0).text())
        execute_query(
            "UPDATE menu_items SET is_available = CASE WHEN is_available = 1 THEN 0 ELSE 1 END "
            "WHERE item_id = ?",
            (item_id,)
        )
        self.load_menu()

    def delete_item(self):
        row = self.table.currentRow()
        if row < 0:
            return
        item_id = int(self.table.item(row, 0).text())
        name = self.table.item(row, 1).text()
        reply = QMessageBox.question(self, "Confirm Delete", f"Delete '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                execute_query("DELETE FROM menu_items WHERE item_id = ?", (item_id,))
                self.load_menu()
            except Exception as e:
                QMessageBox.critical(self, "Error",
                    f"Cannot delete — item may be linked to existing orders.\n{e}")

    def add_item_dialog(self):
        cats = execute_query("SELECT category_id, category_name FROM categories", fetch=True)
        dialog = MenuItemDialog(self, cats)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            execute_query(
                "INSERT INTO menu_items (category_id, item_name, description, price) "
                "VALUES (?, ?, ?, ?)",
                (data["category_id"], data["name"], data["description"], data["price"])
            )
            self.load_menu()

    def edit_item_dialog(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select Item", "Please select a menu item first.")
            return
        item_id = int(self.table.item(row, 0).text())
        item_data = execute_query(
            "SELECT * FROM menu_items WHERE item_id = ?", (item_id,), fetch=True)[0]
        cats = execute_query("SELECT category_id, category_name FROM categories", fetch=True)
        dialog = MenuItemDialog(self, cats, item_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            execute_query(
                "UPDATE menu_items SET category_id=?, item_name=?, description=?, price=? "
                "WHERE item_id=?",
                (data["category_id"], data["name"], data["description"], data["price"], item_id)
            )
            self.load_menu()

    def add_category_dialog(self):
        dialog = AddCategoryDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = dialog.get_name()
            if name:
                execute_query("INSERT INTO categories (category_name) VALUES (?)", (name,))
                self.load_categories_into_filter()
                QMessageBox.information(self, "✅ Done", f"Category '{name}' added.")


class MenuItemDialog(QDialog):
    """Add or Edit a menu item."""
    def __init__(self, parent, categories, item_data=None):
        super().__init__(parent)
        self.categories = categories
        self.setWindowTitle("Edit Menu Item" if item_data else "Add Menu Item")
        self.setFixedSize(380, 300)
        layout = QFormLayout(self)

        self.name_input = QLineEdit()
        self.desc_input = QTextEdit()
        self.desc_input.setFixedHeight(60)
        self.price_input = QDoubleSpinBox()
        self.price_input.setMaximum(99999)
        self.price_input.setPrefix("Rs. ")
        self.cat_combo = QComboBox()
        for c in categories:
            self.cat_combo.addItem(c["category_name"], c["category_id"])

        if item_data:
            self.name_input.setText(item_data["item_name"])
            self.desc_input.setText(item_data["description"] or "")
            self.price_input.setValue(float(item_data["price"]))
            for i, c in enumerate(categories):
                if c["category_id"] == item_data["category_id"]:
                    self.cat_combo.setCurrentIndex(i)
                    break

        layout.addRow("Category:", self.cat_combo)
        layout.addRow("Item Name:", self.name_input)
        layout.addRow("Description:", self.desc_input)
        layout.addRow("Price:", self.price_input)

        save_btn = QPushButton("Save")
        save_btn.setStyleSheet("background:#e67e22; color:white; padding:8px; border-radius:6px;")
        save_btn.clicked.connect(self.accept)
        layout.addRow(save_btn)

    def get_data(self):
        return {
            "category_id": self.cat_combo.currentData(),
            "name": self.name_input.text().strip(),
            "description": self.desc_input.toPlainText().strip(),
            "price": self.price_input.value(),
        }


class AddCategoryDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Add Category")
        self.setFixedSize(280, 120)
        layout = QFormLayout(self)
        self.name_input = QLineEdit()
        layout.addRow("Category Name:", self.name_input)
        btn = QPushButton("Add")
        btn.setStyleSheet("background:#9b59b6; color:white; padding:6px; border-radius:5px;")
        btn.clicked.connect(self.accept)
        layout.addRow(btn)

    def get_name(self):
        return self.name_input.text().strip()