from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QTableWidget, QTableWidgetItem, QFrame,
                              QMessageBox, QTabWidget)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt
from database.connection import execute_query


class SupplierPanel(QWidget):
    """Supplier-facing panel — view purchase orders, mark deliveries."""

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("Restaurant — Supplier Panel")
        self.setMinimumSize(800, 500)
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Top bar
        topbar = QFrame()
        topbar.setObjectName("topbar")
        topbar.setFixedHeight(60)
        top_layout = QHBoxLayout(topbar)
        top_layout.setContentsMargins(20, 0, 20, 0)

        title = QLabel(f"🚚  Supplier Portal — {self.user['full_name']}")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        top_layout.addWidget(title)
        top_layout.addStretch()

        logout_btn = QPushButton("Logout")
        logout_btn.setFixedSize(80, 32)
        logout_btn.setStyleSheet("background:white; color:#2c3e50; border-radius:5px; font-weight:bold;")
        logout_btn.clicked.connect(self.logout)
        top_layout.addWidget(logout_btn)

        main_layout.addWidget(topbar)

        # Tabs
        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        tabs.addTab(self.build_orders_tab(),    "📋  Purchase Orders")
        tabs.addTab(self.build_inventory_tab(), "📦  Items I Supply")
        main_layout.addWidget(tabs)

    # ── Tab 1: Purchase Orders ───────────────────────────────────────

    def build_orders_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(15, 15, 15, 15)

        header = QHBoxLayout()
        header.addWidget(QLabel("📋 Orders from Restaurant",
                                font=QFont("Arial", 13, QFont.Weight.Bold)))
        header.addStretch()
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_purchase_orders)
        header.addWidget(refresh_btn)
        layout.addLayout(header)

        layout.addWidget(QLabel("Select a pending order and click 'Mark as Delivered' once you supply the items."))

        self.purchases_table = QTableWidget(0, 6)
        self.purchases_table.setHorizontalHeaderLabels(
            ["Purchase ID", "Item", "Quantity", "Unit Price", "Total Cost", "Status"])
        self.purchases_table.horizontalHeader().setStretchLastSection(True)
        self.purchases_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.purchases_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.purchases_table)

        deliver_btn = QPushButton("✅ Mark as Delivered")
        deliver_btn.setFixedHeight(40)
        deliver_btn.setStyleSheet(
            "background:#27ae60; color:white; font-size:13px; "
            "font-weight:bold; border-radius:8px;")
        deliver_btn.clicked.connect(self.mark_delivered)
        layout.addWidget(deliver_btn)

        self.load_purchase_orders()
        return page

    def load_purchase_orders(self):
        # Get this supplier's ID from the suppliers table by matching staff name
        supplier = execute_query(
            "SELECT supplier_id FROM suppliers WHERE supplier_name = ?",
            (self.user["full_name"],), fetch=True
        )
        if not supplier:
            self.purchases_table.setRowCount(0)
            return

        supplier_id = supplier[0]["supplier_id"]
        purchases = execute_query(
            "SELECT p.purchase_id, i.item_name, p.quantity, p.unit_price, "
            "p.total_cost, p.status, p.purchase_date "
            "FROM purchases p JOIN inventory i ON p.inventory_id = i.inventory_id "
            "WHERE p.supplier_id = ? ORDER BY p.purchase_date DESC",
            (supplier_id,), fetch=True
        )
        self.purchases_table.setRowCount(len(purchases))
        for row, p in enumerate(purchases):
            values = [
                str(p["purchase_id"]),
                p["item_name"],
                str(p["quantity"]),
                f"Rs. {p['unit_price']:.0f}",
                f"Rs. {p['total_cost']:.0f}",
                p["status"],
            ]
            for col, val in enumerate(values):
                cell = QTableWidgetItem(val)
                if p["status"] == "Delivered":
                    cell.setForeground(QColor("#27ae60"))
                elif p["status"] == "Ordered":
                    cell.setForeground(QColor("#e67e22"))
                self.purchases_table.setItem(row, col, cell)

    def mark_delivered(self):
        row = self.purchases_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select Order", "Please select a purchase order first.")
            return
        purchase_id = int(self.purchases_table.item(row, 0).text())
        status = self.purchases_table.item(row, 5).text()
        if status == "Delivered":
            QMessageBox.information(self, "Already Delivered", "This order is already marked as delivered.")
            return

        qty = float(self.purchases_table.item(row, 2).text())
        reply = QMessageBox.question(self, "Confirm Delivery",
            f"Mark Purchase #{purchase_id} as delivered and update stock?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Mark delivered
                execute_query(
                    "UPDATE purchases SET status = 'Delivered' WHERE purchase_id = ?",
                    (purchase_id,)
                )
                # Update inventory stock
                execute_query(
                    "UPDATE inventory SET quantity_in_stock = quantity_in_stock + ?, "
                    "last_updated = GETDATE() "
                    "WHERE inventory_id = (SELECT inventory_id FROM purchases WHERE purchase_id = ?)",
                    (qty, purchase_id)
                )
                QMessageBox.information(self, "✅ Done",
                    "Delivery confirmed and stock updated successfully!")
                self.load_purchase_orders()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    # ── Tab 2: Items I Supply ────────────────────────────────────────

    def build_inventory_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(15, 15, 15, 15)

        layout.addWidget(QLabel("📦 Inventory Items Linked to You",
                                font=QFont("Arial", 13, QFont.Weight.Bold)))
        layout.addWidget(QLabel("These are the raw materials the restaurant orders from you."))

        self.inventory_table = QTableWidget(0, 4)
        self.inventory_table.setHorizontalHeaderLabels(
            ["Item", "Unit", "Current Stock", "Reorder Level"])
        self.inventory_table.horizontalHeader().setStretchLastSection(True)
        self.inventory_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.inventory_table)

        self.load_supplier_inventory()
        return page

    def load_supplier_inventory(self):
        supplier = execute_query(
            "SELECT supplier_id FROM suppliers WHERE supplier_name = ?",
            (self.user["full_name"],), fetch=True
        )
        if not supplier:
            return
        supplier_id = supplier[0]["supplier_id"]
        items = execute_query(
            "SELECT item_name, unit, quantity_in_stock, reorder_level "
            "FROM inventory WHERE supplier_id = ?",
            (supplier_id,), fetch=True
        )
        self.inventory_table.setRowCount(len(items))
        for row, item in enumerate(items):
            is_low = item["quantity_in_stock"] <= item["reorder_level"]
            values = [item["item_name"], item["unit"] or "",
                      str(item["quantity_in_stock"]), str(item["reorder_level"])]
            for col, val in enumerate(values):
                cell = QTableWidgetItem(val)
                if is_low:
                    cell.setBackground(QColor("#ffcccc"))
                self.inventory_table.setItem(row, col, cell)

    def logout(self):
        from modules.login import LoginWindow
        self.login = LoginWindow()
        self.login.show()
        self.close()

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget { background: #f5f5f5; font-family: Arial; font-size: 13px; }
            QFrame#topbar { background: #2c3e50; }
            QTabWidget::pane { border: none; }
            QTabBar::tab {
                background: #ddd; padding: 10px 20px; font-size: 13px;
                border-top-left-radius: 6px; border-top-right-radius: 6px;
            }
            QTabBar::tab:selected { background: #2c3e50; color: white; font-weight: bold; }
            QTableWidget { background: white; border: 1px solid #ddd; border-radius: 6px; }
            QHeaderView::section { background: #2c3e50; color: white; padding: 6px; }
            QPushButton {
                background: #2c3e50; color: white; border: none;
                border-radius: 6px; padding: 6px 12px;
            }
            QPushButton:hover { background: #1a252f; }
        """)