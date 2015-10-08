# Telepi
Telegram Bot for My raspberrypi

## Usage

1. Generate SSL
```
openssl req -new -x509 -nodes -newkey rsa:1024 -keyout server.key -out server.crt -days 365
```
2. Make config
```
[main]
token=xxxxxxxx:yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
crt=server.crt
key=server.key
#admin's chat_id
chat_id=nnnnnnnn
url=https://uuuu.rrrrr.lll./hook
```
3. Run
```
python main.py
```