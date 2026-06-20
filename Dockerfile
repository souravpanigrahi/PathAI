FROM python:3.10-slim

WORKDIR /code

# Copy the requirements file and install dependencies
COPY backend/requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir -r /code/requirements.txt

# Copy the backend code into the container
COPY backend /code/backend

# Hugging Face runs containers with a non-root user (user ID 1000).
# We must ensure they have write permissions to the cache and data directories
# so osmnx can save the graphml file and use its HTTP cache.
RUN mkdir -p /code/backend/data /code/backend/cache && \
    chmod -R 777 /code/backend/data /code/backend/cache

# Hugging Face routes external traffic to port 7860 by default
EXPOSE 7860
ENV PORT=7860

# Set working directory to the backend so imports and relative paths resolve correctly
WORKDIR /code/backend

# Run FastAPI on port 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
