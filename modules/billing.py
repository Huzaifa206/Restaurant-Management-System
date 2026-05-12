from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QTableWidget, QTableWidgetItem, QMessageBox,
                              QComboBox, QDoubleSpinBox)
from PyQt6.QtGui import QFont
from database.connection import execute_query

TAX_RATE = 0.17  # 17% GST Pakistan


class BillingWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setup_ui()
        self.load_served_orders()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("🧾 Billing & Payments")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        layout.addWidget(QLabel("Select a served order to generate invoice:"))

        self.orders_table = QTableWidget(0, 4)
        self.orders_table.setHorizontalHeaderLabels(["Order ID", "Type", "Total", "Time"])
        self.orders_table.horizontalHeader().setStretchLastSection(True)
        self.orders_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.orders_table.clicked.connect(self.load_order_details)
        layout.addWidget(self.orders_table)

        # Order detail
        layout.addWidget(QLabel("Order Details:"))
        self.detail_table = QTableWidget(0, 4)
        self.detail_table.setHorizontalHeaderLabels(["Item", "Qty", "Unit Price", "Subtotal"])
        self.detail_table.setFixedHeight(180)
        layout.addWidget(self.detail_table)

        # Bill summary
        summary_layout = QHBoxLayout()
        self.subtotal_label = QLabel("Subtotal: Rs. 0")
        self.tax_label = QLabel("Tax (17%): Rs. 0")
        self.total_label = QLabel("TOTAL: Rs. 0")
        self.total_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.total_label.setStyleSheet("color: #c0392b;")
        summary_layout.addWidget(self.subtotal_label)
        summary_layout.addWidget(self.tax_label)
        summary_layout.addStretch()
        summary_layout.addWidget(self.total_label)
        layout.addLayout(summary_layout)

        # Payment method
        pay_row = QHBoxLayout()
        pay_row.addWidget(QLabel("Payment Method:"))
        self.payment_method = QComboBox()
        self.payment_method.addItems(["Cash", "Card", "JazzCash", "EasyPaisa"])
        pay_row.addWidget(self.payment_method)
        pay_row.addStretch()
        layout.addLayout(pay_row)

        # Generate Invoice button
        gen_btn = QPushButton("💳 Process Payment & Generate Invoice")
        gen_btn.setFixedHeight(45)
        gen_btn.setStyleSheet(
            "background:#c0392b; color:white; font-size:14px; "
            "border-radius:8px; font-weight:bold;")
        gen_btn.clicked.connect(self.process_payment)
        layout.addWidget(gen_btn)

        self.current_order_id = None
        self.current_subtotal = 0

    def load_served_orders(self):
        orders = execute_query(
            "SELECT order_id, order_type, total_amount, order_time FROM orders "
            "WHERE status = 'Served' AND order_id NOT IN (SELECT order_id FROM payments)",
            fetch=True
        )
        self.orders_table.setRowCount(len(orders))
        for row, o in enumerate(orders):
            self.orders_table.setItem(row, 0, QTableWidgetItem(str(o["order_id"])))
            self.orders_table.setItem(row, 1, QTableWidgetItem(o["order_type"]))
            self.orders_table.setItem(row, 2, QTableWidgetItem(f"Rs.{o['total_amount']:.0f}"))
            self.orders_table.setItem(row, 3, QTableWidgetItem(str(o["order_time"])))

    def load_order_details(self):
        row = self.orders_table.currentRow()
        if row < 0:
            return
        self.current_order_id = int(self.orders_table.item(row, 0).text())

        details = execute_query(
            "SELECT m.item_name, od.quantity, od.unit_price, od.subtotal "
            "FROM order_details od JOIN menu_items m ON od.item_id = m.item_id "
            "WHERE od.order_id = ?",
            (self.current_order_id,), fetch=True
        )
        self.detail_table.setRowCount(len(details))
        subtotal = 0
        for row_idx, d in enumerate(details):
            self.detail_table.setItem(row_idx, 0, QTableWidgetItem(d["item_name"]))
            self.detail_table.setItem(row_idx, 1, QTableWidgetItem(str(d["quantity"])))
            self.detail_table.setItem(row_idx, 2, QTableWidgetItem(f"Rs.{d['unit_price']:.0f}"))
            self.detail_table.setItem(row_idx, 3, QTableWidgetItem(f"Rs.{d['subtotal']:.0f}"))
            subtotal += float(d["subtotal"])

        tax = subtotal * TAX_RATE
        total = subtotal + tax
        self.current_subtotal = subtotal

        self.subtotal_label.setText(f"Subtotal: Rs. {subtotal:,.0f}")
        self.tax_label.setText(f"Tax (17%): Rs. {tax:,.0f}")
        self.total_label.setText(f"TOTAL: Rs. {total:,.0f}")

    def process_payment(self):
        if not self.current_order_id:
            QMessageBox.warning(self, "No Order", "Please select an order first.")
            return

        subtotal = self.current_subtotal
        tax = subtotal * TAX_RATE
        total = subtotal + tax
        method = self.payment_method.currentText()

        try:
            execute_query(
                "INSERT INTO payments (order_id, amount_paid, payment_method) VALUES (?, ?, ?)",
                (self.current_order_id, total, method)
            )
            payment_id = execute_query(
                "SELECT TOP 1 payment_id FROM payments ORDER BY payment_id DESC",
                fetch=True)[0]["payment_id"]

            execute_query(
                "INSERT INTO invoices (order_id, payment_id, subtotal, tax_rate, tax_amount, total_amount) "
                "VALUES (?, ?, ?, 17, ?, ?)",
                (self.current_order_id, payment_id, subtotal, tax, total)
            )
            execute_query(
                "UPDATE orders SET status = 'Completed' WHERE order_id = ?",
                (self.current_order_id,)
            )
            QMessageBox.information(self, "✅ Payment Done",
                f"Payment of Rs. {total:,.0f} received via {method}.\n"
                f"Invoice generated successfully!")
            self.current_order_id = None
            self.load_served_orders()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))