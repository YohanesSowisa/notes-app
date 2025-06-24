# Python Base Image
FROM python:3.10.8

# Create Work Directory in Container
WORKDIR /app

# Copy all project folders in Container
COPY . /app

# Install all needed libraries
# RUN python -m pip install -v flask requests
RUN pip install -r requirements.txt

# Run Flask
CMD ["python", "main.py"]