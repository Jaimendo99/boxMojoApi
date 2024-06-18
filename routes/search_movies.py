import httpx
from bs4 import BeautifulSoup as bs


def search_movie_title(query: str) -> dict:
    soup = query_movies(query)
    return get_movie_data(soup)


def query_movies(query: str) -> bs:
    url = "https://www.boxofficemojo.com/search/"
    params = {"q": query}
    res = httpx.get(url, params=params)
    res.raise_for_status()
    return bs(res.text, "html.parser")


def get_movie_data(soup: bs) -> dict:

    header = soup.select(
        "div.a-fixed-left-grid-inner div.a-fixed-left-grid-col")
    # title
    title_ls = soup.select(
        "div.a-fixed-left-grid-inner div.a-fixed-left-grid-col a.a-size-medium")
    titles = [title.text for title in title_ls]

    # titleId
    titlesIds = [title["href"].split("/")[2] for title in title_ls]

    # year
    years = [header[soupd].select("span.a-color-secondary")[0].text[2:-1]
             for soupd in range(1, len(header), 2)]

    # img
    imgs = [header[img].select("a img")[0]['src']
            for img in range(0, len(header), 2)]

    # genres
    genres = []
    for genre in soup.find_all("div", class_="a-fixed-left-grid-col a-col-right"):
        try:
            genres.append(genre.contents[3].split(" "))
        except IndexError:
            genres.append([])

    # actors
    actors = []
    for h in range(1, len(header), 2):
        try:
            actors.append(header[h].select(
                "span.a-color-secondary")[1].text.split(", "))
        except IndexError:
            actors.append([])

    movies_q = []
    for title, titleId, year, actor, img, genre in zip(titles, titlesIds, years, actors, imgs, genres):
        movies_q.append({"title": title, "titleId": titleId,
                        "year": year, "actors": actor, "img": img, "genres": genre})

    return movies_q
