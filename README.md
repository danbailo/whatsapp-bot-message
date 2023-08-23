# Whatsapp Bot Message

A simple application to send messages for contacts that was writed in
[numbers.xlsx](resources/numbers.xlsx).


## Requirements

* [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/) if you'll run with Docker


* [Python](https://www.python.org/downloads/) - v3.11 (tested) if you'll run directly with Python

obs: if you'll run directly with Python, it's recommended to use virtual enviroment, like as [pyenv](https://github.com/pyenv/pyenv)

## Running application w/ Docker - Linux Based

```bash
docker compose down && docker compose up --build
```

Whenever you change the [numbers.xlsx](resources/numbers.xlsx), you will need to re-execute `docker compose down && docker compose up --build`

## Running w/ Python - Linux Based

Start a [Selenium](https://github.com/SeleniumHQ/docker-selenium) container with Chrome image.

Recommended

```bash
docker run --name selenium-whatsapp -d -p 4444:4444 -p 7900:7900 --network host -v /tmp:/tmp -v /dev/shm:/dev/shm --env SE_NODE_MAX_SESSIONS=4 --env SE_NODE_SESSION_TIMEOUT=1800 --env SE_NODE_OVERRIDE_MAX_SESSIONS=TRUE selenium/standalone-chrome:113.0-20230508
```

```bash
pip install -r requirements.txt
cd src
python -m main
```

After run application, you need to access http://localhost:7900/?autoconnect=1&password=secret and scan the QRCode.

You have 5 minutes to scan it, otherwise the application will failed.
