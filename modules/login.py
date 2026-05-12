# modules/login.py  —  Obsidian & Ember Login Screen
from PyQt6.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton,
                              QVBoxLayout, QHBoxLayout, QFrame,
                              QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QColor
from theme import QSS, C, R_MD, R_LG
from database.connection import authenticate_user


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Restaurant MS")
        self.setFixedSize(440, 560)
        self._shake_ref = None
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(QSS + f"""
            QWidget {{ background: {C['bg']}; }}
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ── Card ──────────────────────────────────────────────────────
        self.card = QFrame()
        self.card.setFixedSize(380, 500)
        self.card.setStyleSheet(f"""
            QFrame {{
                background: {C['surface_1']};
                border: 1px solid {C['border']};
                border-radius: {R_LG};
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(60); shadow.setOffset(0, 20)
        shadow.setColor(QColor(0, 0, 0, 160))
        self.card.setGraphicsEffect(shadow)

        cl = QVBoxLayout(self.card)
        cl.setContentsMargins(44, 44, 44, 44)
        cl.setSpacing(0)

        # Brand row
        brand_row = QHBoxLayout()
        dot = QLabel("●")
        dot.setStyleSheet(f"color:{C['accent']}; font-size:10px; background:transparent; border:none;")
        name = QLabel("RESTAURANT MS")
        name.setStyleSheet(f"color:{C['text_0']}; font-size:12px; font-weight:700; letter-spacing:3px; background:transparent; border:none;")
        brand_row.addWidget(dot); brand_row.addSpacing(6); brand_row.addWidget(name); brand_row.addStretch()
        cl.addLayout(brand_row)
        cl.addSpacing(36)

        # Title
        title = QLabel("Sign in")
        title.setStyleSheet(f"color:{C['text_0']}; font-size:26px; font-weight:700; letter-spacing:-0.5px; background:transparent; border:none;")
        cl.addWidget(title)
        sub = QLabel("Enter your credentials to continue")
        sub.setStyleSheet(f"color:{C['text_2']}; font-size:13px; background:transparent; margin-top:4px; border:none;")
        cl.addWidget(sub)
        cl.addSpacing(32)

        # Username
        cl.addWidget(self._field_label("USERNAME"))
        cl.addSpacing(6)
        self.username_input = self._input("your_username")
        cl.addWidget(self.username_input)
        cl.addSpacing(16)

        # Password
        cl.addWidget(self._field_label("PASSWORD"))
        cl.addSpacing(6)
        self.password_input = self._input("••••••••", password=True)
        self.password_input.returnPressed.connect(self.login)
        cl.addWidget(self.password_input)
        cl.addSpacing(10)

        # Error label
        self.error_lbl = QLabel("")
        self.error_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_lbl.setFixedHeight(32)
        self.error_lbl.setStyleSheet(f"""
            QLabel {{
                color: {C['accent']}; background: {C['red_bg']};
                border: 1px solid rgba(230,57,70,0.25);
                border-radius: {R_MD}; font-size:12px; font-weight:500; padding:0 12px;
            }}
        """)
        self.error_lbl.setVisible(False)
        cl.addWidget(self.error_lbl)
        cl.addSpacing(20)

        # Sign-in button
        self.login_btn = QPushButton("SIGN IN  →")
        self.login_btn.setFixedHeight(48)
        self.login_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C['accent']}; color: white; border: none;
                border-radius: {R_MD}; font-size:13px; font-weight:700; letter-spacing:1.5px;
            }}
            QPushButton:hover {{ background: {C['accent_dim']}; }}
            QPushButton:pressed {{ background: #8C1E26; }}
            QPushButton:disabled {{ background: {C['surface_3']}; color: {C['text_3']}; }}
        """)
        self.login_btn.clicked.connect(self.login)
        cl.addWidget(self.login_btn)
        cl.addStretch()

        # Footer
        footer = QLabel("Restaurant Management System  ·  v1.0")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet(f"color:{C['text_3']}; font-size:11px; background:transparent; letter-spacing:0.3px; border:none;")
        cl.addWidget(footer)

        outer.addWidget(self.card, alignment=Qt.AlignmentFlag.AlignCenter)

    def _field_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color:{C['text_3']}; font-size:10px; font-weight:700; letter-spacing:1.5px; background:transparent; border:none;")
        return lbl

    def _input(self, placeholder, password=False):
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        if password:
            inp.setEchoMode(QLineEdit.EchoMode.Password)
        inp.setStyleSheet(f"""
            QLineEdit {{
                background:{C['surface_2']}; border:1px solid {C['border']};
                border-radius:{R_MD}; color:{C['text_0']};
                padding:0 14px; min-height:44px; font-size:14px;
            }}
            QLineEdit:focus {{ border-color:{C['accent']}; background:{C['surface_0']}; }}
        """)
        return inp

    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        self.error_lbl.setVisible(False)

        if not username or not password:
            self._show_error("Username and password are required.")
            return

        self.login_btn.setText("AUTHENTICATING...")
        self.login_btn.setEnabled(False)
        user = authenticate_user(username, password)

        if user:
            self.login_btn.setText("✓  ACCESS GRANTED")
            QTimer.singleShot(350, lambda: self.open_dashboard(user))
        else:
            self._show_error("Invalid credentials. Please try again.")
            self.login_btn.setText("SIGN IN  →")
            self.login_btn.setEnabled(True)
            self._do_shake()

    def _show_error(self, msg):
        self.error_lbl.setText(msg)
        self.error_lbl.setVisible(True)

    def _do_shake(self):
        anim = QPropertyAnimation(self.card, b"pos")
        anim.setDuration(300)
        pos = self.card.pos()
        anim.setKeyValueAt(0.0,  pos)
        anim.setKeyValueAt(0.15, pos + QPoint(-8, 0))
        anim.setKeyValueAt(0.30, pos + QPoint(8, 0))
        anim.setKeyValueAt(0.45, pos + QPoint(-5, 0))
        anim.setKeyValueAt(0.60, pos + QPoint(5, 0))
        anim.setKeyValueAt(0.80, pos + QPoint(-3, 0))
        anim.setKeyValueAt(1.0,  pos)
        anim.start()
        self._shake_ref = anim  # prevent GC

    def open_dashboard(self, user):
        role = user["role"]
        if role in ("Admin", "Manager"):
            from modules.admin_dashboard import AdminDashboard
            self.dashboard = AdminDashboard(user)
        elif role == "Chef":
            from modules.kitchen import KitchenDisplay
            self.dashboard = KitchenDisplay(user)
        elif role == "Waiter":
            from modules.orders import OrderWindow
            self.dashboard = OrderWindow(user)
        elif role == "Customer":
            from modules.customer import CustomerPanel
            self.dashboard = CustomerPanel(user)
        elif role == "Supplier":
            from modules.supplier import SupplierPanel
            self.dashboard = SupplierPanel(user)
        else:
            from modules.admin_dashboard import AdminDashboard
            self.dashboard = AdminDashboard(user)
        self.dashboard.show()
        self.close()