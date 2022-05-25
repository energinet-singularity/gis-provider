FROM python:3.10.0-slim-bullseye

# Load python requirements-file
COPY app/requirements.txt /

# Upgrade pip., install requirements and add non-root user
RUN apt-get update && apt install -y git 
RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt --no-cache-dir && \
    rm requirements.txt && \
    groupadd -r localuser && \
    useradd -r -g localuser localuser

USER localuser

ARG API_PORT=5000
EXPOSE ${API_PORT}

# Copy required files into container
COPY app/* /app/
COPY tests/valid-testdata/* /testdata/

# Run the application
CMD ["python3", "-u", "/app/main.py"]
