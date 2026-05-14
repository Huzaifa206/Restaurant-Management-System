# modules/kitchen.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QScrollArea, QFrame, QGridLayout)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from database.connection import execute_query


class KitchenDisplay(QWidget):
    """KDS — Kitchen Display System. Auto-refreshes every 15 seconds."""

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("Kitchen Display System")
        self.showMaximized()
        self.setup_ui()
        self.load_orders()

        self.timer = QTimer()
        self.timer.timeout.connect(self.load_orders)
        self.timer.start(15000)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # ── Header ────────────────────────────────────────────────────
        header = QHBoxLayout()

        title = QLabel("👨‍🍳 Kitchen Display System")
        title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: white; border: none; background: transparent;")
        header.addWidget(title)

        header.addStretch()

        # Chef name pill
        chef_lbl = QLabel(f"  {self.user['full_name']}  ")
        chef_lbl.setStyleSheet("""
            color: #aaa;
            background: #26262F;
            border-radius: 4px;
            padding: 4px 10px;
            font-size: 12px;
            border: none;
        """)
        header.addWidget(chef_lbl)

        header.addSpacing(8)

        # Refresh button
        refresh_btn = QPushButton("⟳  Refresh")
        refresh_btn.setFixedHeight(36)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: #F5A623;
                color: #000;
                border: none;
                border-radius: 5px;
                padding: 0 16px;
                font-size: 13px;
                font-weight: 700;
            }
            QPushButton:hover { background: #D4901E; }
        """)
        refresh_btn.clicked.connect(self.load_orders)
        header.addWidget(refresh_btn)

        header.addSpacing(8)

        # Logout button
        logout_btn = QPushButton("← Logout")
        logout_btn.setFixedHeight(36)
        logout_btn.setStyleSheet("""
            QPushButton {
                background: rgba(230, 57, 70, 0.15);
                color: #E63946;
                border: 1px solid rgba(230, 57, 70, 0.35);
                border-radius: 5px;
                padding: 0 16px;
                font-size: 13px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: #E63946;
                color: white;
                border-color: #E63946;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        header.addWidget(logout_btn)

        layout.addLayout(header)

        # ── Divider ───────────────────────────────────────────────────
        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background: #2A2A35; border: none;")
        layout.addWidget(divider)

        # ── Orders grid ───────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.orders_container = QWidget()
        self.orders_container.setStyleSheet("background: transparent;")
        self.orders_grid = QGridLayout(self.orders_container)
        self.orders_grid.setSpacing(16)
        self.orders_grid.setContentsMargins(0, 8, 0, 8)

        scroll.setWidget(self.orders_container)
        layout.addWidget(scroll)

        self.setStyleSheet("QWidget { background-color: #0C0C0E; color: white; border: none; }")

    def load_orders(self):
        # Clear existing cards
        for i in reversed(range(self.orders_grid.count())):
            widget = self.orders_grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        orders = execute_query(
            "SELECT o.order_id, o.order_type, o.status, o.order_time, "
            "t.table_number "
            "FROM orders o "
            "LEFT JOIN restaurant_tables t ON o.table_id = t.table_id "
            "WHERE o.status IN ('Pending', 'In-Kitchen') "
            "ORDER BY o.order_time",
            fetch=True
        )

        if not orders:
            empty = QLabel("✓  No pending orders right now")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("color: #44444F; font-size: 18px; border: none; background: transparent;")
            self.orders_grid.addWidget(empty, 0, 0)
            return

        for idx, order in enumerate(orders):
            items = execute_query(
                "SELECT m.item_name, od.quantity FROM order_details od "
                "JOIN menu_items m ON od.item_id = m.item_id "
                "WHERE od.order_id = ?",
                (order["order_id"],), fetch=True
            )
            card = self.create_order_card(order, items)
            row, col = divmod(idx, 3)
            self.orders_grid.addWidget(card, row, col)

    def create_order_card(self, order, items):
        is_pending = order["status"] == "Pending"
        color = "#E63946" if is_pending else "#F5A623"

        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: #18181D;
                border: 2px solid {color};
                border-radius: 8px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        # Order header
        hdr = QLabel(f"Order #{order['order_id']}  ·  {order['order_type']}")
        hdr.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        hdr.setStyleSheet(f"color: {color}; border: none; background: transparent;")
        layout.addWidget(hdr)

        # Table / time row
        table_info = f"Table {order['table_number']}" if order["table_number"] else "Takeaway"
        meta = QLabel(f"📍 {table_info}   ⏰ {str(order['order_time'])[11:16]}")
        meta.setStyleSheet("color: #74748A; font-size: 12px; border: none; background: transparent;")
        layout.addWidget(meta)

        # Divider
        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet(f"background: {color}; opacity: 0.3; border: none;")
        layout.addWidget(div)

        # Items list
        for item in items:
            item_lbl = QLabel(f"  ·  {item['item_name']}  ×{item['quantity']}")
            item_lbl.setStyleSheet("color: #C8C8D4; font-size: 13px; border: none; background: transparent;")
            layout.addWidget(item_lbl)

        layout.addSpacing(4)

        # Status badge
        status_lbl = QLabel(order["status"].upper())
        status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_lbl.setFixedHeight(24)
        status_lbl.setStyleSheet(f"""
            QLabel {{
                color: {color};
                background: rgba(230,57,70,0.1) ;
                border-radius: 3px;
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 1.5px;
                border: none;
            }}
        """)
        layout.addWidget(status_lbl)

        layout.addSpacing(4)

        # Action button
        if is_pending:
            btn = QPushButton("🍳  Start Cooking")
            btn.setStyleSheet("""
                QPushButton {
                    background: #F5A623; color: #000;
                    border: none; border-radius: 5px;
                    padding: 8px; font-size: 13px; font-weight: 700;
                }
                QPushButton:hover { background: #D4901E; }
            """)
            btn.clicked.connect(lambda _, oid=order["order_id"]: self.update_status(oid, "In-Kitchen"))
        else:
            btn = QPushButton("✅  Mark Ready")
            btn.setStyleSheet("""
                QPushButton {
                    background: #00C896; color: #000;
                    border: none; border-radius: 5px;
                    padding: 8px; font-size: 13px; font-weight: 700;
                }
                QPushButton:hover { background: #00A87E; }
            """)
            btn.clicked.connect(lambda _, oid=order["order_id"]: self.update_status(oid, "Ready"))

        layout.addWidget(btn)
        return card

    def update_status(self, order_id, status):
        execute_query("UPDATE orders SET status = ? WHERE order_id = ?", (status, order_id))
        self.load_orders()

    def logout(self):
        self.timer.stop()
        from modules.login import LoginWindow
        self.login = LoginWindow()
        self.login.show()
        self.close()