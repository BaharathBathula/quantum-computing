# Runs the whole project with no local Python setup and no cloud account:
#   docker build -t quantum-computing-9 .
#   docker run --rm quantum-computing-9                 # all nine concepts
#   docker run --rm quantum-computing-9 qlab test       # the test-suite
#   docker run --rm -v "$PWD/outputs:/app/outputs" quantum-computing-9   # keep the figures
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 MPLBACKEND=Agg
WORKDIR /app

COPY pyproject.toml requirements.txt README.md ./
COPY qlab ./qlab
COPY concepts ./concepts
COPY exercises ./exercises
COPY tests ./tests
COPY run_all.py grade.py ./
COPY web ./web

RUN pip install --no-cache-dir -e ".[dev]"

CMD ["qlab", "run"]
