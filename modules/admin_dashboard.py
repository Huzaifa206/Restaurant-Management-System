from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                              QPushButton, QLabel, QFrame, QStackedWidget,
                              QTableWidgetItem, QScrollArea)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from theme import (QSS, C, R_MD, R_LG, FONT_MONO,
                   stat_card, page_header, section_label, heading, subheading,
                   divider, styled_table, card_frame, ghost_btn, accent_btn,
                   status_badge)
from database.connection import execute_query


class AdminDashboard(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("Restaurant MS")
        self.showMaximized()
        self.setStyleSheet(QSS)
        self._active_btn = None
        self._nav_btns = []
        self.setup_ui()

    def setup_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        main_layout = QHBoxLayout(root)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(self._build_sidebar())
        main_layout.addWidget(self._build_content())

        # Default page
        self._activate(self._nav_btns[0], self.show_overview)

    # ── Sidebar ───────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        sb = QFrame()
        sb.setFixedWidth(220)
        sb.setStyleSheet(f"""
            QFrame {{
                background: {C['surface_0']};
                border: none;
                border-right: 1px solid {C['border']};
            }}
        """)

        sb_layout = QVBoxLayout(sb)
        sb_layout.setContentsMargins(0, 0, 0, 20)
        sb_layout.setSpacing(0)

        # ── Logo strip ────────────────────────────────────────────────
        logo_frame = QFrame()
        logo_frame.setFixedHeight(64)
        logo_frame.setStyleSheet(f"""
            QFrame {{
                background: {C['surface_0']};
                border: none;
                border-bottom: 1px solid {C['border']};
            }}
        """)
        lf = QHBoxLayout(logo_frame)
        lf.setContentsMargins(20, 0, 16, 0)

        dot_big = QLabel("■")
        dot_big.setStyleSheet(f"color: {C['accent']}; font-size: 16px; border: none; background: transparent;")

        t1 = QLabel("RESTAURANT")
        t1.setStyleSheet(f"color:{C['text_0']}; font-size:11px; font-weight:700; letter-spacing:2px; border:none; background:transparent;")
        t2 = QLabel("MANAGEMENT SYSTEM")
        t2.setStyleSheet(f"color:{C['text_3']}; font-size:8px; font-weight:600; letter-spacing:1.5px; border:none; background:transparent;")

        logo_text = QVBoxLayout()
        logo_text.setSpacing(1)
        logo_text.addWidget(t1)
        logo_text.addWidget(t2)

        lf.addWidget(dot_big)
        lf.addSpacing(10)
        lf.addLayout(logo_text)
        lf.addStretch()
        sb_layout.addWidget(logo_frame)

        # ── User chip ─────────────────────────────────────────────────
        user_frame = QFrame()
        user_frame.setFixedHeight(64)
        user_frame.setStyleSheet(f"""
            QFrame {{
                background: transparent;
                border: none;
                border-bottom: 1px solid {C['border']};
            }}
        """)
        uf = QHBoxLayout(user_frame)
        uf.setContentsMargins(16, 0, 16, 0)

        avatar = QLabel(self.user["full_name"][0].upper())
        avatar.setFixedSize(36, 36)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(f"""
            QLabel {{
                background: {C['accent']};
                color: white;
                border-radius: 18px;
                font-size: 14px;
                font-weight: 800;
                border: none;
            }}
        """)

        uname = QLabel(self.user["full_name"])
        uname.setStyleSheet(f"color:{C['text_0']}; font-size:12px; font-weight:600; background:transparent; border:none;")
        urole = QLabel(self.user["role"].upper())
        urole.setStyleSheet(f"color:{C['text_3']}; font-size:9px; font-weight:700; letter-spacing:1px; background:transparent; border:none;")

        user_info = QVBoxLayout()
        user_info.setSpacing(1)
        user_info.addWidget(uname)
        user_info.addWidget(urole)

        uf.addWidget(avatar)
        uf.addSpacing(10)
        uf.addLayout(user_info)
        uf.addStretch()
        sb_layout.addWidget(user_frame)

        sb_layout.addSpacing(12)

        # ── Nav section label ─────────────────────────────────────────
        nav_lbl = section_label("  MENU")
        nav_lbl.setContentsMargins(20, 0, 0, 6)
        sb_layout.addWidget(nav_lbl)

        # ── Nav buttons ───────────────────────────────────────────────
        nav_items = [
            ("▣", "Overview",  self.show_overview),
            ("◈", "Orders",    self.show_orders),
            ("◉", "Menu",      self.show_menu),
            ("◎", "Inventory", self.show_inventory),
            ("◇", "Billing",   self.show_billing),
            ("◈", "Staff",     self.show_staff),
            ("◻", "Tables",    self.show_tables),
            ("◆", "Reports",   self.show_reports),
        ]

        for icon, label, cb in nav_items:
            btn = QPushButton(f"  {icon}   {label}")
            btn.setObjectName("navBtn")
            btn.setFixedHeight(44)
            btn.clicked.connect(lambda _, b=btn, c=cb: self._activate(b, c))
            self._set_nav_inactive(btn)
            sb_layout.addWidget(btn)
            self._nav_btns.append(btn)

        sb_layout.addStretch()
        sb_layout.addWidget(divider())
        sb_layout.addSpacing(12)

        # ── Logout ────────────────────────────────────────────────────
        logout = QPushButton("  ◁   Logout")
        logout.setFixedHeight(44)
        logout.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {C['text_2']};
                border: none;
                text-align: left;
                padding-left: 18px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: {C['red_bg']};
                color: {C['accent']};
            }}
        """)
        logout.clicked.connect(self.logout)
        sb_layout.addWidget(logout)

        return sb

    # ── Content stack ─────────────────────────────────────────────────────────
    def _build_content(self):
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background: {C['bg']}; border: none;")
        return self.stack

    def _set_nav_inactive(self, btn):
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {C['text_2']};
                border: none;
                text-align: left;
                padding-left: 18px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: {C['surface_1']};
                color: {C['text_0']};
            }}
        """)

    def _set_nav_active(self, btn):
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {C['accent_glow']};
                color: {C['accent']};
                border: none;
                border-left: 2px solid {C['accent']};
                text-align: left;
                padding-left: 16px;
                font-size: 13px;
                font-weight: 700;
            }}
        """)

    def _activate(self, btn, callback):
        for b in self._nav_btns:
            self._set_nav_inactive(b)
        self._set_nav_active(btn)
        self._active_btn = btn
        callback()

    def _set_page(self, widget):
        while self.stack.count():
            w = self.stack.widget(0)
            self.stack.removeWidget(w)
            w.deleteLater()
        self.stack.addWidget(widget)
        self.stack.setCurrentWidget(widget)

    # ── Page routing ──────────────────────────────────────────────────────────
    def show_overview(self):
        self._set_page(OverviewPage(self.user))

    def show_orders(self):
        from modules.orders import OrderWindow
        self._set_page(OrderWindow(self.user, embedded=True))

    def show_menu(self):
        from modules.menu import MenuWindow
        self._set_page(MenuWindow(self.user))

    def show_inventory(self):
        from modules.inventory import InventoryWindow
        self._set_page(InventoryWindow(self.user))

    def show_billing(self):
        from modules.billing import BillingWindow
        self._set_page(BillingWindow(self.user))

    def show_staff(self):
        from modules.staff import StaffWindow
        self._set_page(StaffWindow(self.user))

    def show_tables(self):
        from modules.tables import TableWindow
        self._set_page(TableWindow(self.user))

    def show_reports(self):
        self._set_page(_PlaceholderPage("Reports & Analytics", "Advanced analytics coming soon."))

    def logout(self):
        from modules.login import LoginWindow
        self.w = LoginWindow()
        self.w.show()
        self.close()


# ─────────────────────────────────────────────────────────────────────────────
#  Overview / Dashboard Page
# ─────────────────────────────────────────────────────────────────────────────
class OverviewPage(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setStyleSheet(f"QWidget {{ background: {C['bg']}; border: none; }}")
        self._build()

    def _build(self):
        # Scrollable outer container
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        inner = QWidget()
        inner.setStyleSheet(f"QWidget {{ background: {C['bg']}; border: none; }}")

        layout = QVBoxLayout(inner)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(0)

        # ── Header ────────────────────────────────────────────────────
        h_row = QHBoxLayout()

        title_lbl = QLabel(f"Good day, {self.user['full_name'].split()[0]}")
        title_lbl.setStyleSheet(f"color:{C['text_0']}; font-size:20px; font-weight:700; letter-spacing:-0.3px; background:transparent; border:none;")

        sub_lbl = QLabel("Here's your restaurant at a glance.")
        sub_lbl.setStyleSheet(f"color:{C['text_2']}; font-size:13px; background:transparent; border:none;")

        title_block = QVBoxLayout()
        title_block.setSpacing(3)
        title_block.addWidget(title_lbl)
        title_block.addWidget(sub_lbl)

        self.time_lbl = QLabel()
        self.time_lbl.setStyleSheet(f"color:{C['text_3']}; font-size:12px; font-family:'{FONT_MONO}'; background:transparent; border:none;")
        self._update_time()

        timer = QTimer(self)
        timer.timeout.connect(self._update_time)
        timer.start(1000)

        h_row.addLayout(title_block)
        h_row.addStretch()
        h_row.addWidget(self.time_lbl)
        layout.addLayout(h_row)
        layout.addSpacing(28)

        # ── KPI Cards ─────────────────────────────────────────────────
        stats = self._get_stats()

        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(12)
        kpi_row.addWidget(stat_card("▣", str(stats["orders"]),          "Today's Orders",  "orders placed today",    C["accent"]))
        kpi_row.addWidget(stat_card("◈", f"{stats['revenue']:,.0f}",    "Revenue (Rs.)",   "collected today",         C["green"]))
        kpi_row.addWidget(stat_card("⚠", str(stats["low_stock"]),       "Low Stock",       "items below reorder lvl", C["yellow"]))
        kpi_row.addWidget(stat_card("◉", str(stats["staff"]),           "Active Staff",    "currently employed",      C["blue"]))
        layout.addLayout(kpi_row)
        layout.addSpacing(32)

        # ── Section label ─────────────────────────────────────────────
        activity_lbl = QLabel("RECENT ACTIVITY")
        activity_lbl.setStyleSheet(f"color:{C['text_3']}; font-size:10px; font-weight:700; letter-spacing:2px; background:transparent; border:none;")
        layout.addWidget(activity_lbl)
        layout.addSpacing(12)

        # ── Two-column section ────────────────────────────────────────
        cols = QHBoxLayout()
        cols.setSpacing(16)

        # Recent orders card
        orders_card = self._build_orders_card()
        cols.addWidget(orders_card, 6)

        # Low stock card
        stock_card = self._build_stock_card()
        cols.addWidget(stock_card, 4)

        layout.addLayout(cols)
        layout.addStretch()

        scroll.setWidget(inner)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _build_orders_card(self):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {C['surface_1']};
                border: 1px solid {C['border']};
                border-radius: {R_LG};
            }}
        """)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 20, 20, 20)
        cl.setSpacing(12)

        # Card header
        hdr = QHBoxLayout()
        title = QLabel("Recent Orders")
        title.setStyleSheet(f"color:{C['text_0']}; font-size:15px; font-weight:600; background:transparent; border:none;")
        view_all = ghost_btn("View All")
        view_all.setFixedHeight(30)
        hdr.addWidget(title)
        hdr.addStretch()
        hdr.addWidget(view_all)
        cl.addLayout(hdr)
        cl.addWidget(divider())

        try:
            recents = execute_query(
                "SELECT TOP 6 order_id, order_type, status, "
                "ISNULL(total_amount, 0) as total, order_time "
                "FROM orders ORDER BY order_id DESC",
                fetch=True
            )
            for o in recents:
                cl.addWidget(self._order_row(o))
        except Exception as e:
            err = QLabel(f"Could not load: {e}")
            err.setStyleSheet(f"color:{C['text_2']}; border:none; background:transparent;")
            cl.addWidget(err)

        cl.addStretch()
        return card

    def _build_stock_card(self):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {C['surface_1']};
                border: 1px solid {C['border']};
                border-radius: {R_LG};
            }}
        """)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 20, 20, 20)
        cl.setSpacing(12)

        title = QLabel("Stock Alerts")
        title.setStyleSheet(f"color:{C['text_0']}; font-size:15px; font-weight:600; background:transparent; border:none;")
        cl.addWidget(title)
        cl.addWidget(divider())

        try:
            low = execute_query(
                "SELECT TOP 6 item_name, quantity_in_stock, reorder_level, unit "
                "FROM inventory WHERE quantity_in_stock <= reorder_level "
                "ORDER BY quantity_in_stock ASC",
                fetch=True
            )
            if not low:
                ok = QLabel("✓  All stock levels healthy")
                ok.setStyleSheet(f"color:{C['green']}; font-size:13px; border:none; background:transparent;")
                cl.addWidget(ok)
            for item in low:
                cl.addWidget(self._stock_row(item))
        except Exception as e:
            err = QLabel(f"Could not load: {e}")
            err.setStyleSheet(f"color:{C['text_2']}; border:none; background:transparent;")
            cl.addWidget(err)

        cl.addStretch()
        return card

    def _order_row(self, o):
        row = QFrame()
        row.setStyleSheet(f"""
            QFrame {{
                background: transparent;
                border: none;
                border-bottom: 1px solid {C['border']};
            }}
        """)
        rl = QHBoxLayout(row)
        rl.setContentsMargins(0, 10, 0, 10)

        id_lbl = QLabel(f"#{o['order_id']}")
        id_lbl.setFixedWidth(50)
        id_lbl.setStyleSheet(f"color:{C['text_0']}; font-family:'{FONT_MONO}'; font-weight:700; font-size:13px; border:none; background:transparent;")

        type_lbl = QLabel(o["order_type"])
        type_lbl.setStyleSheet(f"color:{C['text_2']}; font-size:12px; border:none; background:transparent;")

        amt = QLabel(f"Rs. {o['total']:,.0f}")
        amt.setStyleSheet(f"color:{C['text_0']}; font-family:'{FONT_MONO}'; font-size:13px; font-weight:600; border:none; background:transparent;")

        badge = status_badge(o["status"])

        rl.addWidget(id_lbl)
        rl.addWidget(type_lbl)
        rl.addStretch()
        rl.addWidget(badge)
        rl.addSpacing(16)
        rl.addWidget(amt)
        return row

    def _stock_row(self, item):
        row = QFrame()
        row.setStyleSheet(f"""
            QFrame {{
                background: transparent;
                border: none;
                border-bottom: 1px solid {C['border']};
            }}
        """)
        rl = QHBoxLayout(row)
        rl.setContentsMargins(0, 10, 0, 10)

        name = QLabel(item["item_name"])
        name.setStyleSheet(f"color:{C['text_0']}; font-size:13px; font-weight:600; border:none; background:transparent;")

        qty = QLabel(f"{item['quantity_in_stock']} {item['unit'] or ''}")
        qty.setStyleSheet(f"color:{C['yellow']}; font-family:'{FONT_MONO}'; font-size:12px; font-weight:700; border:none; background:transparent;")

        rl.addWidget(name)
        rl.addStretch()
        rl.addWidget(qty)
        return row

    def _get_stats(self):
        try:
            orders = execute_query(
                "SELECT COUNT(*) as c FROM orders WHERE CAST(order_time AS DATE)=CAST(GETDATE() AS DATE)",
                fetch=True)[0]["c"]
            revenue = execute_query(
                "SELECT ISNULL(SUM(amount_paid),0) as r FROM payments WHERE CAST(payment_time AS DATE)=CAST(GETDATE() AS DATE)",
                fetch=True)[0]["r"]
            low_stock = execute_query(
                "SELECT COUNT(*) as c FROM inventory WHERE quantity_in_stock<=reorder_level",
                fetch=True)[0]["c"]
            staff = execute_query(
                "SELECT COUNT(*) as c FROM staff WHERE is_active=1",
                fetch=True)[0]["c"]
            return {"orders": orders, "revenue": revenue, "low_stock": low_stock, "staff": staff}
        except:
            return {"orders": 0, "revenue": 0, "low_stock": 0, "staff": 0}

    def _update_time(self):
        from datetime import datetime
        self.time_lbl.setText(datetime.now().strftime("%a, %d %b %Y  %H:%M:%S"))


# ─────────────────────────────────────────────────────────────────────────────
class _PlaceholderPage(QWidget):
    def __init__(self, title, subtitle):
        super().__init__()
        self.setStyleSheet(f"QWidget {{ background: {C['bg']}; border: none; }}")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        t = QLabel(title)
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t.setStyleSheet(f"color:{C['text_0']}; font-size:22px; font-weight:700; border:none; background:transparent;")

        s = QLabel(subtitle)
        s.setAlignment(Qt.AlignmentFlag.AlignCenter)
        s.setStyleSheet(f"color:{C['text_2']}; font-size:14px; border:none; background:transparent;")

        layout.addWidget(t)
        layout.addSpacing(8)
        layout.addWidget(s)