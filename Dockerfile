FROM python:3.11-slim

WORKDIR /app

# Copy only necessary files
COPY pyproject.toml .
COPY src/db_agent/ src/db_agent/

# Install dependencies
RUN pip install --no-cache-dir -e .

# Run the server
CMD ["python", "-m", "db_agent.server", "--transport", "http", "--host", "0.0.0.0", "--port", "9002"]
