# Contributing to llm-wiki-skill

Thank you for your interest in contributing. Here's everything you need to get started.

## Getting Started

1. Fork the repository and clone your fork
2. Create a new branch from `main`: `git checkout -b feat/your-feature`
3. Make your changes, then open a Pull Request

## Branch Naming

| Prefix | Use case |
|--------|----------|
| `feat/` | New features |
| `fix/` | Bug fixes |
| `docs/` | Documentation only |
| `refactor/` | Code refactoring without behavior change |
| `chore/` | Maintenance tasks |

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add xlsx extraction support
fix: handle empty wiki index gracefully
docs: update quick start example
```

## Code Style

**Python**
- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use type hints for all function signatures
- Docstrings for public functions (Google style)
- Max line length: 100 characters

**Markdown**
- Use ATX-style headers (`#`, `##`, etc.)
- Wrap lines at 120 characters where possible
- Spell-check before submitting

## Pull Request Guidelines

- Keep PRs focused — one feature or fix per PR
- Include a clear description of what changed and why
- Reference any related issues: `Closes #123`
- Ensure all existing functionality still works before submitting
- Add or update documentation if your change affects user-facing behavior

## Reporting Issues

When filing a bug report, please include:
- A clear, descriptive title
- Steps to reproduce
- Expected vs. actual behavior
- Environment details (OS, Python version, Claude model)

For feature requests, describe the use case and why it would benefit other users.

## Questions

Open a [GitHub Discussion](../../discussions) for general questions rather than filing an issue.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
