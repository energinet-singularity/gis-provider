# Select base-image
FROM python:3.10.0-slim-bullseye

# Load python requirements-file
COPY app/requirements.txt /

# Upgrade pip., install requirements and add non-root user
RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt --no-cache-dir && \
    rm requirements.txt && \
    groupadd -r localuser && \
    useradd -r -g localuser localuser

# Switch to new user-account
USER localuser

# Copy required files into container
COPY app/* /app/

# Run the application
CMD ["python3", "-u", "/app/my_script.py"]
