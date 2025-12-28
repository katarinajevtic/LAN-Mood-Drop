# LAN Mood Drop

### LAN Mood Drop is a lightweight TCP client–server application for real-time message exchange and mood tracking within a local network.
## Features

- TCP client–server architecture
- Multiple simultaneous clients
- Real-time message broadcasting
- Per-client mood state
- Mood statistics aggregation
- On-demand message history
- Runtime commands over TCP

---

## Supported Commands

| Command        | Description |
|---------------|-------------|
| `/mood <type>` | Change current mood (`happy`, `tired`, `angry`, `focused`) |
| `/users`       | List all connected clients |
| `/stats`       | Show mood statistics |
| `/history`     | Display recent message history |
| `exit`         | Disconnect client |

---

## Technologies Used

- Python 3
- `socket` (TCP)
- `threading`
- JSON-based configuration

---
## Configuration

Network parameters are defined in `config.json`
## How to Run
### 1. Start the server
```
python server.py
```
### 2. Start one or more clients
```
python client.py
```
To connect from another machine in the same LAN, update server_ip
in config.json to the server’s local IP address.
## License
This project is licensed under the MIT License. See the [LICENCE](https://github.com/git/git-scm.com/blob/main/MIT-LICENSE.txt) file for more details.
