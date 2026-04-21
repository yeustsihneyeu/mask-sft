from pathlib import Path


def project_root(current_file: str | Path = __file__) -> Path:
    return Path(current_file).resolve().parent.parent


def data_path(*parts: str) -> Path:
    return project_root() / "data" / Path(*parts)


def report_path(*parts: str) -> Path:
    return project_root() / "reports" / Path(*parts)
