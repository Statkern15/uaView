# Contributing to uaView

Thank you for your interest in contributing to uaView! We welcome contributions from the community and are grateful for your help in making this OPC-UA client better.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Development Guidelines](#development-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Testing](#testing)
- [Documentation](#documentation)




## Development setup

- Clone the repository
- Install the [uv package manager](https://docs.astral.sh/uv/getting-started/installation/); 


## How to Contribute

### Types of Contributions

We welcome several types of contributions:

- **Bug fixes**: Fix issues reported in GitHub Issues
- **Feature additions**: Implement new functionality
- **Documentation improvements**: Enhance docs, comments, or examples
- **Performance optimizations**: Improve speed or memory usage
- **UI/UX improvements**: Enhance the terminal interface
- **Testing**: Add or improve test coverage
- **Configuration examples**: Add more server configuration examples

### Areas Needing Help

Check our current limitations in the [README.md](README.md) for areas where contributions are especially welcome:

- Historical data access (HA)
- Method calling functionality
- Write operations
- Event monitoring
- Certificate management
- Batch operations
- Data export functionality

## Development Guidelines


### Code Organization

The project follows this structure:
```
uaView/
├── main.py              # Main application entry point
├── style.tcss           # Textual CSS styling
├── config/              # Configuration files
├── ua_client/           # OPC-UA client implementation
└── widgets/             # UI widgets and components
```

### Coding Standards

1. **Follow Python conventions**:
   - Use descriptive variable and function names
   - Add docstrings to classes and functions
   - Type hints where appropriate

2. **Async/await patterns**:
   - Use `async def` for I/O operations
   - Properly handle exceptions in async contexts
   - Don't block the event loop

3. **Error handling**:
   - Use try/except blocks for OPC-UA operations
   - Log errors appropriately
   - Graceful degradation when possible

4. **Widget development**:
   - Follow Textual widget patterns
   - Use CSS for styling in [`style.tcss`](uaView/style.tcss)
   - Implement proper event handling

## Issue Guidelines

### Bug Reports

When reporting bugs, please include:

1. **Environment information**:
   - Python version
   - Operating system
   - uaView version

2. **Steps to reproduce**:
   - Exact steps to trigger the bug
   - Expected behavior
   - Actual behavior

3. **Additional context**:
   - Server configuration (sanitized)
   - Error messages or logs
   - Screenshots if applicable

### Feature Requests

For new features:

1. **Use case description**: Why is this feature needed?
2. **Proposed solution**: How should it work?
3. **Alternatives considered**: What other approaches were considered?
4. **Additional context**: Screenshots, mockups, or examples


## Documentation

### Code Documentation

- Add docstrings to all public functions and classes
- Use clear, concise language
- Include parameter and return type information
- Add usage examples where helpful

### README Updates

When adding new features:
- Update the features list in [README.md](README.md)
- Add configuration examples if needed
- Update key bindings table if applicable
- Add to limitations section if introducing known constraints

## Development Tips

### Working with Textual

- Use `textual console` for debugging
- Check the [Textual documentation](https://textual.textualize.io/)
- Test UI changes with different terminal sizes
- Use CSS for consistent styling

### Working with OPC-UA

- Test with multiple server types when possible
- Handle connection failures gracefully
- Be mindful of subscription limits
- Consider security implications


## Questions?

- Open a GitHub issue for bugs or feature requests
- Check existing issues before creating new ones
- Join discussions in existing issues
- Ask questions in issue comments

## Recognition

Contributors will be acknowledged in:
- GitHub contributors list
- Release notes for significant contributions
- Project documentation where appropriate

Thank you for contributing to uaView! 🚀