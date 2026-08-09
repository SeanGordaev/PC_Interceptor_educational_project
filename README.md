# PC Interceptor — Educational Project

A small Python proof-of-concept for learning how keyboard and mouse events can be captured, serialized, transmitted over TCP, and reproduced on another computer.

> [!WARNING]
> **Educational use only.** Run this project only on computers you own or on systems where you have explicit permission to test.  
> The current protocol has **no authentication and no encryption**, so it should not be exposed directly to the public Internet.

## Overview

The project contains two main programs:

- **`Invader.py`** — runs on the controlling computer. It listens for local keyboard and mouse events, starts a TCP server, and sends the captured events to the connected peer.
- **`Victom.py`** — runs on the controlled computer. It connects to the TCP server, receives events, and reproduces them using `pynput`.

The project is intentionally small and focuses on the fundamentals of:

- TCP client/server communication
- packet framing
- keyboard event capture
- mouse movement and click capture
- remote input reproduction
- threads and queues
- configuration through JSON

## How It Works

```text
┌──────────────────────────────┐
│       Controller PC          │
│                              │
│  Keyboard / Mouse            │
│          │                   │
│          ▼                   │
│      Invader.py              │
│          │                   │
│       TCP server             │
└──────────┬───────────────────┘
           │
           │ TCP
           ▼
┌──────────────────────────────┐
│       Controlled PC          │
│                              │
│       Victom.py              │
│          │                   │
│          ▼                   │
│  Keyboard / Mouse control    │
└──────────────────────────────┘
```

`Invader.py` captures input with `pynput`, converts each event into a small packet, and places it in a queue. The main sending loop takes packets from the queue and sends them over a TCP connection.

`Victom.py` receives the framed data, determines the event type, and reproduces the corresponding keyboard or mouse action.

## Supported Events

| Mode | Purpose | Example payload |
|---|---|---|
| `kb` | Keyboard key press | `a`, `Key.enter`, `Key.space` |
| `pos` | Mouse position | `500|300` |
| `click` | Mouse button click | `Button.left` |

Mouse movement packets are rate-limited in the current implementation to roughly one update every `0.03` seconds.

## Packet Format

Each field is sent using a simple length-prefixed format:

```text
[2-byte length][mode][2-byte length][payload]
```

The lengths are unsigned integers encoded in **big-endian** byte order.

For example, a keyboard packet conceptually contains:

```text
[length of "kb"]["kb"][length of key][key]
```

The receiver uses `recv_exact()` to keep reading until the requested number of bytes has been received. This is important because TCP is a byte stream and a single `recv()` call is not guaranteed to return an entire logical packet.

## Project Structure

```text
PC_Interceptor_educational_project/
│
└── src/
    ├── Invader.py
    ├── Victom.py
    └── config.json
```

### `Invader.py`

The controller side of the project.

Responsibilities:

- opens a TCP server socket
- waits for one incoming connection
- listens for keyboard presses
- listens for mouse movement
- listens for mouse clicks
- serializes captured events
- sends events to the connected computer

### `Victom.py`

The controlled side of the project.

Responsibilities:

- connects to the controller over TCP
- receives length-prefixed packets
- distinguishes keyboard, movement, and click events
- reproduces keyboard input
- updates the mouse position
- reproduces mouse clicks

### `config.json`

Contains the host and port used by the program:

```json
{
    "HOST": "192.168.1.50",
    "PORT": 65432
}
```

The meaning of `HOST` depends on which program is running.

For **`Invader.py`**, `HOST` is the address the TCP server binds to. You can normally use the controller computer's LAN address. `0.0.0.0` can also be used to listen on all local IPv4 interfaces.

For **`Victom.py`**, `HOST` must be the reachable IP address of the computer running `Invader.py`.

The `PORT` must match on both computers.

### Same-computer test

For testing both programs on one computer, use:

```json
{
    "HOST": "127.0.0.1",
    "PORT": 65432
}
```

## Requirements

- Python **3.9+**
- [`pynput`](https://pypi.org/project/pynput/)
- Two computers on a reachable network, or one computer for localhost testing

Install the external dependency with:

```bash
python -m pip install pynput
```

## Installation

Clone the repository:

```bash
git clone https://github.com/SeanGordaev/PC_Interceptor_educational_project.git
cd PC_Interceptor_educational_project
```

Optional but recommended: create a virtual environment.

### Windows

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install pynput
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install pynput
```

Input-control permissions and `pynput` behavior may differ between operating systems and desktop environments.

## Running the Project

### 1. Configure the controller

On the computer that will run `Invader.py`, edit:

```text
src/config.json
```

Set `HOST` to an address the server can bind to and choose a port.

### 2. Start the controller

```bash
python src/Invader.py
```

The program creates the TCP server and waits for a connection.

### 3. Configure the controlled computer

On the second computer, set `HOST` in its copy of `src/config.json` to the IP address of the controller computer.

Use the same `PORT`.

### 4. Start the controlled side

```bash
python src/Victom.py
```

After the connection is established, supported keyboard and mouse events from the controller are forwarded to the controlled computer.

## Current Limitations

This repository is a learning project rather than production-ready remote desktop software.

Current limitations include:

- one TCP client at a time
- no authentication
- no encryption/TLS
- no integrity protection
- no automatic reconnection
- no graphical interface
- no screen/video streaming
- keyboard events are reproduced as short press/release actions rather than exact key-hold timing
- basic custom protocol without versioning
- configuration is edited manually

Because there is currently no authentication or encryption, **do not port-forward this service or expose it directly to the Internet**.

## Possible Improvements

Some useful next steps for studying networking and software design would be:

- add a `requirements.txt`
- add graceful connection shutdown
- add reconnect handling
- add protocol versioning
- distinguish key-down and key-up events
- improve mouse movement handling
- add structured logging
- add authenticated peers
- add encrypted transport
- separate networking, protocol, and input-handling logic into modules
- add unit tests for packet encoding/decoding

## Educational Goals

This project can be used to study several important concepts:

1. **TCP is a stream, not a message protocol**  
   Applications need their own framing mechanism to determine where one message ends and another begins.

2. **Input events need serialization**  
   Keyboard keys, coordinates, and mouse buttons must be converted into a representation that can be transmitted.

3. **Network code must handle partial reads**  
   Receiving exactly N bytes may require multiple calls to `recv()`.

4. **Input capture and networking are separate jobs**  
   Threads and queues allow event collection and network transmission to be decoupled.

5. **Remote-control software requires strong security controls**  
   Authentication, encryption, authorization, and safe network exposure become essential outside a controlled experiment.

## Legal and Ethical Notice

This repository is intended for education, experimentation, and authorized testing.

Do not use it to control, monitor, or interfere with a computer without the owner's explicit permission. Users are responsible for complying with applicable laws, policies, and network rules.

## License

This project is licensed under the MIT License.

See the [LICENSE](LICENSE) file for details.
