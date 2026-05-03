FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY src/zkali_mcp/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/zkali_mcp/ ./

# Create data directory for the database
RUN mkdir -p /data

# Default environment variables
ENV MCP_DB_PATH=/data/zkali.db \
    MCP_TRANSPORT=streamable-http \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8000

EXPOSE 8000

ENTRYPOINT ["python", "main.py"]
