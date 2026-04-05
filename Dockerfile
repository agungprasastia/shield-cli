FROM python:3.12-slim

LABEL maintainer="Shield Team"
LABEL description="AI-Powered Penetration Testing CLI Tool"

# Install system packages and security tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    nmap \
    nikto \
    git \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python-based tools
RUN pip install --no-cache-dir sqlmap wafw00f sslyze arjun dnsrecon cmseek

WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY config/ config/
COPY ai/ ai/
COPY cli/ cli/
COPY core/ core/
COPY tools/ tools/
COPY reports/ reports/
COPY workflows/ workflows/
COPY utils/ utils/

# Install Shield
RUN pip install --no-cache-dir -e .

# Create reports directory
RUN mkdir -p /app/reports /app/logs

ENTRYPOINT ["python", "-m", "cli.main"]
