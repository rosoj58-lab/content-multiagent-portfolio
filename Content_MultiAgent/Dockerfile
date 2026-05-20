FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY . .

RUN if [ -f pyproject.toml ]; then \
      if [ -f uv.lock ]; then uv sync --frozen; else uv sync; fi; \
    fi

EXPOSE 8501

CMD ["sh", "-lc", "if [ -f app.py ]; then uv run streamlit run app.py --server.address=0.0.0.0 --server.port=8501; elif [ -f src/seo_content_pipeline/app.py ]; then uv run streamlit run src/seo_content_pipeline/app.py --server.address=0.0.0.0 --server.port=8501; else echo 'Project scaffold is ready. Add the Streamlit app, then run docker compose up --build.'; sleep infinity; fi"]
