FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY main.py .

# Create output directory
RUN mkdir -p /output

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app /output

USER app

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Default output directory
ENV PORTAINER_OUTPUT_FILE=/output/portainer-docs.md

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.path.insert(0, '/app/src'); from portainer_documenter import __version__; print(__version__)" || exit 1

# Default command
ENTRYPOINT ["python", "main.py"]