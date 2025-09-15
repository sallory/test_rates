# ---- Builder stage ----
FROM python:3.12-slim AS builder

WORKDIR /code

COPY requirements ./requirements
RUN pip install --upgrade pip \
    && pip install --prefix=/install -r requirements/local.txt

# ---- Runtime stage ----
FROM python:3.12-slim AS runtime

WORKDIR /code

COPY --from=builder /install /usr/local

COPY pyproject.toml .
COPY alembic.ini .

COPY src ./src
COPY tests ./tests
COPY migrations ./migrations
COPY scripts /scripts

RUN chmod +x /scripts/*.sh

RUN pip install -e .

ENTRYPOINT ["/scripts/entrypoint.sh"]
CMD ["/scripts/start-reload.sh"]