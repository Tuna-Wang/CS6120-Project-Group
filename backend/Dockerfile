# Use an official Python image
FROM python:3.10-slim

# Set workdir
WORKDIR /app

# Copy dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy your app code
COPY . .

# Expose port (match what your app runs on)
EXPOSE 8000

# Run the app
CMD ["python3", "main.py"]
