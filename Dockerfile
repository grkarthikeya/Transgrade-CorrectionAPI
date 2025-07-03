# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy the application code first
COPY . .

# Remove problematic files that might cause build issues
RUN rm -rf .venv __pycache__ *.egg-info build dist

# Install dependencies from requirements.txt only
RUN pip install --no-cache-dir -r requirements.txt

# Install CrewAI and common tools if not already in requirements
RUN pip install --no-cache-dir crewai crewai-tools

# Make sure all Python files are accessible
RUN find /app -name "*.py" -type f -exec chmod +r {} \;

# Create an entrypoint script that tries different ways to run the crew
RUN echo '#!/bin/bash\n\
echo "Attempting to run CrewAI..."\n\
\n\
# Try method 1: crewai run\n\
if command -v crewai >/dev/null 2>&1; then\n\
    echo "Trying: crewai run"\n\
    crewai run && exit 0\n\
fi\n\
\n\
# Try method 2: Look for main crew files\n\
if [ -f "main.py" ]; then\n\
    echo "Trying: python main.py"\n\
    python main.py && exit 0\n\
fi\n\
\n\
if [ -f "run_crew.py" ]; then\n\
    echo "Trying: python run_crew.py"\n\
    python run_crew.py && exit 0\n\
fi\n\
\n\
if [ -f "crew.py" ]; then\n\
    echo "Trying: python crew.py"\n\
    python crew.py && exit 0\n\
fi\n\
\n\
# Try method 3: Look for any Python file with "crew" in the name\n\
CREW_FILE=$(find . -name "*crew*.py" -type f | head -1)\n\
if [ -n "$CREW_FILE" ]; then\n\
    echo "Trying: python $CREW_FILE"\n\
    python "$CREW_FILE" && exit 0\n\
fi\n\
\n\
echo "Could not find a way to run the crew. Available Python files:"\n\
find . -name "*.py" -type f\n\
echo ""\n\
echo "Please check your project structure and update the CMD in Dockerfile"\n\
exit 1\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Expose the port the app runs on
EXPOSE 5055

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5055/health || exit 1

# Use the flexible entrypoint
CMD ["/app/entrypoint.sh"]