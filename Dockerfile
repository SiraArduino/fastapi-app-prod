# ใช้ base image ที่มี python อยู่แล้ว
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements และติดตั้ง
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project เข้า container
COPY . .

# Set env vars (optional แต่แนะนำ)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# เปิด port
EXPOSE 8000

# คำสั่งเริ่มแอป
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
