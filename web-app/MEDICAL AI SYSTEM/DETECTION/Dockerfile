FROM python:3.11-slim

# ==========================================
# SYSTEM DEPENDENCIES
# ==========================================

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# ==========================================
# WORKING DIRECTORY
# ==========================================

WORKDIR /app

# ==========================================
# COPY REQUIREMENTS FIRST
# (Docker cache optimization)
# ==========================================

COPY requirements.txt .

# ==========================================
# INSTALL PYTHON DEPENDENCIES
# ==========================================

RUN pip install --no-cache-dir --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

# ==========================================
# COPY APPLICATION
# ==========================================

COPY . .

# ==========================================
# CREATE OUTPUT FOLDERS
# ==========================================

RUN mkdir -p output

# ==========================================
# EXPOSE PORT
# ==========================================

EXPOSE 8003

# ==========================================
# START SERVICE
# ==========================================

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8003"]
