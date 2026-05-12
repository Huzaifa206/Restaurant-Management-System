from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QTableWidget, QTableWidgetItem, QComboBox,
                              QSpinBox, QMessageBox, QFrame, QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from database.connection import execute_query, get_all_menu_items, get_all_tables


class OrderWindow(QWidget):
    def __init__(self, user, embedded=False):
        super().__init__()
        self.user = user
        self.current_order_items = []   # Items in current order
        self.selected_table = None
        self.setup_ui()
        self.load_data()

        # Auto-refresh every 30 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_active_orders)
        self.timer.start(30000)

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # ── LEFT: New Order Panel ────────────────────────
        left_panel = QFrame()
        left_panel.setFixedWidth(400)
        left_layout = QVBoxLayout(left_panel)

        left_layout.addWidget(QLabel("🆕 New Order", font=QFont("Arial", 14, QFont.Weight.Bold)))

        # Order type selector
        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("Type:"))
        self.order_type = QComboBox()
        self.order_type.addItems(["Dine-in", "Takeaway", "Online"])
        self.order_type.currentTextChanged.connect(self.on_order_type_changed)
        type_row.addWidget(self.order_type)
        left_layout.addLayout(type_row)

        # Table selector (visible for Dine-in)
        self.table_row = QHBoxLayout()
        self.table_row.addWidget(QLabel("Table:"))
        self.table_selector = QComboBox()
        self.table_row.addWidget(self.table_selector)
        left_layout.addLayout(self.table_row)

        # Menu items list
        left_layout.addWidget(QLabel("📋 Menu Items:"))
        self.menu_list = QListWidget()
        self.menu_list.itemDoubleClicked.connect(self.add_to_order)
        left_layout.addWidget(self.menu_list)

        # Quantity
        qty_row = QHBoxLayout()
        qty_row.addWidget(QLabel("Qty:"))
        self.qty_spin = QSpinBox()
        self.qty_spin.setMinimum(1)
        self.qty_spin.setMaximum(20)
        qty_row.addWidget(self.qty_spin)
        add_btn = QPushButton("Add to Order")
        add_btn.clicked.connect(self.add_to_order)
        qty_row.addWidget(add_btn)
        left_layout.addLayout(qty_row)

        # Current order table
        left_layout.addWidget(QLabel("🛒 Current Order:"))
        self.order_table = QTableWidget(0, 4)
        self.order_table.setHorizontalHeaderLabels(["Item", "Qty", "Price", "Subtotal"])
        self.order_table.setFixedHeight(200)
        self.order_table.horizontalHeader().setStretchLastSection(True)
        left_layout.addWidget(self.order_table)

        # Total
        self.total_label = QLabel("Total: Rs. 0")
        self.total_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        left_layout.addWidget(self.total_label)

        # Place order button
        place_btn = QPushButton("✅ Place Order")
        place_btn.setFixedHeight(45)
        place_btn.setStyleSheet("background:#27ae60; color:white; font-size:14px; border-radius:8px;")
        place_btn.clicked.connect(self.place_order)
        left_layout.addWidget(place_btn)

        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.clicked.connect(self.clear_order)
        left_layout.addWidget(clear_btn)

        # ── RIGHT: Active Orders ────────────────────────
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        right_layout.addWidget(QLabel("📋 Active Orders", font=QFont("Arial", 14, QFont.Weight.Bold)))

        self.active_orders_table = QTableWidget(0, 5)
        self.active_orders_table.setHorizontalHeaderLabels(
            ["Order ID", "Type", "Table", "Status", "Time"])
        self.active_orders_table.horizontalHeader().setStretchLastSection(True)
        right_layout.addWidget(self.active_orders_table)

        # Status update buttons
        btn_row = QHBoxLayout()
        for status, color in [("In-Kitchen", "#e67e22"), ("Ready", "#3498db"), ("Served", "#27ae60")]:
            btn = QPushButton(status)
            btn.setStyleSheet(f"background:{color}; color:white; border-radius:5px; padding:6px;")
            btn.clicked.connect(lambda checked, s=status: self.update_order_status(s))
            btn_row.addWidget(btn)
        right_layout.addLayout(btn_row)

        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)

    def load_data(self):
        # Load menu items
        self.menu_items_data = get_all_menu_items()
        self.menu_list.clear()
        for item in self.menu_items_data:
            self.menu_list.addItem(
                f"{item['item_name']} — Rs. {item['price']} ({item['category_name']})")

        # Load tables
        tables = get_all_tables(self.user.get("branch_id", 1))
        self.table_selector.clear()
        for t in tables:
            self.table_selector.addItem(
                f"Table {t['table_number']} ({t['status']})", t["table_id"])

        self.load_active_orders()

    def add_to_order(self):
        idx = self.menu_list.currentRow()
        if idx < 0:
            QMessageBox.warning(self, "Select Item", "Please select a menu item first.")
            return
        item = self.menu_items_data[idx]
        qty = self.qty_spin.value()

        # Check if item already in order
        for existing in self.current_order_items:
            if existing["item_id"] == item["item_id"]:
                existing["qty"] += qty
                self.refresh_order_table()
                return

        self.current_order_items.append({
            "item_id": item["item_id"],
            "name": item["item_name"],
            "price": float(item["price"]),
            "qty": qty,
        })
        self.refresh_order_table()

    def refresh_order_table(self):
        self.order_table.setRowCount(len(self.current_order_items))
        total = 0
        for row, item in enumerate(self.current_order_items):
            subtotal = item["price"] * item["qty"]
            total += subtotal
            self.order_table.setItem(row, 0, QTableWidgetItem(item["name"]))
            self.order_table.setItem(row, 1, QTableWidgetItem(str(item["qty"])))
            self.order_table.setItem(row, 2, QTableWidgetItem(f"Rs.{item['price']:.0f}"))
            self.order_table.setItem(row, 3, QTableWidgetItem(f"Rs.{subtotal:.0f}"))
        self.total_label.setText(f"Total: Rs. {total:,.0f}")

    def place_order(self):
        if not self.current_order_items:
            QMessageBox.warning(self, "Empty Order", "Please add items to the order.")
            return

        order_type = self.order_type.currentText()
        table_id = self.table_selector.currentData() if order_type == "Dine-in" else None

        try:
            # Insert order
            execute_query(
                "INSERT INTO orders (branch_id, table_id, staff_id, order_type, status) "
                "VALUES (?, ?, ?, ?, 'Pending')",
                (self.user.get("branch_id", 1), table_id, self.user["staff_id"], order_type)
            )
            # Get new order ID
            order_id = execute_query(
                "SELECT TOP 1 order_id FROM orders ORDER BY order_id DESC",
                fetch=True)[0]["order_id"]

            # Insert order details
            for item in self.current_order_items:
                execute_query(
                    "INSERT INTO order_details (order_id, item_id, quantity, unit_price) "
                    "VALUES (?, ?, ?, ?)",
                    (order_id, item["item_id"], item["qty"], item["price"])
                )

            # Update total
            execute_query(
                "UPDATE orders SET total_amount = "
                "(SELECT SUM(quantity * unit_price) FROM order_details WHERE order_id = ?) "
                "WHERE order_id = ?",
                (order_id, order_id)
            )

            QMessageBox.information(self, "✅ Success", f"Order #{order_id} placed successfully!")
            self.clear_order()
            self.load_active_orders()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to place order:\n{str(e)}")

    def clear_order(self):
        self.current_order_items = []
        self.order_table.setRowCount(0)
        self.total_label.setText("Total: Rs. 0")

    def load_active_orders(self):
        try:
            from database.connection import get_pending_orders
            orders = get_pending_orders()
            self.active_orders_table.setRowCount(len(orders))
            for row, o in enumerate(orders):
                self.active_orders_table.setItem(row, 0, QTableWidgetItem(str(o["order_id"])))
                self.active_orders_table.setItem(row, 1, QTableWidgetItem(o["order_type"]))
                table_num = str(o["table_number"]) if o["table_number"] else "N/A"
                self.active_orders_table.setItem(row, 2, QTableWidgetItem(table_num))
                self.active_orders_table.setItem(row, 3, QTableWidgetItem(o["status"]))
                self.active_orders_table.setItem(row, 4, QTableWidgetItem(str(o["order_time"])))
        except Exception as e:
            print(f"Error loading orders: {e}")

    def update_order_status(self, new_status):
        row = self.active_orders_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select Order", "Please select an order to update.")
            return
        order_id = int(self.active_orders_table.item(row, 0).text())
        execute_query("UPDATE orders SET status = ? WHERE order_id = ?", (new_status, order_id))
        self.load_active_orders()

    def on_order_type_changed(self, order_type):
        self.table_selector.setVisible(order_type == "Dine-in")