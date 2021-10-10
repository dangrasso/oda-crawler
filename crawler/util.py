from urllib.parse import urlparse, urljoin


def get_base_url(url: str) -> str:
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"


def to_absolute_url(base_url: str, url: str) -> str:
    if url.startswith("http"):
        return url
    return urljoin(base_url, url)
