FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN --mount=type=secret,id=pip_ca,target=/run/secrets/pip_ca \
    if [ -f /run/secrets/pip_ca ]; then export PIP_CERT=/run/secrets/pip_ca; fi && \
    pip install --no-cache-dir -r requirements.txt && useradd --create-home appuser
COPY --chmod=u=rwX,go=rX app ./app
USER appuser
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
