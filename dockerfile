FROM python:3.11

WORKDIR /app

# Copy the rest of the application files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app/src