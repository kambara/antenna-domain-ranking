import re
from typing import List

import pandas as pd
import requests
from tld import get_fld

import favicon


def main():
    src_df = pd.read_csv("data.csv")
    domains = extract_domains(src_df)
    for domain in domains:
        domain = remove_wildcard(domain)
        icon = find_favicon(domain)
        if icon:
            print(icon)
            download_favicon(icon, f"./favicon_ico/{domain}.ico")
        else:
            print("!! Not found")


def extract_domains(df: pd.DataFrame) -> List[str]:
    domains = pd.Series(dtype="object")
    for year in df:
        domains = pd.concat([domains, df[year].dropna()])
    return domains.unique().tolist()


def find_favicon(domain: str):
    # HTTPS
    icon = get_ico(f"https://{domain}/")
    if icon is not None:
        return icon
    # HTTP
    icon = get_ico(f"http://{domain}/")
    if icon is not None:
        return icon
    # First level domain
    fld = get_fld(f"http://{domain}")
    if fld == domain:
        return
    # HTTPS
    icon = get_ico(f"https://{fld}/")
    if icon is not None:
        return icon
    # HTTP
    icon = get_ico(f"http://{fld}/")
    if icon is not None:
        return icon
    return None


def get_ico(url: str):
    # print("  Find:", url)
    try:
        icons = favicon.get(url, timeout=5)
    except Exception:
        return None
    for icon in icons:
        match = re.search(r"\.ico$", icon.url)
        if icon.format == "ico" and match:
            return icon.url
    return None


def remove_wildcard(domain: str) -> str:
    match = re.search(r"\*\.(.+)$", domain)
    if match:
        return match[1]
    return domain


def download_favicon(favicon_url: str, file: str):
    response = requests.get(favicon_url, stream=True)
    with open(file, "wb") as image:
        for chunk in response.iter_content(1024):
            image.write(chunk)


main()
