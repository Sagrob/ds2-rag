import cloudscraper
from bs4 import BeautifulSoup

scraper = cloudscraper.create_scraper()

def scrape_fextralife(url: str) -> str:
    response = scraper.get(url, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # clean page title (e.g., "Chimes")
    title_tag = soup.find("h1", id="firstHeading")
    title = title_tag.get_text(strip=True) if title_tag else ""

    # main MediaWiki container used by Fextralife
    main_content = soup.find("div", class_="mw-parser-output") or soup.find("div", id="mw-content-text")
    if not main_content:
        return ""

    # remove (TOC), edit boxes, scripts, styles, nav and other unwanted elements
    for tag in main_content(["script", "style", "nav", "aside"]):
        tag.decompose()
    for unwanted in main_content.find_all(["div", "span"], class_=["toc", "mw-editsection", "navbox", "infobox"]):
        unwanted.decompose()

    lines = [line.strip() for line in main_content.get_text(separator="\n").splitlines() if line.strip()]
    clean_text = "\n".join(lines)

    return f"Page: {title}\n{clean_text}" if title else clean_text

# quick test
if __name__ == "__main__":
    url = "https://darksouls2.wiki.fextralife.com/Chimes"
    texto = scrape_fextralife(url)
    print(f"Total de caracteres extraídos: {len(texto)}\n")
    print(texto[:2000])