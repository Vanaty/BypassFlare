# BypassFlare
[![GitHub issues](https://img.shields.io/github/issues/Vanaty/BypassFlare/)](https://github.com/Vanaty/BypassFlare/issues)
[![Donate Bitcoin](https://img.shields.io/badge/Donate-Bitcoin-f7931a.svg)](https://www.blockchain.com/btc/address/145ZargDFhQNSNw38Ycj56bEteQtJH56ya)
[![Donate Ethereum](https://img.shields.io/badge/Donate-Ethereum-8c8c8c.svg)](https://www.blockchain.com/eth/address/0x560EC50ca58219648d019B5ccE9756ab4b13cDb5)

BypassFlare is a proxy server to bypass Cloudflare and DDoS-GUARD protection.
No browser driver required.

## How it works

BypassFlare starts a proxy server, and it waits for user requests in an idle state using few resources.
When some request arrives, it uses [DrissionPage](https://github.com/g1879/DrissionPage)
to create a web browser (Chrome).
It opens the URL with user parameters and waits until the Cloudflare challenge
is solved (or timeout). The HTML code and the cookies are sent back to the user, and those cookies can be used to
bypass Cloudflare using other HTTP clients.

**NOTE**: Web browsers consume a lot of memory. If you are running BypassFlare on a machine with few RAM, do not make
many requests at once. With each request a new browser is launched.

It is also possible to use a permanent session. However, if you use sessions, you should make sure to close them as
soon as you are done using them.

## Installation

### From source code

> **Warning**
> Installing from source code only works for x64 architecture. For other architectures use Docker.

* Install [Python 3.11](https://www.python.org/downloads/).
* Install [Chrome](https://www.google.com/intl/en_us/chrome/) (all OS) or [Chromium](https://www.chromium.org/getting-involved/download-chromium/) (just Linux, it doesn't work in Windows) web browser.
* (Only in Linux) Install [Xvfb](https://en.wikipedia.org/wiki/Xvfb) package.
* (Only in macOS) Install [XQuartz](https://www.xquartz.org/) package.
* Clone this repository and open a shell in that path.
* Run `pip install -r requirements.txt` command to install BypassFlare dependencies.
* Run `python src/main.py` command to start BypassFlare.

### From source code (FreeBSD/TrueNAS CORE)

* Run `pkg install chromium python39 py39-pip xorg-vfbserver` command to install the required dependencies.
* Clone this repository and open a shell in that path.
* Run `python3.9 -m pip install -r requirements.txt` command to install BypassFlare dependencies.
* Run `python3.9 src/main.py` command to start BypassFlare.

### Systemd service

We provide an example Systemd unit file `bypassflare.service` as reference. You have to modify the file to suit your needs: paths, user and environment variables.

## Usage

Example Bash request:
```bash
curl -L -X POST 'http://localhost:8191/v1' \
-H 'Content-Type: application/json' \
--data-raw '{
  "cmd": "request.get",
  "url": "http://www.google.com/",
  "maxTimeout": 60000
}'
```

Example Python request:
```py
import requests

url = "http://localhost:8191/v1"
headers = {"Content-Type": "application/json"}
data = {
    "cmd": "request.get",
    "url": "http://www.google.com/",
    "maxTimeout": 60000
}
response = requests.post(url, headers=headers, json=data)
print(response.text)
```

Example PowerShell request:
```ps1
$body = @{
    cmd = "request.get"
    url = "http://www.google.com/"
    maxTimeout = 60000
} | ConvertTo-Json

irm -UseBasicParsing 'http://localhost:8191/v1' -Headers @{"Content-Type"="application/json"} -Method Post -Body $body
```

### Commands

#### + `sessions.create`

This will launch a new browser instance which will retain cookies until you destroy it with `sessions.destroy`.
This comes in handy, so you don't have to keep solving challenges over and over and you won't need to keep sending
cookies for the browser to use.

This also speeds up the requests since it won't have to launch a new browser instance for every request.

| Parameter | Notes                                                                                                                                                                                                                                                                                                            |
|-----------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| session   | Optional. The session ID that you want to be assigned to the instance. If isn't set a random UUID will be assigned.                                                                                                                                                                                              |
| proxy     | Optional, default disabled. Eg: `"proxy": {"url": "http://127.0.0.1:8888"}`. You must include the proxy schema in the URL: `http://`, `socks4://` or `socks5://`. Authorization (username/password) is supported. Eg: `"proxy": {"url": "http://127.0.0.1:8888", "username": "testuser", "password": "testpass"}` |

#### + `sessions.list`

Returns a list of all the active sessions. More for debugging if you are curious to see how many sessions are running.
You should always make sure to properly close each session when you are done using them as too many may slow your
computer down.

Example response:

```json
{
  "sessions": [
    "session_id_1",
    "session_id_2",
    "session_id_3..."
  ]
}
```

#### + `sessions.destroy`

This will properly shutdown a browser instance and remove all files associated with it to free up resources for a new
session. When you no longer need to use a session you should make sure to close it.

| Parameter | Notes                                         |
|-----------|-----------------------------------------------|
| session   | The session ID that you want to be destroyed. |

#### + `request.get`

| Parameter           | Notes                                                                                                                                                                                                                                                                                                                                        |
|---------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| url                 | Mandatory                                                                                                                                                                                                                                                                                                                                    |
| session             | Optional. Will send the request from and existing browser instance. If one is not sent it will create a temporary instance that will be destroyed immediately after the request is completed.                                                                                                                                                |
| session_ttl_minutes | Optional. BypassFlare will automatically rotate expired sessions based on the TTL provided in minutes.                                                                                                                                                                                                                                      |
| maxTimeout          | Optional, default value 60000. Max timeout to solve the challenge in milliseconds.                                                                                                                                                                                                                                                           |
| cookies             | Optional. Will be used by the headless browser. Eg: `"cookies": {"name1": "value1", "name2": "value2", "domain": ".exemple.com"}`.                                                                                                                                                                                           |
| returnOnlyCookies   | Optional, default false. Only returns the cookies. Response data, headers and other parts of the response are removed.                                                                                                                                                                                                                       |
| proxy               | Optional, default disabled. Eg: `"proxy": {"url": "http://127.0.0.1:8888"}`. You must include the proxy schema in the URL: `http://`, `socks4://` or `socks5://`. Authorization (username/password) is not supported. (When the `session` parameter is set, the proxy is ignored; a session specific proxy can be set in `sessions.create`.) |

> **Warning**
> If you want to use Cloudflare clearance cookie in your scripts, make sure you use the BypassFlare User-Agent too. If they don't match you will see the challenge.

Example response from running the `curl` above:

```json
{
    "solution": {
        "url": "https://www.google.com/?gws_rd=ssl",
        "status": 200,
        "headers": {
            "status": "200",
            "date": "Thu, 28 Avr 2024 04:15:49 GMT",
            "expires": "-1",
            "cache-control": "private, max-age=0",
            "content-type": "text/html; charset=UTF-8",
            "strict-transport-security": "max-age=31536000",
            "p3p": "CP=\"This is not a P3P policy! See g.co/p3phelp for more info.\"",
            "content-encoding": "br",
            "server": "gws",
            "content-length": "61587",
            "x-xss-protection": "0",
            "x-frame-options": "SAMEORIGIN",
            "set-cookie": "1P_JAR=2020-07-16-04; expires=Sat..."
        },
        "response":"<!DOCTYPE html>...",
        "cookies": [
            {
                "name": "NID",
                "value": "204=QE3Ocq15XalczqjuDy52HeseG3zAZuJzID3R57...",
                "domain": ".google.com",
                "path": "/",
                "expires": 1610684149.307722,
                "size": 178,
                "httpOnly": true,
                "secure": true,
                "session": false,
                "sameSite": "None"
            },
            {
                "name": "1P_JAR",
                "value": "2024-05-16-04",
                "domain": ".google.com",
                "path": "/",
                "expires": 1597464949.307626,
                "size": 19,
                "httpOnly": false,
                "secure": true,
                "session": false,
                "sameSite": "None"
            }
        ],
        "userAgent": "Windows NT 10.0; Win64; x64) AppleWebKit/5..."
    },
    "status": "ok",
    "message": "",
    "startTimestamp": 1594872947467,
    "endTimestamp": 1594872949617,
    "version": "2024.04"
}
```

### + `request.post`

This is the same as `request.get` but it takes one more param:

| Parameter | Notes                                                                    |
|-----------|--------------------------------------------------------------------------|
| postData  | Must be a string with `application/x-www-form-urlencoded`. Eg: `a=b&c=d` |

## Environment variables

| Name               | Default                | Notes                                                                                                                                                         |
|--------------------|------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| LOG_LEVEL          | info                   | Verbosity of the logging. Use `LOG_LEVEL=debug` for more information.                                                                                         |
| LOG_HTML           | false                  | Only for debugging. If `true` all HTML that passes through the proxy will be logged to the console in `debug` level.                                          |
| CAPTCHA_SOLVER     | none                   | Captcha solving method. It is used when a captcha is encountered. See the Captcha Solvers section.                                                            |
| TZ                 | UTC                    | Timezone used in the logs and the web browser. Example: `TZ=Europe/London`.                                                                                   |
| LANG               | none                   | Language used in the web browser. Example: `LANG=en_GB`.                                                                                   |
| HEADLESS           | true                   | Only for debugging. To run the web browser in headless mode or visible.                                                                                       |
| BROWSER_TIMEOUT    | 40000                  | If you are experiencing errors/timeouts because your system is slow, you can try to increase this value. Remember to increase the `maxTimeout` parameter too. |
| TEST_URL           | https://www.google.com | BypassFlare makes a request on start to make sure the web browser is working. You can change that URL if it is blocked in your country.                      |
| PORT               | 8191                   | Listening port. You don't need to change this if you are running on Docker.                                                                                   |
| HOST               | 0.0.0.0                | Listening interface. You don't need to change this if you are running on Docker.                                                                              |
| PROMETHEUS_ENABLED | false                  | Enable Prometheus exporter. See the Prometheus section below.                                                                                                 |
| PROMETHEUS_PORT    | 8192                   | Listening port for Prometheus exporter. See the Prometheus section below.                                                                                     |

Environment variables are set differently depending on the operating system. Some examples:
* Docker: Take a look at the Docker section in this document. Environment variables can be set in the `docker-compose.yml` file or in the Docker CLI command.
* Linux: Run `export LOG_LEVEL=debug` and then run `BypassFlare` in the same shell.
* Windows: Open `cmd.exe`, run `set LOG_LEVEL=debug` and then run `python [path]\src\main.py` in the same shell.

## Prometheus exporter

The Prometheus exporter for BypassFlare is disabled by default. It can be enabled with the environment variable `PROMETHEUS_ENABLED`. If you are using Docker make sure you expose the `PROMETHEUS_PORT`.

Example metrics:
```shell
# HELP bypassflare_request_total Total requests with result
# TYPE bypassflare_request_total counter
bypassflare_request_total{domain="nowsecure.nl",result="solved"} 1.0
# HELP bypassflare_request_created Total requests with result
# TYPE bypassflare_request_created gauge
bypassflare_request_created{domain="nowsecure.nl",result="solved"} 1.690141657157109e+09
# HELP bypassflare_request_duration Request duration in seconds
# TYPE bypassflare_request_duration histogram
bypassflare_request_duration_bucket{domain="nowsecure.nl",le="0.0"} 0.0
bypassflare_request_duration_bucket{domain="nowsecure.nl",le="10.0"} 1.0
bypassflare_request_duration_bucket{domain="nowsecure.nl",le="25.0"} 1.0
bypassflare_request_duration_bucket{domain="nowsecure.nl",le="50.0"} 1.0
bypassflare_request_duration_bucket{domain="nowsecure.nl",le="+Inf"} 1.0
bypassflare_request_duration_count{domain="nowsecure.nl"} 1.0
bypassflare_request_duration_sum{domain="nowsecure.nl"} 5.858
# HELP bypassflare_request_duration_created Request duration in seconds
# TYPE bypassflare_request_duration_created gauge
bypassflare_request_duration_created{domain="nowsecure.nl"} 1.6901416571570296e+09
```
