from anyio import Path


def parse_proxy(
        path: Path
) -> list[str]:
    with open(path, "r") as f:
        try:
            return [line.strip() for line in f if line.strip()]
        except:
            return []
