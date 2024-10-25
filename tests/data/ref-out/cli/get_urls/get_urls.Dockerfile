FROM python:3-slim

WORKDIR /app

RUN pip install pyeodh click

COPY get_urls.py app.py

CMD ["python"]