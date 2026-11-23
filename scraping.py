import re
import cloudscraper
from bs4 import BeautifulSoup

scraper = cloudscraper.create_scraper()

def scrape_fextralife(url: str) -> str:
    response = scraper.get(url, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # clean page title (e.g., "Chimes")
    title_tag = soup.find("h1", id="firstHeading")
    title = " ".join(title_tag.get_text(" ").split()) if title_tag else ""

    # main MediaWiki container used by Fextralife
    main_content = soup.find("div", class_="mw-parser-output") or soup.find("div", id="mw-content-text")
    if not main_content:
        return ""

    # remove TOC, edit boxes, scripts, styles, nav and other unwanted elements
    for tag in main_content(["script", "style", "nav", "aside"]):
        tag.decompose()
    for unwanted in main_content.find_all(["div", "span"], class_=["toc", "mw-editsection", "navbox", "infobox"]):
        unwanted.decompose()

    # mark intentional <br> line breaks
    for br in main_content.find_all("br"):
        br.replace_with(" [[BR]] ")

    # format table rows (cells separated by ' | ')
    for row in main_content.find_all("tr"):
        cells = [" ".join(cell.get_text(" ").split()) for cell in row.find_all(["th", "td"])]
        if any(cells):
            row.replace_with(f" [[BR]] {' | '.join(cells)} [[BR]] ")

    # mark real block boundaries (headings, paragraphs, list items, divs)
    for block in main_content.find_all(["p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "div"]):
        block.insert_before(" [[BR]] ")
        block.insert_after(" [[BR]] ")

    # collapse all raw HTML newlines/tabs/multiple spaces into single spaces
    flat_text = " ".join(main_content.get_text(" ").split())

    # rebuild clean lines only at real block boundaries
    lines = [line.strip() for line in flat_text.split("[[BR]]") if line.strip()]
    clean_text = "\n".join(lines)

    # fix stray spaces before punctuation and inside parentheses
    clean_text = re.sub(r"\s+([.,;:!?])", r"\1", clean_text)
    clean_text = re.sub(r"\(\s+", "(", clean_text)
    clean_text = re.sub(r"\s+\)", ")", clean_text)

    return f"Page: {title}\n{clean_text}" if title else clean_text

# quick test
if __name__ == "__main__":
    url = "https://darksouls2.wiki.fextralife.com/Chimes"
    texto = scrape_fextralife(url)
    print(f"Total de caracteres extraídos: {len(texto)}\n")
    print(texto[:2000])