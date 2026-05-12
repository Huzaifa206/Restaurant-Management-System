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
        self.timer.start(15000)  # Refresh every 15 seconds

    def setup_ui(self):
        layout = QVBoxLayout(self)

        header = QHBoxLayout()
        title = QLabel("👨‍🍳 Kitchen Display System")
        title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        header.addWidget(title)
        header.addStretch()
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_orders)
        refresh_btn.setStyleSheet("background:#f39c12; color:white; padding:8px 15px; border-radius:6px;")
        header.addWidget(refresh_btn)
        layout.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.orders_container = QWidget()
        self.orders_grid = QGridLayout(self.orders_container)
        scroll.setWidget(self.orders_container)
        layout.addWidget(scroll)

        self.setStyleSheet("background-color: #1a1a2e; color: white;")

    def load_orders(self):
        # Clear existing cards
        for i in reversed(range(self.orders_grid.count())):
            self.orders_grid.itemAt(i).widget().setParent(None)

        orders = execute_query(
            "SELECT o.order_id, o.order_type, o.status, o.order_time, "
            "t.table_number "
            "FROM orders o "
            "LEFT JOIN restaurant_tables t ON o.table_id = t.table_id "
            "WHERE o.status IN ('Pending', 'In-Kitchen') "
            "ORDER BY o.order_time",
            fetch=True
        )

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
        card = QFrame()
        color = "#e74c3c" if order["status"] == "Pending" else "#f39c12"
        card.setStyleSheet(f"""
            QFrame {{
                background: #16213e;
                border: 3px solid {color};
                border-radius: 12px;
                padding: 10px;
            }}
        """)
        layout = QVBoxLayout(card)

        header = QLabel(f"Order #{order['order_id']} | {order['order_type']}")
        header.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {color};")
        layout.addWidget(header)

        table_info = f"Table {order['table_number']}" if order["table_number"] else "Takeaway"
        layout.addWidget(QLabel(f"📍 {table_info}"))
        layout.addWidget(QLabel(f"⏰ {str(order['order_time'])[11:16]}"))

        layout.addWidget(QLabel("─" * 25))
        for item in items:
            layout.addWidget(QLabel(f"  • {item['item_name']} x{item['quantity']}"))

        status_label = QLabel(f"Status: {order['status']}")
        status_label.setStyleSheet(f"color:{color}; font-weight:bold; margin-top:8px;")
        layout.addWidget(status_label)

        # Mark as In-Kitchen / Ready button
        if order["status"] == "Pending":
            btn = QPushButton("🍳 Start Cooking")
            btn.setStyleSheet("background:#e67e22; color:white; border-radius:5px; padding:6px;")
            btn.clicked.connect(lambda _, oid=order["order_id"]: self.update_status(oid, "In-Kitchen"))
        else:
            btn = QPushButton("✅ Mark Ready")
            btn.setStyleSheet("background:#27ae60; color:white; border-radius:5px; padding:6px;")
            btn.clicked.connect(lambda _, oid=order["order_id"]: self.update_status(oid, "Ready"))

        layout.addWidget(btn)
        return card

    def update_status(self, order_id, status):
        execute_query("UPDATE orders SET status = ? WHERE order_id = ?", (status, order_id))
        self.load_orders()