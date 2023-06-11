# Start from a base image
# FROM python:3.10-alpine
FROM python:3.10

# Install dependencies
# RUN apk update && apk add --no-cache \
#     curl \
#     make \
#     gcc \
#     g++ \
#     openssl-dev \
#     bzip2-dev \
#     libffi-dev \
#     zlib-dev \
#     sqlite-dev \
#     opus-dev
RUN apt-get update && apt-get install -y \
    wget \
    make \
    gcc \
    g++ \
    libssl-dev \
    libbz2-dev \
    libffi-dev \
    zlib1g-dev \
    libsqlite3-dev \
    libopus-dev \
    ffmpeg

# Install hts_engine_API
RUN curl -L https://downloads.sourceforge.net/project/hts-engine/hts_engine%20API/hts_engine_API-1.10/hts_engine_API-1.10.tar.gz -o hts_engine_API-1.10.tar.gz && \
    tar xzf hts_engine_API-1.10.tar.gz && \
    cd hts_engine_API-1.10 && \
    ./configure --prefix=/usr/local && \
    make && \
    make install && \
    cd ../ && \
    rm hts_engine_API-1.10.tar.gz && \
    rm -r hts_engine_API-1.10

# Install open_jtalk
RUN curl -L https://downloads.sourceforge.net/project/open-jtalk/Open%20JTalk/open_jtalk-1.10/open_jtalk-1.10.tar.gz -o open_jtalk-1.10.tar.gz && \
    tar xzf open_jtalk-1.10.tar.gz && \
    cd open_jtalk-1.10 && \
    ./configure --prefix=/usr/local && \
    make && \
    make install && \
    cd ../ && \
    rm open_jtalk-1.10.tar.gz && \
    rm -r open_jtalk-1.10

# Set the working directory
WORKDIR /app

# Copy requirements.txt
COPY requirements.txt .

# Install python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app's source code from your host to your image filesystem.
COPY . .

# Run py background
CMD ["python3.10", "main.py"]
