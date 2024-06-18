# https://www.boxofficemojo.com/date/2024-05-10/weekly/
import pandas as pd
from bs4 import BeautifulSoup as bs4
import httpx
from io import StringIO
from utils.utils import parse_gross


def get_top_week(week: str, top: int = 10) -> dict:
    url = f"https://www.boxofficemojo.com/date/{week}/weekly/"
    table, soup = get_top_week_html(url)
    week = soup.select("th a")[0]['href'][6:16]
    rlids, movie_titles = get_rlids(soup, top)
    grosses = get_parsed_table(table, rlids, movie_titles,  top)
    data = get_data(grosses, week)
    return data


def get_top_week_html(url: str):
    res = httpx.get(url)
    res.raise_for_status()
    soup = bs4(res.text, "html.parser")
    table = pd.read_html(StringIO(res.text))[0]
    return table, soup


def get_rlids(soup: bs4, top: int = 10):
    movies_urls = soup.select("td a", {"rowspan": "7"})

    movie_titles = pd.Series(
        [element.text for element in soup.select("td a h3")][:top])
    rlids = pd.Series(
        [actual_urls['href']
            for actual_urls in movies_urls if actual_urls["href"].startswith("/")][:top]
    ).str.extract(r"(\/release\/)(.*)(\/\?.*)")[1]
    return rlids, movie_titles


def get_parsed_table(table: pd.DataFrame, rlids: pd.Series, movie_titles: pd.Series, top: int) -> pd.DataFrame:
    table = table.loc[table['Rank'] < top+1]
    table = table.drop_duplicates(
        subset="Release", keep="first").reset_index(drop=True)
    table["rlid"] = rlids
    table['title'] = movie_titles
    return pd.concat([table.iloc[:, [1, -1, -2]], table.iloc[:, 3:10].apply(lambda x: x.apply(parse_gross))], axis=1)


def get_data(grosses: pd.DataFrame, week) -> dict:
    data = {
        "week": week,
        "movies": []
    }
    for _, column in grosses.iterrows():
        data["movies"].append({
            "movieName": column["title"],
            "domesticRealese": column["rlid"],
            "weeklyGross": list(column[3:10].values)
        })
    return data
