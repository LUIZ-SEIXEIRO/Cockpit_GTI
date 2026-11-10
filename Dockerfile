FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir Flask requests urllib3 PyMySQL
COPY . .
EXPOSE 5000
ENV PORT=5000
ENV PYTHONUNBUFFERED=1
ENTRYPOINT []
CMD ["python", "main.py"]
