from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QTableWidget, QTableWidgetItem, QTabWidget,
                              QListWidget, QSpinBox, QMessageBox, QComboBox, QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from database.connection import execute_query, get_all_menu_items


class CustomerPanel(QWidget):
    """Customer-facing panel — View Menu, Place Orders, Track Orders."""

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.cart = []   # Items added before placing order
        self.setWindowTitle("Restaurant — Customer Panel")
        self.setMinimumSize(900, 600)
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

        welcome = QLabel(f"🍽️  Welcome, {self.user['full_name']}")
        welcome.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        welcome.setStyleSheet("color: white;")
        top_layout.addWidget(welcome)
        top_layout.addStretch()

        logout_btn = QPushButton("Logout")
        logout_btn.setFixedSize(80, 32)
        logout_btn.setStyleSheet("background:white; color:#c0392b; border-radius:5px; font-weight:bold;")
        logout_btn.clicked.connect(self.logout)
        top_layout.addWidget(logout_btn)

        main_layout.addWidget(topbar)

        # Tabs
        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        tabs.addTab(self.build_menu_tab(), "🍛  View Menu & Order")
        tabs.addTab(self.build_track_tab(), "📦  Track My Orders")
        main_layout.addWidget(tabs)

    # ── Tab 1: Menu + Cart ───────────────────────────────────────────

    def build_menu_tab(self):
        page = QWidget()
        layout = QHBoxLayout(page)
        layout.setContentsMargins(15, 15, 15, 15)

        # LEFT — Menu list
        left = QVBoxLayout()
        left.addWidget(QLabel("📋 Menu", font=QFont("Arial", 13, QFont.Weight.Bold)))

        # Category filter
        self.menu_category_filter = QComboBox()
        self.menu_category_filter.addItem("All Categories", None)
        cats = execute_query("SELECT category_id, category_name FROM categories ORDER BY category_name",
                             fetch=True)
        for c in cats:
            self.menu_category_filter.addItem(c["category_name"], c["category_id"])
        self.menu_category_filter.currentIndexChanged.connect(self.load_menu)
        left.addWidget(self.menu_category_filter)

        self.menu_table = QTableWidget(0, 3)
        self.menu_table.setHorizontalHeaderLabels(["Item", "Category", "Price"])
        self.menu_table.horizontalHeader().setStretchLastSection(True)
        self.menu_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.menu_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        left.addWidget(self.menu_table)

        # Quantity + Add to cart
        qty_row = QHBoxLayout()
        qty_row.addWidget(QLabel("Quantity:"))
        self.qty_spin = QSpinBox()
        self.qty_spin.setMinimum(1)
        self.qty_spin.setMaximum(20)
        qty_row.addWidget(self.qty_spin)
        add_btn = QPushButton("🛒 Add to Cart")
        add_btn.setStyleSheet("background:#e67e22; color:white; border-radius:6px; padding:6px 12px;")
        add_btn.clicked.connect(self.add_to_cart)
        qty_row.addWidget(add_btn)
        left.addLayout(qty_row)

        # RIGHT — Cart
        right = QVBoxLayout()
        right.addWidget(QLabel("🛒 My Cart", font=QFont("Arial", 13, QFont.Weight.Bold)))

        self.cart_table = QTableWidget(0, 4)
        self.cart_table.setHorizontalHeaderLabels(["Item", "Qty", "Price", "Subtotal"])
        self.cart_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        right.addWidget(self.cart_table)

        remove_btn = QPushButton("❌ Remove Selected")
        remove_btn.clicked.connect(self.remove_from_cart)
        right.addWidget(remove_btn)

        self.cart_total_label = QLabel("Total: Rs. 0")
        self.cart_total_label.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        self.cart_total_label.setStyleSheet("color: #c0392b;")
        right.addWidget(self.cart_total_label)

        # Order type
        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("Order Type:"))
        self.order_type = QComboBox()
        self.order_type.addItems(["Dine-in", "Takeaway", "Online"])
        type_row.addWidget(self.order_type)
        right.addLayout(type_row)

        place_btn = QPushButton("✅ Place Order")
        place_btn.setFixedHeight(45)
        place_btn.setStyleSheet(
            "background:#27ae60; color:white; font-size:14px; "
            "font-weight:bold; border-radius:8px;")
        place_btn.clicked.connect(self.place_order)
        right.addWidget(place_btn)

        clear_btn = QPushButton("🗑️ Clear Cart")
        clear_btn.clicked.connect(self.clear_cart)
        right.addWidget(clear_btn)

        # Combine left and right
        left_widget = QWidget()
        left_widget.setLayout(left)
        right_widget = QWidget()
        right_widget.setLayout(right)

        layout.addWidget(left_widget, 6)   # 60% width
        layout.addWidget(right_widget, 4)  # 40% width

        self.load_menu()
        return page

    def load_menu(self):
        cat_id = self.menu_category_filter.currentData()
        if cat_id:
            items = execute_query(
                "SELECT m.item_id, m.item_name, c.category_name, m.price "
                "FROM menu_items m JOIN categories c ON m.category_id = c.category_id "
                "WHERE m.is_available = 1 AND m.category_id = ? ORDER BY m.item_name",
                (cat_id,), fetch=True
            )
        else:
            items = execute_query(
                "SELECT m.item_id, m.item_name, c.category_name, m.price "
                "FROM menu_items m JOIN categories c ON m.category_id = c.category_id "
                "WHERE m.is_available = 1 ORDER BY c.category_name, m.item_name",
                fetch=True
            )
        self.menu_items_data = items
        self.menu_table.setRowCount(len(items))
        for row, item in enumerate(items):
            self.menu_table.setItem(row, 0, QTableWidgetItem(item["item_name"]))
            self.menu_table.setItem(row, 1, QTableWidgetItem(item["category_name"]))
            self.menu_table.setItem(row, 2, QTableWidgetItem(f"Rs. {item['price']:.0f}"))

    def add_to_cart(self):
        idx = self.menu_table.currentRow()
        if idx < 0:
            QMessageBox.warning(self, "Select Item", "Please select a menu item first.")
            return
        item = self.menu_items_data[idx]
        qty = self.qty_spin.value()

        for existing in self.cart:
            if existing["item_id"] == item["item_id"]:
                existing["qty"] += qty
                self.refresh_cart()
                return

        self.cart.append({
            "item_id": item["item_id"],
            "name": item["item_name"],
            "price": float(item["price"]),
            "qty": qty,
        })
        self.refresh_cart()

    def remove_from_cart(self):
        row = self.cart_table.currentRow()
        if row < 0:
            return
        self.cart.pop(row)
        self.refresh_cart()

    def refresh_cart(self):
        self.cart_table.setRowCount(len(self.cart))
        total = 0
        for row, item in enumerate(self.cart):
            subtotal = item["price"] * item["qty"]
            total += subtotal
            self.cart_table.setItem(row, 0, QTableWidgetItem(item["name"]))
            self.cart_table.setItem(row, 1, QTableWidgetItem(str(item["qty"])))
            self.cart_table.setItem(row, 2, QTableWidgetItem(f"Rs. {item['price']:.0f}"))
            self.cart_table.setItem(row, 3, QTableWidgetItem(f"Rs. {subtotal:.0f}"))
        self.cart_total_label.setText(f"Total: Rs. {total:,.0f}")

    def clear_cart(self):
        self.cart = []
        self.refresh_cart()

    def place_order(self):
        if not self.cart:
            QMessageBox.warning(self, "Empty Cart", "Please add items to your cart first.")
            return
        order_type = self.order_type.currentText()
        try:
            execute_query(
                "INSERT INTO orders (branch_id, staff_id, order_type, status) "
                "VALUES (?, ?, ?, 'Pending')",
                (self.user.get("branch_id", 1), self.user["staff_id"], order_type)
            )
            order_id = execute_query(
                "SELECT TOP 1 order_id FROM orders ORDER BY order_id DESC",
                fetch=True)[0]["order_id"]

            for item in self.cart:
                execute_query(
                    "INSERT INTO order_details (order_id, item_id, quantity, unit_price) "
                    "VALUES (?, ?, ?, ?)",
                    (order_id, item["item_id"], item["qty"], item["price"])
                )
            execute_query(
                "UPDATE orders SET total_amount = "
                "(SELECT SUM(quantity * unit_price) FROM order_details WHERE order_id = ?) "
                "WHERE order_id = ?",
                (order_id, order_id)
            )
            QMessageBox.information(self, "✅ Order Placed",
                f"Your order #{order_id} has been placed!\n"
                f"Go to 'Track My Orders' tab to follow its status.")
            self.clear_cart()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # ── Tab 2: Track Orders ──────────────────────────────────────────

    def build_track_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(15, 15, 15, 15)

        header = QHBoxLayout()
        header.addWidget(QLabel("📦 My Orders", font=QFont("Arial", 13, QFont.Weight.Bold)))
        header.addStretch()
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_my_orders)
        header.addWidget(refresh_btn)
        layout.addLayout(header)

        self.orders_track_table = QTableWidget(0, 4)
        self.orders_track_table.setHorizontalHeaderLabels(
            ["Order ID", "Type", "Status", "Ordered At"])
        self.orders_track_table.horizontalHeader().setStretchLastSection(True)
        self.orders_track_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.orders_track_table)

        # Status guide
        guide = QHBoxLayout()
        for status, color, meaning in [
            ("Pending",    "#e74c3c", "Waiting for kitchen"),
            ("In-Kitchen", "#e67e22", "Being prepared"),
            ("Ready",      "#3498db", "Ready to serve"),
            ("Served",     "#27ae60", "Enjoy your meal!"),
        ]:
            lbl = QLabel(f"⬤  {status} — {meaning}")
            lbl.setStyleSheet(f"color:{color}; font-size:12px;")
            guide.addWidget(lbl)
        guide.addStretch()
        layout.addLayout(guide)

        self.load_my_orders()

        # Auto-refresh every 20 seconds
        self.track_timer = QTimer()
        self.track_timer.timeout.connect(self.load_my_orders)
        self.track_timer.start(20000)

        return page

    def load_my_orders(self):
        orders = execute_query(
            "SELECT order_id, order_type, status, order_time "
            "FROM orders WHERE staff_id = ? ORDER BY order_time DESC",
            (self.user["staff_id"],), fetch=True
        )
        status_colors = {
            "Pending": "#e74c3c", "In-Kitchen": "#e67e22",
            "Ready": "#3498db",   "Served": "#27ae60", "Completed": "#27ae60"
        }
        self.orders_track_table.setRowCount(len(orders))
        for row, o in enumerate(orders):
            self.orders_track_table.setItem(row, 0, QTableWidgetItem(str(o["order_id"])))
            self.orders_track_table.setItem(row, 1, QTableWidgetItem(o["order_type"]))
            status_item = QTableWidgetItem(o["status"])
            color = status_colors.get(o["status"], "#333")
            status_item.setForeground(Qt.GlobalColor.white)
            from PyQt6.QtGui import QColor
            status_item.setBackground(QColor(color))
            self.orders_track_table.setItem(row, 2, status_item)
            self.orders_track_table.setItem(row, 3, QTableWidgetItem(str(o["order_time"])))

    def logout(self):
        from modules.login import LoginWindow
        self.login = LoginWindow()
        self.login.show()
        self.close()

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget { background: #f5f5f5; font-family: Arial; font-size: 13px; }
            QFrame#topbar { background: #c0392b; }
            QTabWidget::pane { border: none; background: #f5f5f5; }
            QTabBar::tab {
                background: #ddd; padding: 10px 20px; font-size: 13px;
                border-top-left-radius: 6px; border-top-right-radius: 6px;
            }
            QTabBar::tab:selected { background: #c0392b; color: white; font-weight: bold; }
            QTableWidget { background: white; border: 1px solid #ddd; border-radius: 6px; }
            QHeaderView::section { background: #1a1a2e; color: white; padding: 6px; }
            QPushButton {
                background: #1a1a2e; color: white; border: none;
                border-radius: 6px; padding: 6px 12px;
            }
            QPushButton:hover { background: #16213e; }
            QComboBox { padding: 4px 8px; border: 1px solid #ddd; border-radius: 5px; background:white; color:#333; }
            QSpinBox  { padding: 4px 8px; border: 1px solid #ddd; border-radius: 5px; background:white; color:#333; }
        """)