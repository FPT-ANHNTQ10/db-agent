FROM python:3.11-slim

WORKDIR /app

# Install PostgreSQL client for healthcheck
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Copy only necessary files
COPY pyproject.toml .
COPY src/db_agent/ src/db_agent/
COPY entrypoint.sh /entrypoint.sh

# Install dependencies
RUN pip install --no-cache-dir -e .

# Make entrypoint executable
RUN chmod +x /entrypoint.sh

# Run the server
ENTRYPOINT ["/entrypoint.sh"]
