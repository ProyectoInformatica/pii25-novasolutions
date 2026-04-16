BTN_PRIMARY = """
QPushButton{
    background-color:#3489e2;
    color:white;
    padding:10px;
    border-radius:10px;
    font-size:14px;
}
QPushButton:hover{ background-color:#2f7fd1; }
QPushButton:pressed{ background-color:#2a72ba; }
"""

BTN_DANGER = """
QPushButton{
    background-color:#AA3333;
    color:white;
    padding:10px;
    border-radius:10px;
    font-size:14px;
}
QPushButton:hover{ background-color:#972d2d; }
QPushButton:pressed{ background-color:#822727; }
"""

BTN_NEUTRAL = """
QPushButton{
    background-color:#2b2f36;
    color:white;
    padding:10px;
    border-radius:10px;
    font-size:14px;
    border: 1px solid rgba(255,255,255,0.10);
}
QPushButton:hover{ background-color:#333844; }
QPushButton:pressed{ background-color:#2a2e38; }
"""

INPUT_STYLE = """
QLineEdit{
    padding:10px;
    border-radius:10px;
    background:#1b214d;
    border:1px solid rgba(255,255,255,0.15);
    color:white;
}
QLineEdit:focus{
    border:1px solid rgba(52,137,226,0.85);
}
"""

LIST_STYLE = """
QListWidget{
    background:#141b44;
    color:white;
    border:1px solid rgba(255,255,255,0.12);
    border-radius:10px;
    padding:6px;
}
QListWidget::item{
    padding:8px;
    border-radius:8px;
}
QListWidget::item:selected{
    background: rgba(52,137,226,0.45);
    border: 1px solid rgba(52,137,226,0.75);
}
QListWidget::item:hover{
    background: rgba(255,255,255,0.06);
}
"""

PANEL_STYLE = """
QGroupBox {
    border: 1px solid #555;
    margin-top: 18px;
    padding-top: 10px;
    border-radius: 10px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 8px;
    margin-left: 10px;
    color: white;
    font-weight: 600;
}
"""

GROUPBOX_STYLE = """
QGroupBox { border: 1px solid #555; margin-top: 18px; padding-top: 10px; font-weight: bold; }
QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 6px; }
"""