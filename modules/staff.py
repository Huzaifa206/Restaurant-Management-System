from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QTableWidget, QTableWidgetItem, QDialog,
                              QFormLayout, QLineEdit, QComboBox, QDoubleSpinBox, QMessageBox)
from PyQt6.QtGui import QFont
from database.connection import execute_query


class StaffWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.branch_id = user.get("branch_id", 1)
        self.setup_ui()
        self.load_staff()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QHBoxLayout()
        header.addWidget(QLabel("👥 Staff Management", font=QFont("Arial", 16, QFont.Weight.Bold)))
        header.addStretch()

        add_btn = QPushButton("+ Add Staff")
        add_btn.setStyleSheet("background:#2ecc71; color:white; padding:8px 15px; border-radius:6px;")
        add_btn.clicked.connect(self.add_staff_dialog)
        header.addWidget(add_btn)
        layout.addLayout(header)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Role", "Username", "Phone", "Salary", "Active"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        btn_row = QHBoxLayout()
        deactivate_btn = QPushButton("❌ Deactivate")
        deactivate_btn.clicked.connect(self.deactivate_staff)
        btn_row.addWidget(deactivate_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

    def load_staff(self):
        staff_list = execute_query(
            "SELECT staff_id, full_name, role, username, phone, salary, is_active "
            "FROM staff WHERE branch_id = ? ORDER BY role, full_name",
            (self.branch_id,), fetch=True
        )
        self.table.setRowCount(len(staff_list))
        for row, s in enumerate(staff_list):
            values = [str(s["staff_id"]), s["full_name"], s["role"],
                      s["username"], s["phone"] or "", f"Rs.{s['salary']:,.0f}",
                      "Yes" if s["is_active"] else "No"]
            for col, val in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(val))

    def add_staff_dialog(self):
        dialog = StaffDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                execute_query(
                    "INSERT INTO staff (branch_id, full_name, role, username, password_hash, phone, salary) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (self.branch_id, data["name"], data["role"], data["username"],
                     data["password"], data["phone"], data["salary"])
                )
                QMessageBox.information(self, "✅ Added", f"Staff '{data['name']}' added successfully!")
                self.load_staff()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add staff:\n{str(e)}")

    def deactivate_staff(self):
        row = self.table.currentRow()
        if row < 0:
            return
        staff_id = int(self.table.item(row, 0).text())
        name = self.table.item(row, 1).text()
        reply = QMessageBox.question(self, "Confirm", f"Deactivate {name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            execute_query("UPDATE staff SET is_active = 0 WHERE staff_id = ?", (staff_id,))
            self.load_staff()


class StaffDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Add New Staff Member")
        self.setFixedSize(380, 320)
        layout = QFormLayout(self)

        self.name = QLineEdit()
        self.role = QComboBox()
        self.role.addItems(["Manager", "Chef", "Waiter", "Cashier", "Cleaner"])
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.phone = QLineEdit()
        self.salary = QDoubleSpinBox()
        self.salary.setMaximum(999999)
        self.salary.setValue(25000)

        layout.addRow("Full Name:", self.name)
        layout.addRow("Role:", self.role)
        layout.addRow("Username:", self.username)
        layout.addRow("Password:", self.password)
        layout.addRow("Phone:", self.phone)
        layout.addRow("Salary (Rs.):", self.salary)

        save_btn = QPushButton("Add Staff Member")
        save_btn.setStyleSheet("background:#2ecc71; color:white; padding:8px; border-radius:6px;")
        save_btn.clicked.connect(self.accept)
        layout.addRow(save_btn)

    def get_data(self):
        return {
            "name": self.name.text(),
            "role": self.role.currentText(),
            "username": self.username.text(),
            "password": self.password.text(),
            "phone": self.phone.text(),
            "salary": self.salary.value()
        }