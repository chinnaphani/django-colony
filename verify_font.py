# verify_font.py
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

try:
    pdfmetrics.registerFont(TTFont('DejaVuSans', '/app/static/fonts/DejaVuSans.ttf'))
    print("Font registration successful!")
except Exception as e:
    print(f"Font registration failed: {e}")
    raise
