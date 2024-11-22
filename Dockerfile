FROM ubuntu

LABEL maintainer="Christopher L.D. SHEN <shenleidi@gmail.com>"

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
      python3-gdal \
      python3-skimage \
      python3-numpy \
      python3-geopy \
      python3-matplotlib \
      python3-pandas \
      python3-flask \
      gunicorn \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY port.py planner.py app.py ports.csv /app/
COPY raw-data/map.tif /app/raw-data/map.tif

WORKDIR /app

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
