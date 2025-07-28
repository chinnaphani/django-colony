from django.contrib.staticfiles import finders
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

font_path = finders.find('fonts/DejaVuSans.ttf')
if font_path:
    pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))
else:
    raise FileNotFoundError("DejaVuSans.ttf not found in collected staticfiles.")
