# Whatsapp Bot Message

A simple application to send messages for contacts that was writed in
[numbers.xlsx](resources/numbers.xlsx).

## Running application

### Start selenium
```bash
$ docker run --name selenium-chrome -d -p 4444:4444 -p 7900:7900 --shm-size="2g" --env SE_NODE_SESSION_TIMEOUT=1800 --env SE_NODE_OVERRIDE_MAX_SESSIONS=TRUE selenium/standalone-chrome:115.0
```


### Build application
```bash
$ docker build -t whatsapp-message-bot -f Dockerfile .
```

### First run
```bash
$ docker run --name whatsapp-message-bot --network host -it whatsapp-message-bot /bin/bash
```

### After first run

After run the container first time, the container is already created, then, you just need to attach it.

```bash
$ docker start whatsapp-message-bot
```

```bash
$ docker attach whatsapp-message-bot
```