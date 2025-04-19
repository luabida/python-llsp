def get_version() -> str:
    try:
        return importlib_metadata.version(__name__)
    except importlib_metadata.PackageNotFoundError:  # pragma: no cover
        return "1.0.1"  # changed by semantic-release


__version__: str = get_version()
