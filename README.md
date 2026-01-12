# uaView

A lightweight, terminal-based OPC-UA client for seamless server interaction.

---

## Introduction

uaView is a lightweight, terminal-based user interface (TUI) designed for efficient interaction with OPC-UA servers. It allows users to connect, browse nodes, and monitor live data in real-time — all within an intuitive command-line environment.

### Features

* **Easy Connection Management**: Quickly connect to OPC-UA servers via a simple selection interface.
* **Project Organization**: Save server configurations for better project management.
* **Address Space Browser**: Navigate the server's address space in a tree-like structure.
* **Node Details**: View comprehensive node attributes in a structured table format.
* **Real-time Monitoring**: Subscribe to nodes to see live value updates with timestamps.
* **Activity Logging**: Monitor operations and events in real-time.
* **Dark Mode Support**: Eye-friendly interface for long sessions.
* **Keyboard Shortcuts**: Navigate efficiently using keyboard-driven controls.
* **Cross-Platform**: Compatible with Linux, macOS, and Windows.

### Why uaView?

uaView addresses the need for a lightweight, terminal-based OPC-UA client, especially useful for:

* Terminal-focused workflows (SSH, headless servers, containers)
* Quick access to server information without GUI overhead
* Keyboard-driven navigation for faster operation
* Managing multiple server connections across projects
* Resource-constrained environments

---

## Installation

uaView can be run via **Docker** or **Docker Compose**. By default, the application looks for `settings.json` inside the container at `/app/config/settings.json`. Using the `UAVIEW_SETTINGS` environment variable is optional and only needed if you want to load the settings from a different path.

### 1. Docker Run (Default Way)

Run the container using the **default internal settings path**:

```bash
docker run -it \
  --name uaview \
  -v <HOST_PATH_TO_SETTINGS_JSON>:/app/config/settings.json \
  uaview_local:0.0.1 \
  bash
```

* The app automatically loads `/app/config/settings.json` inside the container.
* No `UAVIEW_SETTINGS` environment variable is required.
* Replace `<HOST_PATH_TO_SETTINGS_JSON>` with the path to your local `settings.json`.

**Optional:** To use a custom path for the settings file, set the `UAVIEW_SETTINGS` environment variable:

```bash
docker run -it \
  --name uaview \
  -e UAVIEW_SETTINGS=/custom/path/settings.json \
  -v /home/user/custom_settings.json:/custom/path/settings.json \
  uaview_local:0.0.1 \
  bash
```

#### Common Error: Container Name Conflict

If you see the following error:

```
docker: Error response from daemon: Conflict. The container name "/uaview" is already in use by container "<container_id>". You have to remove (or rename) that container to be able to reuse that name.
```

**Solution:**

* Remove the old container:

```bash
docker rm uaview
```

* Or use a different container name:

```bash
docker run -it --name uaview_test ...
```

* **Alternatively**, use the `--rm` option to automatically remove the container when it exits, avoiding conflicts:

```bash
docker run --rm -it \
  -e UAVIEW_SETTINGS=/app/config/settings.json \
  -v /home/user/uaview_test/settings.json:/app/config/settings.json \
  uaview_local:0.0.1 \
  bash
```

This is recommended for temporary or interactive use.

### 2. Docker Compose (Default Way)

```yaml
version: "3.9"
services:
  uaview:
    image: uaview_local:0.0.1
    container_name: uaview
    volumes:
      - <HOST_PATH_TO_SETTINGS_JSON>:/app/config/settings.json
    tty: true
    stdin_open: true
```

**Optional:** To override with a custom settings path, add:

```yaml
    environment:
      - UAVIEW_SETTINGS=/custom/path/settings.json
```

Usage:

1. Save as `docker-compose.yml`.
2. Run `docker-compose up`.
3. Enter the container shell with `docker exec -it uaview bash`.

### Notes

* Ensure the host path to `settings.json` is **absolute**, e.g., `/home/user/uaview/settings.json`.
* The default internal path inside the container is `/app/config/settings.json`.
* Using Docker Compose is recommended for reproducible deployments or multi-container setups.
* Using `--rm` with `docker run` avoids container name conflicts for interactive sessions.

---

## Configuration

Server connections are configured in `uaView/config/settings.json`.

### Example Configuration

```json
{
  "Local Test Server": {
    "endpoint_url": "opc.tcp://localhost:4840/freeopcua/server/",
    "security_policy": "None",
    "security_mode": "None",
    "user_name": "",
    "password": ""
  },
  "Production Server": {
    "endpoint_url": "opc.tcp://192.168.1.100:4840/UA/ProductionServer",
    "security_policy": "Basic256Sha256",
    "security_mode": "SignAndEncrypt",
    "user_name": "admin",
    "password": "secure_password"
  },
  "Cloud Server": {
    "endpoint_url": "opc.tcp://cloud.example.com:4840/",
    "security_policy": "Basic256Sha256",
    "security_mode": "Sign",
    "user_name": "readonly_user",
    "password": "view_only_pass"
  }
}
```

**Parameters:**

* `endpoint_url`: OPC-UA server endpoint URL.
* `security_policy`: Security policy (`None`, `Basic256`, `Basic256Sha256`).
* `security_mode`: Security mode (`None`, `Sign`, `SignAndEncrypt`).
* `user_name` / `password`: Optional credentials; leave empty for anonymous access.

**Security Tips:**

* Store sensitive credentials securely.
* Use environment variables or Docker secrets for production.

---

## Usage

### Key Bindings

| Key     | Action           | Description                        |
| ------- | ---------------- | ---------------------------------- |
| `Tab`   | Next view        | Cycle through interface panels     |
| `↑/↓`   | Navigate         | Move through tree/list items       |
| `←/→`   | Collapse/Expand  | Toggle tree nodes                  |
| `Enter` | Select           | Select highlighted item            |
| `s`     | Subscribe        | Subscribe to node for live updates |
| `d`     | Toggle dark mode | Switch light/dark theme            |
| `q`     | Quit             | Exit the application               |
| `?`     | Help             | Show command palette               |

---

## Limitations

* **Historical Data**: Not yet supported.
* **Methods**: Cannot invoke server methods.
* **Write Operations**: Read-only mode.
* **Event Monitoring**: Event subscriptions not implemented.
* **Certificate Management**: Limited support.
* **Batch Operations**: No bulk subscribe/unsubscribe.
* **Export**: Data export not yet available.

---

## Contributing

Contributions are welcome! Submit a Pull Request or open an issue for discussion. See [CONTRIBUTING](CONTRIBUTING.md) for details.

## License

Licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

Made with ❤️ for the OPC UA community.
