import asyncio
from playwright.async_api import Page, async_playwright, Playwright
from bs4 import BeautifulSoup
from json import loads
import re as regex
import requests


def split_lyrics(lyrics: str):
    return lyrics.split("\n")


async def run(playwright: Playwright):

    async def send_message(msg: str, page: Page):
        message_input = await page.query_selector("#c-input")
        assert message_input
        await message_input.fill(msg, timeout=0, force=True)
        await page.keyboard.press("Enter")

    chromium = playwright.chromium
    browser = await chromium.launch_persistent_context(
        user_data_dir="resources/tmp",
        headless=False,
    )
    page = await browser.new_page()
    await page.goto("https://aternos.org/console/")
    arr = ["sim"]
    for _i in range(0, 10):
        for j in range(0, len(arr) - 1):
            await send_message(f"tell LucasHype {arr[j]}", page)
    await page.wait_for_timeout(1000000)


song_name_search_url = "https://cse.google.com/cse/element/v1?num=1&cx=partner-pub-9911820215479768%3A4038644078&callback=google.search.cse.api6519"

cse_token_generator_url = (
    "https://cse.google.com/cse.js?cx=partner-pub-9911820215479768:4038644078"
)


async def generate_cse_token() -> str:
    cse_token_content = str(requests.get(cse_token_generator_url).content)
    cse_token_regex = regex.compile('(?<="cse_token": )"[^"]*"')
    cse_token = str(cse_token_regex.findall(cse_token_content)[0])
    cse_token = cse_token.replace('"', "")
    return cse_token


async def search_lyrics(query: str, result_index: int = 0) -> str:

    lyrics_url = await search_lyrics_url(query, result_index)
    lyrics_url = lyrics_url.replace("/traducao.html", "")
    lyrics_html = requests.get(lyrics_url).content.decode()
    lyrics_soup = BeautifulSoup(lyrics_html, "html.parser")
    lyrics_div = lyrics_soup.find(class_="lyric-original")
    lyrics = ""
    for content in lyrics_div.contents:  # type: ignore
        lyrics += (
            f"{content}".replace("<br/>", "\n")
            .replace("<p>", "\n\n")
            .replace("</p>", "")
        )

    return lyrics


async def search_lyrics_url(query: str, result_index: int = 0) -> str:
    cse_token = await generate_cse_token()
    query_url = f"{song_name_search_url}&q={query}&cse_tok={cse_token}"

    raw_json = requests.get(query_url).content.decode()
    raw_json = raw_json.split("\n", 2)[2]  # removing google api header
    raw_json = raw_json[:-2]
    raw_json = "{" + raw_json
    json = loads(raw_json)
    return json["results"][result_index]["url"]


async def main():
    await run_playwright()


async def run_playwright():
    lyrics = await search_lyrics("")
    print(lyrics)
    # async with async_playwright() as playwright:
    #     await run(playwright)


asyncio.run(main())
