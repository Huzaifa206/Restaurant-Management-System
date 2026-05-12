C = {
    "bg":           "#0C0C0E",
    "surface_0":    "#111114",
    "surface_1":    "#18181D",
    "surface_2":    "#1F1F26",
    "surface_3":    "#26262F",

    "border":       "#2A2A35",
    "border_focus": "#E63946",

    "accent":       "#E63946",
    "accent_dim":   "#B52D38",
    "accent_glow":  "rgba(230,57,70,0.12)",

    "text_0":       "#FFFFFF",
    "text_1":       "#C8C8D4",
    "text_2":       "#74748A",
    "text_3":       "#44444F",

    "green":        "#00C896",
    "green_bg":     "rgba(0,200,150,0.10)",
    "yellow":       "#F5A623",
    "yellow_bg":    "rgba(245,166,35,0.10)",
    "red":          "#E63946",
    "red_bg":       "rgba(230,57,70,0.10)",
    "blue":         "#4A90D9",
    "blue_bg":      "rgba(74,144,217,0.10)",
}

FONT = "Segoe UI"
FONT_MONO = "Consolas"

R_SM = "3px"
R_MD = "5px"
R_LG = "8px"

QSS = f"""

/* ══════════════════════════════════════════════════════
   BASE  — NO * border rule (causes bleed on all widgets)
         Each widget type declares its own border.
══════════════════════════════════════════════════════ */
QWidget {{
    font-family: '{FONT}', 'Arial', sans-serif;
    font-size: 13px;
    color: {C['text_1']};
    background: {C['bg']};
    border: none;
    outline: none;
}}

QMainWindow {{ background: {C['bg']}; border: none; }}
QDialog     {{ background: {C['surface_1']}; border: none; }}

/* Labels — never have a border */
QLabel {{
    background: transparent;
    border: none;
    color: {C['text_1']};
}}

/* Frames — no border by default; specific variants override below */
QFrame {{
    border: none;
    background: transparent;
}}

/* Layout containers */
QStackedWidget, QScrollArea, QSplitter {{ border: none; background: transparent; }}
QGroupBox {{ border: none; background: transparent; }}
QMenuBar, QStatusBar, QToolBar {{ border: none; }}

/* ══════════════════════════════════════════════════════
   SCROLLBARS  — whisper thin, barely there
══════════════════════════════════════════════════════ */
QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {C['border']};
    border-radius: 3px;
    min-height: 40px;
}}
QScrollBar::handle:vertical:hover {{
    background: {C['text_3']};
}}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 6px;
}}
QScrollBar::handle:horizontal {{
    background: {C['border']};
    border-radius: 3px;
}}
QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {{
    width: 0;
}}
QAbstractScrollArea {{
    background: transparent;
}}

/* ══════════════════════════════════════════════════════
   LABELS
══════════════════════════════════════════════════════ */
QLabel {{
    background: transparent;
    color: {C['text_1']};
    border: none;
}}
QLabel[role="heading"] {{
    color: {C['text_0']};
    font-size: 20px;
    font-weight: 700;
    letter-spacing: -0.3px;
}}
QLabel[role="subheading"] {{
    color: {C['text_2']};
    font-size: 13px;
}}
QLabel[role="section"] {{
    color: {C['text_3']};
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2px;
}}
QLabel[role="mono"] {{
    font-family: '{FONT_MONO}';
    color: {C['text_0']};
}}

/* ══════════════════════════════════════════════════════
   INPUT FIELDS
══════════════════════════════════════════════════════ */
QLineEdit {{
    background: {C['surface_2']};
    border: 1px solid {C['border']};
    border-radius: {R_MD};
    color: {C['text_0']};
    padding: 0 14px;
    min-height: 42px;
    font-size: 13px;
    selection-background-color: {C['accent_dim']};
}}
QLineEdit:hover {{
    border-color: {C['text_3']};
    background: {C['surface_2']};
}}
QLineEdit:focus {{
    border-color: {C['accent']};
    background: {C['surface_1']};
}}
QLineEdit:disabled {{
    background: {C['surface_1']};
    color: {C['text_3']};
    border-color: {C['border']};
}}

QTextEdit {{
    background: {C['surface_2']};
    border: 1px solid {C['border']};
    border-radius: {R_MD};
    color: {C['text_0']};
    padding: 10px 14px;
    font-size: 13px;
    selection-background-color: {C['accent_dim']};
}}
QTextEdit:focus {{
    border-color: {C['accent']};
}}

/* ══════════════════════════════════════════════════════
   BUTTONS  — the accent button is THE button
══════════════════════════════════════════════════════ */
QPushButton {{
    background: {C['accent']};
    color: {C['text_0']};
    border: none;
    border-radius: {R_MD};
    padding: 0 20px;
    min-height: 38px;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.2px;
}}
QPushButton:hover {{
    background: {C['accent_dim']};
}}
QPushButton:pressed {{
    background: #8C1E26;
    padding-top: 1px;
}}
QPushButton:disabled {{
    background: {C['surface_3']};
    color: {C['text_3']};
}}

/* Ghost button variant */
QPushButton[variant="ghost"] {{
    background: transparent;
    color: {C['text_1']};
    border: 1px solid {C['border']};
}}
QPushButton[variant="ghost"]:hover {{
    background: {C['surface_2']};
    border-color: {C['text_3']};
    color: {C['text_0']};
}}
QPushButton[variant="ghost"]:pressed {{
    background: {C['surface_3']};
}}

/* Success variant */
QPushButton[variant="success"] {{
    background: {C['green']};
    color: #000;
}}
QPushButton[variant="success"]:hover {{
    background: #00A87E;
}}

/* Warning variant */
QPushButton[variant="warning"] {{
    background: {C['yellow']};
    color: #000;
}}
QPushButton[variant="warning"]:hover {{
    background: #D4901E;
}}

/* Danger variant */
QPushButton[variant="danger"] {{
    background: {C['red']};
    color: white;
}}
QPushButton[variant="danger"]:hover {{
    background: {C['accent_dim']};
}}

/* ══════════════════════════════════════════════════════
   COMBOBOX
══════════════════════════════════════════════════════ */
QComboBox {{
    background: {C['surface_2']};
    border: 1px solid {C['border']};
    border-radius: {R_MD};
    color: {C['text_0']};
    padding: 0 14px;
    min-height: 40px;
    font-size: 13px;
}}
QComboBox:hover {{
    border-color: {C['text_3']};
}}
QComboBox:focus {{
    border-color: {C['accent']};
}}
QComboBox::drop-down {{
    border: none;
    width: 32px;
    padding-right: 8px;
}}
QComboBox::down-arrow {{
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {C['text_2']};
    width: 0;
    height: 0;
}}
QComboBox QAbstractItemView {{
    background: {C['surface_1']};
    border: 1px solid {C['border']};
    border-radius: {R_MD};
    color: {C['text_1']};
    selection-background-color: {C['surface_3']};
    selection-color: {C['text_0']};
    padding: 4px;
    outline: none;
}}
QComboBox QAbstractItemView::item {{
    min-height: 34px;
    padding: 0 12px;
    border-radius: {R_SM};
}}
QComboBox QAbstractItemView::item:hover {{
    background: {C['surface_3']};
}}

/* ══════════════════════════════════════════════════════
   SPINBOX
══════════════════════════════════════════════════════ */
QSpinBox, QDoubleSpinBox {{
    background: {C['surface_2']};
    border: 1px solid {C['border']};
    border-radius: {R_MD};
    color: {C['text_0']};
    padding: 0 12px;
    min-height: 40px;
    font-size: 13px;
    font-family: '{FONT_MONO}';
}}
QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {C['accent']};
}}
QSpinBox::up-button, QDoubleSpinBox::up-button {{
    background: {C['surface_3']};
    border: none;
    border-left: 1px solid {C['border']};
    border-bottom: 1px solid {C['border']};
    border-top-right-radius: {R_MD};
    width: 24px;
}}
QSpinBox::down-button, QDoubleSpinBox::down-button {{
    background: {C['surface_3']};
    border: none;
    border-left: 1px solid {C['border']};
    border-bottom-right-radius: {R_MD};
    width: 24px;
}}
QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
    background: {C['accent']};
}}
QSpinBox::up-arrow {{
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 5px solid {C['text_2']};
}}
QSpinBox::down-arrow {{
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {C['text_2']};
}}

/* ══════════════════════════════════════════════════════
   TABLES  — the heartbeat of a data app
══════════════════════════════════════════════════════ */
QTableWidget {{
    background: {C['surface_1']};
    border: 1px solid {C['border']};
    border-radius: {R_LG};
    gridline-color: {C['border']};
    alternate-background-color: {C['surface_2']};
    color: {C['text_1']};
    outline: none;
    selection-background-color: {C['surface_3']};
    selection-color: {C['text_0']};
}}
QTableWidget::item {{
    padding: 0 16px;
    min-height: 44px;
    border: none;
    color: {C['text_1']};
}}
QTableWidget::item:hover {{
    background: {C['surface_3']};
    color: {C['text_0']};
}}
QTableWidget::item:selected {{
    background: {C['surface_3']};
    color: {C['text_0']};
    border-left: 2px solid {C['accent']};
}}
QHeaderView {{
    background: transparent;
    border: none;
}}
QHeaderView::section {{
    background: {C['surface_0']};
    color: {C['text_3']};
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 0 16px;
    min-height: 36px;
    border: none;
    border-bottom: 1px solid {C['border']};
    border-right: 1px solid {C['border']};
}}
QHeaderView::section:first {{
    border-top-left-radius: {R_LG};
}}
QHeaderView::section:last {{
    border-top-right-radius: {R_LG};
    border-right: none;
}}
QHeaderView::section:hover {{
    background: {C['surface_1']};
    color: {C['text_1']};
}}
QTableCornerButton::section {{
    background: {C['surface_0']};
    border: none;
    border-bottom: 1px solid {C['border']};
}}

/* ══════════════════════════════════════════════════════
   LIST WIDGET
══════════════════════════════════════════════════════ */
QListWidget {{
    background: {C['surface_1']};
    border: 1px solid {C['border']};
    border-radius: {R_LG};
    color: {C['text_1']};
    outline: none;
}}
QListWidget::item {{
    padding: 10px 16px;
    border-bottom: 1px solid {C['border']};
    color: {C['text_1']};
}}
QListWidget::item:hover {{
    background: {C['surface_2']};
    color: {C['text_0']};
}}
QListWidget::item:selected {{
    background: {C['accent_glow']};
    color: {C['accent']};
    border-left: 2px solid {C['accent']};
}}

/* ══════════════════════════════════════════════════════
   TAB WIDGET
══════════════════════════════════════════════════════ */
QTabWidget::pane {{
    background: {C['surface_1']};
    border: 1px solid {C['border']};
    border-radius: {R_LG};
    top: -1px;
}}
QTabBar {{
    background: transparent;
}}
QTabBar::tab {{
    background: transparent;
    color: {C['text_2']};
    padding: 10px 20px;
    font-size: 13px;
    font-weight: 500;
    border: none;
    border-bottom: 2px solid transparent;
    margin-right: 4px;
    min-width: 90px;
}}
QTabBar::tab:hover {{
    color: {C['text_0']};
    background: {C['surface_2']};
    border-radius: {R_MD} {R_MD} 0 0;
}}
QTabBar::tab:selected {{
    color: {C['accent']};
    font-weight: 700;
    border-bottom: 2px solid {C['accent']};
    background: transparent;
}}

/* ══════════════════════════════════════════════════════
   DIALOGS & MESSAGE BOXES
══════════════════════════════════════════════════════ */
QDialog {{
    background: {C['surface_1']};
    border: 1px solid {C['border']};
    border-radius: {R_LG};
}}
QMessageBox {{
    background: {C['surface_1']};
}}
QMessageBox QLabel {{
    color: {C['text_1']};
    font-size: 13px;
}}
QMessageBox QPushButton {{
    min-width: 90px;
    min-height: 34px;
}}

/* ══════════════════════════════════════════════════════
   FORM LAYOUT LABELS
══════════════════════════════════════════════════════ */
QFormLayout QLabel {{
    color: {C['text_2']};
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.3px;
    min-height: 40px;
}}

/* ══════════════════════════════════════════════════════
   TOOLTIP
══════════════════════════════════════════════════════ */
QToolTip {{
    background: {C['surface_3']};
    color: {C['text_0']};
    border: 1px solid {C['border']};
    border-radius: {R_SM};
    padding: 6px 10px;
    font-size: 12px;
}}

/* ══════════════════════════════════════════════════════
   CHECKBOXES
══════════════════════════════════════════════════════ */
QCheckBox {{
    color: {C['text_1']};
    spacing: 8px;
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1.5px solid {C['border']};
    border-radius: 3px;
    background: {C['surface_2']};
}}
QCheckBox::indicator:hover {{
    border-color: {C['accent']};
}}
QCheckBox::indicator:checked {{
    background: {C['accent']};
    border-color: {C['accent']};
    image: none;
}}

/* ══════════════════════════════════════════════════════
   RADIO BUTTONS
══════════════════════════════════════════════════════ */
QRadioButton {{
    color: {C['text_1']};
    spacing: 8px;
}}
QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border: 1.5px solid {C['border']};
    border-radius: 8px;
    background: {C['surface_2']};
}}
QRadioButton::indicator:checked {{
    background: {C['accent']};
    border-color: {C['accent']};
}}

/* ══════════════════════════════════════════════════════
   FRAME VARIANTS
══════════════════════════════════════════════════════ */
QFrame[variant="card"] {{
    background: {C['surface_1']};
    border: 1px solid {C['border']};
    border-radius: {R_LG};
}}
QFrame[variant="sidebar"] {{
    background: {C['surface_0']};
    border: none;
    border-right: 1px solid {C['border']};
}}
QFrame[variant="topbar"] {{
    background: {C['surface_0']};
    border: none;
    border-bottom: 1px solid {C['border']};
}}
QFrame[variant="divider"] {{
    background: {C['border']};
    max-height: 1px;
    border: none;
}}


/* ══════════════════════════════════════════════════════
   SIDEBAR NAV BUTTONS  (set via objectName)
══════════════════════════════════════════════════════ */
QPushButton#navBtn {{
    background: transparent;
    color: {C['text_2']};
    border: none;
    border-radius: 0;
    text-align: left;
    padding: 0 0 0 18px;
    min-height: 44px;
    font-size: 13px;
    font-weight: 500;
    letter-spacing: 0.1px;
}}
QPushButton#navBtn:hover {{
    background: {C['surface_1']};
    color: {C['text_0']};
}}
QPushButton#navBtn[active="true"] {{
    background: {C['accent_glow']};
    color: {C['accent']};
    font-weight: 700;
    border-left: 2px solid {C['accent']};
    padding-left: 16px;
}}

/* ══════════════════════════════════════════════════════
   STACKED WIDGET / SCROLL AREA
══════════════════════════════════════════════════════ */
QStackedWidget {{
    background: {C['bg']};
    border: none;
}}
QScrollArea {{
    background: transparent;
    border: none;
}}
QScrollArea > QWidget > QWidget {{
    background: transparent;
}}

"""

