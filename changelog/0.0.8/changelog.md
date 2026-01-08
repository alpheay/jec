# Changelog 0.0.8

## Refactoring
- **Decorators Modularization**: Refactored `src/jec_api/decorators.py` into a modular package structure at `src/jec_api/decorator/`.
    - Split monolithic file into dedicated modules: `auth.py`, `log.py`, `speed.py`, `version.py`, and `utils.py`.
    - Maintained backward compatibility by exporting all decorators in `src/jec_api/decorator/__init__.py`.
    - Updated top-level `jec_api` package to export `auth` decorator directly.

## Testing
- **Comprehensive Test Suite**: Added `test/0.0.8/feat_test.py` covering all decorator functionalities.
    - **Auth**: Verified public/private access, role-based strictness, and token validation logic.
    - **Log**: Verified request logging and error propagation.
    - **Speed**: Verified performance timing logging.
    - **Version**: Verified API version constraint logic (`>=`, `==`, `<`, etc.) and header requirements.
    - **Combination**: Verified behavior when multiple decorators are stacked on a single endpoint.
