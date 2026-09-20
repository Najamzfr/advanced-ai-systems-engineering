FROM python:3.12-slim
WORKDIR /app
COPY . .
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8080
RUN python project.py --allow-sample >/dev/null
RUN rm -rf reports __pycache__
EXPOSE 8080
USER nobody
CMD ["python","serve.py"]