def badge(text, kind="default"):
    """Return a styled QLabel acting as a status badge."""
    from PyQt6.QtWidgets import QLabel
    from PyQt6.QtCore import Qt
    palette = {
        "success": (C["green"],     C["green_bg"]),
        "warning": (C["yellow"],    C["yellow_bg"]),
        "danger":  (C["red"],       C["red_bg"]),
        "info":    (C["blue"],      C["blue_bg"]),
        "default": (C["text_2"],    C["surface_3"]),
    }
    fg, bg = palette.get(kind, palette["default"])
    lbl = QLabel(text)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setFixedHeight(22)
    lbl.setStyleSheet(f"""
        QLabel {{
            background: {bg};
            color: {fg};
            border-radius: 3px;
            padding: 0 8px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.5px;
        }}
    """)
    return lbl


def status_badge(status_text):
    mapping = {
        "Pending":    "warning",
        "In-Kitchen": "warning",
        "Ready":      "info",
        "Served":     "success",
        "Completed":  "success",
        "Cancelled":  "danger",
        "Available":  "success",
        "Occupied":   "danger",
        "Reserved":   "warning",
        "Ordered":    "warning",
        "Delivered":  "success",
        "Present":    "success",
        "Absent":     "danger",
        "Late":       "warning",
    }
    return badge(status_text.upper(), mapping.get(status_text, "default"))


