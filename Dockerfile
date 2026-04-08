# Stage 1: Builder
FROM python:3.10-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.10-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy project files
COPY models.py .
COPY openenv_models.py .
COPY environment.py .
COPY data.py .
COPY evaluator.py .
COPY grader.py .
COPY hard_defender_agent.py .
COPY inference.py .
COPY openenv.yaml .

# Create output directory
RUN mkdir -p /app/outputs

# Environment variables (with defaults)
ENV API_BASE_URL=https://api.openai.com/v1
ENV MODEL_NAME=gpt-3.5-turbo
ENV HF_TOKEN=""
ENV USE_LLM=false
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command: run inference
CMD ["python", "inference.py"]

# Alternative: Run as server (for Hugging Face Spaces)
# CMD ["python", "server.py"]
