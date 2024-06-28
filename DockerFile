# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install PostgreSQL client libraries
RUN apt-get update && apt-get install -y libpq-dev gcc

# Copy the current directory contents into the container at /app
COPY . /app

# Install psycopg2 for PostgreSQL connections
RUN pip install --no-cache-dir psycopg2-binary

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Use ARG for build-time variables
ARG DATAFORSEO_USERNAME
ARG DATAFORSEO_PASSWORD

# Set environment variables
ENV DATAFORSEO_USERNAME=${DATAFORSEO_USERNAME}
ENV DATAFORSEO_PASSWORD=${DATAFORSEO_PASSWORD}

# Run both scripts when the container launches
CMD ["python", "-c", "import GoogleMapsEndPoint_Filtered as filtered; import GoogleMapsEndPoint_raw as raw; filtered.main(); raw.main()"]