def divider():
    from PyQt6.QtWidgets import QFrame
    f = QFrame()
    f.setFixedHeight(1)
    f.setProperty("variant", "divider")
    f.setStyleSheet(f"background: {C['border']}; border: none; max-height: 1px;")
    return f


def section_label(text):
    from PyQt6.QtWidgets import QLabel
    lbl = QLabel(text.upper())
    lbl.setStyleSheet(f"""
        color: {C['text_3']};
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 2px;
        background: transparent;
        padding: 4px 0;
    """)
    return lbl


def heading(text, size=20):
    from PyQt6.QtWidgets import QLabel
    lbl = QLabel(text)
    lbl.setStyleSheet(f"""
        color: {C['text_0']};
        font-size: {size}px;
        font-weight: 700;
        letter-spacing: -0.3px;
        background: transparent;
    """)
    return lbl


def subheading(text):
    from PyQt6.QtWidgets import QLabel
    lbl = QLabel(text)
    lbl.setStyleSheet(f"color: {C['text_2']}; font-size: 13px; background: transparent;")
    return lbl


def stat_card(icon, value, label, sublabel="", accent=None):
    """A KPI stat card widget."""
    from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QFont

    ac = accent or C["accent"]
    card = QFrame()
    card.setMinimumHeight(108)
    card.setStyleSheet(f"""
        QFrame {{
            background: {C['surface_1']};
            border: 1px solid {C['border']};
            border-radius: {R_LG};
            border-left: 2px solid {ac};
        }}
        QFrame:hover {{
            background: {C['surface_2']};
            border-color: {C['text_3']};
            border-left-color: {ac};
        }}
    """)

    layout = QVBoxLayout(card)
    layout.setContentsMargins(20, 16, 20, 16)
    layout.setSpacing(4)

    top = QHBoxLayout()
    icon_lbl = QLabel(icon)
    icon_lbl.setFont(QFont("Segoe UI Emoji", 16))
    icon_lbl.setStyleSheet(f"color: {ac}; background: transparent;")
    top.addStretch()
    top.addWidget(icon_lbl)
    layout.addLayout(top)

    val_lbl = QLabel(value)
    val_lbl.setStyleSheet(f"""
        color: {C['text_0']};
        font-size: 28px;
        font-weight: 700;
        font-family: '{FONT_MONO}';
        letter-spacing: -1px;
        background: transparent;
    """)
    layout.addWidget(val_lbl)

    lbl = QLabel(label)
    lbl.setStyleSheet(f"color: {C['text_1']}; font-size: 13px; font-weight: 600; background: transparent;")
    layout.addWidget(lbl)

    if sublabel:
        sub = QLabel(sublabel)
        sub.setStyleSheet(f"color: {C['text_3']}; font-size: 11px; background: transparent;")
        layout.addWidget(sub)

    return card


