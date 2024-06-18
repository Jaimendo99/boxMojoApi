import httpx
from utils.utils import get_last_friday
from routes.topweek import get_top_week
from routes.search_movies import search_movie_title
from routes.weekly_gross import get_weekly_by_id
from fastapi import FastAPI
from routes.total_weekly_gross import read_data, write_data, update_data,  get_multi_week_grosses, parse_responses
import asyncio

app = FastAPI()


@app.get("/weeklytop/")
async def weekly_top(week: str = get_last_friday(), top: int = 10):
    return get_top_week(week, top)


@app.get("/search/{query_title}")
async def search_movie(query_title: str):
    return search_movie_title(query_title)


@app.get("/weeklyhistory/{id}")
async def weekly_history(id: str):
    return get_weekly_by_id(id)


@app.get("/historicweekly/")
async def historic_weekly():
    data = read_data()
    if not data:
        print("Data not found / Data lacks data , updating...")
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, read=30.0, write=30.0, connect=30.0)
        ) as client:
            responses = await get_multi_week_grosses(
                client, ["2019", "2020", "2021", "2023", "2024", ])
            data = parse_responses(responses)
            write_data(data)
    await update_data(data)
    return read_data()
