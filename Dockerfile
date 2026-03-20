# 1. Use an official Python 3.12 slim image for a smaller footprint
FROM python:3.12-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Install system dependencies (needed for some Python libraries or NumPy)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy ONLY the requirements file first to leverage Docker cache
COPY requirements.txt .

# 5. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the entire project (src, setup.cfg, pyproject.toml, etc.)
COPY . .

# 7. Install your package in "editable" mode or standard mode
# This ensures your 'predictor' console_script is created inside the container
RUN pip install -e .

# 8. Define the command to run your app
# Since you defined 'predictor' in setup.cfg, you can call it directly
ENTRYPOINT ["predictor"]

# Default arguments (can be overridden when running the container)
CMD ["--segment-body", "Thigh"]