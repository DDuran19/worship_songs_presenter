# Developer Guide

## Getting Started

### Prerequisites
- Python 3.7+
- Git
- Basic understanding of PyQt5 and Python

### Setting Up the Development Environment
1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd worship_songs_presenter
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

## Code Organization

### Main Components
- `_app.py`: Main application entry point and UI setup
- `lyrics/`: Lyrics processing and management
- `ui/`: UI components and widgets
- `utils/`: Utility functions and helpers

### Code Style
- Follow PEP 8 guidelines
- Use type hints for better code documentation
- Keep functions small and focused
- Write docstrings for all public functions and classes

## Development Workflow

1. Create a new branch for your feature/fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and run tests:
   ```bash
   python -m pytest
   ```

3. Run the linter:
   ```bash
   flake8 .
   ```

4. Commit your changes with a descriptive message:
   ```bash
   git commit -m "Add: New feature description"
   ```

5. Push your changes and create a pull request

## Testing

### Running Tests
```bash
pytest tests/
```

### Writing Tests
- Place test files in the `tests/` directory
- Name test files with `test_` prefix
- Use descriptive test function names starting with `test_`
- Follow the Arrange-Act-Assert pattern

## Documentation

### Updating Documentation
- Update the relevant markdown files in the `docs/` directory
- Keep documentation in sync with code changes
- Add examples for new features

### Building Documentation
```bash
cd docs
make html
```

## Release Process

1. Update version number in `__version__.py`
2. Update `CHANGELOG.md`
3. Create a release tag:
   ```bash
   git tag -a v1.0.0 -m "Version 1.0.0"
   git push origin v1.0.0
   ```
4. Create a GitHub release with release notes

## Contributing

### Bug Reports
- Check existing issues before creating a new one
- Include steps to reproduce the issue
- Add relevant error messages and screenshots if applicable

### Feature Requests
- Explain the problem you're trying to solve
- Describe the proposed solution
- Provide examples if possible

### Pull Requests
- Keep PRs focused on a single feature or fix
- Include tests for new functionality
- Update documentation as needed
- Reference related issues in your PR description
