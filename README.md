# Whatsapp Bot Message

A simple application to send messages for contacts that was writed in
[numbers.xlsx](resources/numbers.xlsx).


## Requirements

* Docker & Docker compose

## Running application

```bash
docker compose down && docker compose up --build
```

After run application, you need to access http://localhost:7900/?autoconnect=1&resize=scale&password=secret
and scan the QRCode.

You have 5 minutes to scan it, otherwise the application will failed.

Whenever you change the [numbers.xlsx](resources/numbers.xlsx), you will need to re-execute `docker compose down && docker compose up --build`