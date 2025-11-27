FROM python:3.11-slim-bookworm

WORKDIR /app

ARG UID=10001
ARG GID=10001

# Create non-root user
RUN groupadd --gid ${GID} app \
    && useradd --uid ${UID} --gid ${GID} --home-dir /home/app --create-home app

# System deps + curl (needed for code-server install)
RUN apt-get update && apt-get install -y --no-install-recommends \
    make \
    gcc \
    git \
    tree \
    libpq-dev \
    gdal-bin libgdal-dev \
    libproj-dev libgeos-dev binutils \
    postgresql-client \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install code-server system-wide
# It will place the binary into /usr/local/bin/code-server
RUN curl -fsSL https://code-server.dev/install.sh | sh -s -- --method=standalone --prefix=/usr/local

USER ${UID}:${GID}

RUN pip install --upgrade pip 

COPY --chown=${UID}:${GID} requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=${UID}:${GID} . .

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["code-server", "--bind-addr", "0.0.0.0:8080", "/app"]
