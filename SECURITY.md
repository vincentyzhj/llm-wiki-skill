# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| latest (`main`) | ✅ |
| older branches | ❌ |

We only provide security fixes for the latest version on `main`.

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability, report it privately via one of the following:

- **GitHub Private Vulnerability Reporting**: Use the [Security tab](../../security/advisories/new) in this repository (preferred)
- **Email**: Contact the maintainer at the email address listed on the [llmrix GitHub profile](https://github.com/llmrix)

### What to Include

Please provide as much of the following as possible:

- Type of vulnerability (e.g., path traversal, code injection, data exposure)
- File(s) and line number(s) involved
- Step-by-step reproduction instructions
- Proof-of-concept or exploit code (if available)
- Potential impact assessment

### Response Timeline

| Stage | Target |
|-------|--------|
| Acknowledgement | Within 48 hours |
| Initial assessment | Within 7 days |
| Fix or mitigation | Within 30 days (depending on severity) |
| Public disclosure | Coordinated with reporter after fix is released |

We follow responsible disclosure. We ask that you give us reasonable time to address the issue before any public disclosure.

## Scope

The following are in scope:

- Code execution vulnerabilities in Python scripts
- Path traversal or arbitrary file read/write in wiki workspace handling
- Prompt injection risks in LLM-facing inputs
- Dependency vulnerabilities in bundled third-party code

The following are out of scope:

- Vulnerabilities in third-party dependencies (report those upstream)
- Issues requiring physical access to the machine
- Social engineering attacks

## Security Best Practices for Users

- Do not ingest documents from untrusted sources without review
- Keep your Python dependencies up to date
- Restrict wiki workspace paths to non-sensitive directories
- Review generated wiki content before sharing externally

## Credits

We appreciate responsible disclosure and will acknowledge reporters in the release notes (with permission).
