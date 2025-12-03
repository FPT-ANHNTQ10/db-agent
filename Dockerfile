FROM python:3.11-slim

WORKDIR /app

# Copy only pyproject.toml first to cache dependencies layer
COPY pyproject.toml .

# Install dependencies only (this layer will be cached)
RUN pip install --no-cache-dir fastmcp==2.11.3 pydantic>=2.5.0 psycopg2-binary>=2.9.0

# Copy source code (this layer changes when code changes)
COPY src/ src/

# Install package in editable mode (fast since deps already installed)
RUN pip install --no-cache-dir -e . --no-deps

# Run the server
CMD ["python", "-m", "db_agent.server", "--transport", "http", "--host", "0.0.0.0", "--port", "9002"]
