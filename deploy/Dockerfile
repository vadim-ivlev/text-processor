FROM python:3.7.6-slim-stretch

WORKDIR /usr/src/app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# CMD [ "python", "-u", "./server.py" ]
CMD while true; do echo 'text-processor.'; sleep 100; done