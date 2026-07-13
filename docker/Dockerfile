FROM python:3.13-slim-bookworm AS builder
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_NO_CACHE_DIR=1
WORKDIR /build
COPY pyproject.toml requirements.lock README.md LICENSE ./
COPY app ./app
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install --requirement requirements.lock \
    && /opt/venv/bin/pip install --no-deps .

FROM python:3.13-slim-bookworm AS production
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 APP_ENV=production PATH=/opt/venv/bin:$PATH
RUN apt-get update && apt-get install -y --no-install-recommends curl dumb-init && rm -rf /var/lib/apt/lists/* && groupadd --gid 1000 educinfo && useradd --uid 1000 --gid educinfo --home-dir /app --create-home educinfo
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY --chown=educinfo:educinfo run.py ./
COPY --chown=educinfo:educinfo docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod 755 /usr/local/bin/entrypoint.sh && mkdir -p /app/instance && chown -R educinfo:educinfo /app/instance
USER educinfo
EXPOSE 5000
VOLUME ["/app/instance"]
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 CMD curl -fsS http://localhost:5000/health/ready || exit 1
ENTRYPOINT ["/usr/bin/dumb-init", "--", "/usr/local/bin/entrypoint.sh"]
CMD ["gunicorn", "--bind=0.0.0.0:5000", "--worker-class=gthread", "--workers=1", "--threads=4", "--timeout=30", "--access-logfile=-", "--error-logfile=-", "run:app"]