def page_header(title, subtitle=""):
    """Standard page top-bar with title + subtitle."""
    from PyQt6.QtWidgets import QWidget, QVBoxLayout
    w = QWidget()
    w.setStyleSheet("background: transparent;")
    l = QVBoxLayout(w)
    l.setContentsMargins(0, 0, 0, 0)
    l.setSpacing(3)
    l.addWidget(heading(title))
    if subtitle:
        l.addWidget(subheading(subtitle))
    return w


def styled_table(columns, stretch_last=True, alternating=True):
    """Return a pre-styled QTableWidget."""
    from PyQt6.QtWidgets import QTableWidget
    t = QTableWidget(0, len(columns))
    t.setHorizontalHeaderLabels(columns)
    t.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    t.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    t.setAlternatingRowColors(alternating)
    t.verticalHeader().setVisible(False)
    t.setShowGrid(False)
    t.setFocusPolicy(t.focusPolicy())
    if stretch_last:
        t.horizontalHeader().setStretchLastSection(True)
    return t


def card_frame():
    from PyQt6.QtWidgets import QFrame
    f = QFrame()
    f.setProperty("variant", "card")
    f.setStyleSheet(f"""
        QFrame {{
            background: {C['surface_1']};
            border: 1px solid {C['border']};
            border-radius: {R_LG};
        }}
    """)
    return f


