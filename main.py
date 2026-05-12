# main.py
import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QFont
from theme import QSS, FONT
from database.connection import test_connection
from modules.login import LoginWindow


def main():
    print("=" * 52)
    print("   Restaurant Management System  —  v1.0")
    print("=" * 52)
    print("[startup] Initializing application...")

    app = QApplication(sys.argv)
    app.setApplicationName("Restaurant Management System")
    app.setStyle("Fusion")       # Fusion base — QSS overrides everything
    app.setFont(QFont(FONT, 13)) # Global font baseline
    app.setStyleSheet(QSS)       # Apply Obsidian & Ember theme globally

    print("[startup] Connecting to MS SQL Server...", end=" ", flush=True)
    if test_connection():
        print("✓  Connected successfully!")
    else:
        print("✗  Connection FAILED")
        QMessageBox.critical(None, "Database Error",
            "Cannot connect to the database.\n\n"
            "Check:\n"
            "  1. SQL Server service is running\n"
            "  2. Server name in database/connection.py\n"
            "  3. ODBC Driver 17 is installed")
        sys.exit(1)

    print("[startup] Launching UI...")
    print("=" * 52)

    window = LoginWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()