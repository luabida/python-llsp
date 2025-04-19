def get_version() -> str:
    try:
        return importlib_metadata.version(__name__)
    except importlib_metadata.PackageNotFoundError:  # pragma: no cover
        return "0.1.0"  # changed by semantic-release


__version__: str = get_version()
__all__: List[str] = []  # noqa: WPS410 (the only __variable__ we use)
