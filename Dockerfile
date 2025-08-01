FROM python:3.10-slim

# -------------------------------
# ENVIRONMENT VARIABLES
# -------------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app/mycolony"
ENV DJANGO_SETTINGS_MODULE="mycolony.settings"
ENV FONT_PATH="/app/static/fonts/DejaVuSans.ttf"

# -------------------------------
# WORKING DIRECTORY
# -------------------------------
WORKDIR /app

# -------------------------------
# SYSTEM DEPENDENCIES
# -------------------------------
RUN apt-get update && \
    apt-get install -y \
        build-essential \
        libmariadb-dev \
        pkg-config \
        libfreetype6-dev \
        wget \
        unzip \
        libjpeg-dev \
        zlib1g-dev \
        file && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# -------------------------------
# PYTHON DEPENDENCIES
# -------------------------------
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# -------------------------------
# INSTALL DejaVu FONT
# -------------------------------
RUN mkdir -p /app/static/fonts/ && \
    wget -O /tmp/dejavu-fonts.zip \
        https://github.com/dejavu-fonts/dejavu-fonts/releases/download/version_2_37/dejavu-fonts-ttf-2.37.zip && \
    unzip /tmp/dejavu-fonts.zip -d /tmp/ && \
    find /tmp -name DejaVuSans.ttf -exec cp {} /app/static/fonts/ \; && \
    file /app/static/fonts/DejaVuSans.ttf && \
    chmod 644 /app/static/fonts/DejaVuSans.ttf && \
    chown nobody:nogroup /app/static/fonts/DejaVuSans.ttf && \
    rm -rf /tmp/dejavu-fonts* && \
    echo "✅ Font verification complete:" && \
    ls -la /app/static/fonts/ && \
    python -c "with open('/app/static/fonts/DejaVuSans.ttf', 'rb') as f: print(f'Font size: {len(f.read())} bytes')"

# -------------------------------
# COPY APPLICATION
# -------------------------------
COPY . .

# -------------------------------
# VERIFY FONT REGISTRATION
# -------------------------------
# -------------------------------
# VERIFY FONT REGISTRATION
# -------------------------------
# -------------------------------
# VERIFY FONT REGISTRATION
# -------------------------------
COPY verify_font.py /app/
RUN python verify_font.py



# -------------------------------
# COLLECT STATIC FILES
# -------------------------------
WORKDIR /app/mycolony
RUN python manage.py collectstatic --noinput --clear

# -------------------------------
# EXPOSE PORT AND START
# -------------------------------
EXPOSE 8080
CMD ["gunicorn", "mycolony.wsgi:application", "--bind", "0.0.0.0:8080"]