def ghost_btn(text):
    from PyQt6.QtWidgets import QPushButton
    b = QPushButton(text)
    b.setProperty("variant", "ghost")
    b.setStyleSheet(f"""
        QPushButton {{
            background: transparent;
            color: {C['text_1']};
            border: 1px solid {C['border']};
            border-radius: {R_MD};
            padding: 0 16px;
            min-height: 36px;
            font-size: 13px;
            font-weight: 500;
        }}
        QPushButton:hover {{
            background: {C['surface_2']};
            border-color: {C['text_3']};
            color: {C['text_0']};
        }}
        QPushButton:pressed {{
            background: {C['surface_3']};
        }}
    """)
    return b


def accent_btn(text):
    from PyQt6.QtWidgets import QPushButton
    b = QPushButton(text)
    b.setStyleSheet(f"""
        QPushButton {{
            background: {C['accent']};
            color: white;
            border: none;
            border-radius: {R_MD};
            padding: 0 20px;
            min-height: 38px;
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 0.2px;
        }}
        QPushButton:hover {{ background: {C['accent_dim']}; }}
        QPushButton:pressed {{ background: #8C1E26; padding-top: 1px; }}
        QPushButton:disabled {{ background: {C['surface_3']}; color: {C['text_3']}; }}
    """)
    return b


def success_btn(text):
    from PyQt6.QtWidgets import QPushButton
    b = QPushButton(text)
    b.setStyleSheet(f"""
        QPushButton {{
            background: {C['green']};
            color: #000;
            border: none;
            border-radius: {R_MD};
            padding: 0 20px;
            min-height: 38px;
            font-size: 13px;
            font-weight: 700;
        }}
        QPushButton:hover {{ background: #00A87E; }}
        QPushButton:pressed {{ background: #008060; }}
        QPushButton:disabled {{ background: {C['surface_3']}; color: {C['text_3']}; }}
    """)
    return b


def warning_btn(text):
    from PyQt6.QtWidgets import QPushButton
    b = QPushButton(text)
    b.setStyleSheet(f"""
        QPushButton {{
            background: {C['yellow']};
            color: #000;
            border: none;
            border-radius: {R_MD};
            padding: 0 20px;
            min-height: 38px;
            font-size: 13px;
            font-weight: 700;
        }}
        QPushButton:hover {{ background: #D4901E; }}
        QPushButton:pressed {{ background: #A8701A; }}
    """)
    return b