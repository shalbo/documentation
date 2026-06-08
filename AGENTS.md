# AGENTS.md

## Cursor Cloud specific instructions

This repository is the **Odoo 16.0 documentation** site (Sphinx/reStructuredText). It is not the Odoo ERP application. There is no database, Docker stack, or long-running app server — development means building static HTML and optionally running RST guideline tests.

### Quick reference

| Task | Command |
|------|---------|
| Install deps | See [Dependency installation](#dependency-installation) below |
| Build docs | `make html` (default target: `make`) |
| Fast build | `make fast` |
| Clean build | `make clean` |
| Run tests | `make test` |
| View docs | Open `_build/html/index.html` or serve with `python3 -m http.server 8080` from `_build/html/` |

See `README.md` and `make help` for standard commands.

### Dependency installation

On **Python 3.12+** (common in cloud VMs), a plain `pip install -r requirements.txt -r tests/requirements.txt` may fail:

1. **Pillow 9.0.1** (pinned in `tests/requirements.txt`) has no wheel for Python 3.12. Install a compatible Pillow instead: `pip3 install Pillow` (after other test deps).
2. **sphinxcontrib-\*** packages pulled in by pip may require Sphinx 5+, while this project pins **Sphinx 4.3.2**. Pin older contrib packages after installing `requirements.txt`:

```bash
pip3 install -r requirements.txt
pip3 install 'sphinxcontrib-applehelp==1.0.2' 'sphinxcontrib-devhelp==1.0.2' \
  'sphinxcontrib-qthelp==1.0.3' 'sphinxcontrib-serializinghtml==1.1.5' \
  'sphinxcontrib-htmlhelp==2.0.0'
pip3 install mock==5.0.1 sphinx-lint==0.6.7 Pillow
```

3. Ensure `~/.local/bin` is on `PATH` (where `sphinx-build` is installed via pip).
4. `make test` invokes `python` (not `python3`). Install `python-is-python3` on Debian/Ubuntu if needed.

System packages for building Pillow from source (if required): `libjpeg-dev zlib1g-dev libpng-dev libfreetype6-dev`.

### Optional: full Developer docs with autodoc

Clone the matching Odoo sources so autodoc directives resolve:

```bash
git clone --branch 16.0 --depth 1 https://github.com/odoo/odoo odoo
```

Place the clone at `/workspace/odoo` or `/workspace/../odoo`. Without it, the build still succeeds but Developer API reference pages use placeholders.

### Gotchas

- **`make test` references `content/services`**, which is not present in this checkout. The test runner may warn or skip that path; redirect-rule failures in `redirects/16.0.txt` are known content issues, not environment problems.
- **Graphviz** (`dot`) is optional; without it, diagram directives use a placeholder extension.
- **Build time**: full `make html` takes ~1–2 minutes on a typical cloud VM.
- Re-run `make html` after editing RST under `content/` or theme files under `extensions/odoo_theme/`.
