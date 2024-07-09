# Dockerfile
# Use the latest Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY ife_contact_list.py .

# You will need to set these private environment variables, no defaults
# ENV OPENCAGE_API_KEY="YOUR_API_KEY"
# ENV TARGET_POSTCODE="TARGET_POSTCODE"

# You can set these environment variables, they have defaults
# ENV FILENAME="CEngandIEngUKlisting23.02.24.xlsx"
# ENV IFE_BASE_URL="https://www.ife.org.uk/write/MediaUploads/"
# ENV DATA_DIRECTORY="/data"

# Mount the data directory
VOLUME /data

# Run the application
CMD ["python", "ife_contact_list.py"]
