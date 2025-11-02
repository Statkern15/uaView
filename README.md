# uaView

A lightweight, terminal-based OPC-UA client for seamless server interaction.

# Introduction

uaView is a lightweight, terminal-based user interface (TUI) designed for seamless interaction with OPC-UA servers. It allows users to connect, browse nodes, and monitor live data efficiently -- all within an intuitive command-line environment.

## Features

- **Easy Connection Management**: Connect to OPC-UA servers via a simple selection interface
- **Project Organization**: Save OPC-UA server configurations for easier project management
- **Address Space Browser**: Browse the server's address space in an intuitive tree-like structure
- **Node Details**: View comprehensive node attributes in a detailed table format
- **Real-time Monitoring**: Subscribe to nodes to view live value updates with timestamps
- **Activity Logging**: Real-time logging of operations and events
- **Dark Mode Support**: Eye-friendly dark mode interface
- **Keyboard Shortcuts**: Navigate efficiently with keyboard-driven controls
- **Cross-Platform**: Works on Linux, macOS, and Windows

## Why uaView?

Having spent a lot of time working with OPC-UA, I was often frustrated by the lack of practical solutions for Linux servers and resource-constrained environments. uaView aims to fill this gap by providing a lightweight, terminal-based alternative to traditional GUI-based OPC-UA clients. It's designed for users who:

- Prefer terminal-based tools for efficiency and simplicity
- Need quick access to OPC-UA server information without heavy GUI overhead
- Want a keyboard-driven interface for faster navigation
- Work in environments where GUI applications aren't practical (SSH sessions, headless servers, containers)
- Require a lightweight solution that doesn't compromise on functionality
- Need to manage multiple server connections across different projects

## Installation

TODO write installation guidelines

## Configuration

### Server Configuration

Server connections are managed through the `uaView/config/settings.json` file. Each server configuration includes connection details and security settings.

#### Example Configuration:

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

#### Configuration Parameters:

- **endpoint_url**: The OPC-UA server endpoint URL (required)
- **security_policy**: Security policy to use (`None`, `Basic256`, `Basic256Sha256`)
- **security_mode**: Security mode (`None`, `Sign`, `SignAndEncrypt`)
- **user_name**: Username for authentication (optional, leave empty for anonymous)
- **password**: Password for authentication (optional, leave empty for anonymous)

### Security Notes

- Store sensitive credentials securely
- Consider using environment variables for production passwords
- For Docker deployments, use Docker secrets for credential management

## Usage

TODO add usage description

### Key Bindings

| Key | Action | Description |
|-----|--------|-------------|
| `Tab` | Next view | Cycle through interface panels |
| `↑/↓` | Navigate | Move through tree/list items |
| `←/→` | Collapse/Expand | Toggle tree nodes |
| `Enter` | Select | Select highlighted item |
| `s` | Subscribe | Subscribe to selected node for live updates |
| `d` | Toggle dark mode | Switch between light/dark themes |
| `q` | Quit | Exit the application |
| `?` | Help | Show command palette |


## Limitations

### Current Known Limitations

- **Historical Data**: No support for historical data access (HA) yet
- **Methods**: Cannot call server methods
- **Write Operations**: Read-only mode - no writing to nodes
- **Event Monitoring**: Event subscriptions not yet implemented
- **Certificate Management**: Limited certificate handling
- **Batch Operations**: Cannot subscribe/unsubscribe multiple nodes at once
- **Export**: No data export functionality


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

For detailed guidelines on contributing, please refer to the [CONTRIBUTING](CONTRIBUTING.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


Made with ❤️ for the OPC UA community