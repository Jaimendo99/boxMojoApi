
import json
import numpy as np
import httpx
import pandas as pd
from datetime import datetime
from utils.utils import parse_gross
from io import StringIO
import asyncio


baseUrl = "https://www.boxofficemojo.com/"


async def get_gross(client: httpx.AsyncClient, year: str, week: str):
    endpoint = f"weekly/{year}W{week}/"
    url = baseUrl + endpoint
    return week, await client.get(url)


async def get_week_grosses(client: httpx.AsyncClient, year: str):
    weeks = [str(i).zfill(2) for i in range(1, 53)]
    if int(year) == datetime.now().year:
        weeks = weeks[:datetime.now().isocalendar()[1]-2]

    tasks = [get_gross(client, year, w) for w in weeks]
    return year, await asyncio.gather(*tasks)


async def get_multi_week_grosses(client: httpx.AsyncClient, years: list):
    tasks = [get_week_grosses(client, year) for year in years]
    return await asyncio.gather(*tasks)


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


def parse_responses(responses):
    data = []
    for res in responses:
        year = res[0]
        for r in res[1]:
            week = r[0]
            try:
                table = pd.read_html(StringIO(r[1].text))[0]
            except:
                print(f"Error in {year}W{week}")
                data.append({
                    "Year": year,
                    "Week": week,
                    "total_gross": 0,
                    "top5_gross": 0,
                    "others_gross": 0
                })
            table_small = table.loc[:, ["Rank", "Release", "Gross"]]
            table_small["Gross"] = table_small["Gross"].apply(parse_gross)
            total_gross = table_small["Gross"].sum()
            top5_gross = table_small.head(5)
            others_gross = total_gross - top5_gross['Gross'].sum()
            top5_gross_dict = top5_gross.to_dict(orient='records')
            data.append({
                "year": year,
                "week": week,
                "total_gross": total_gross,
                "others_gross": others_gross,
                "top5_gross": top5_gross_dict
            })

    return data


def read_data():
    try:
        with open('data.json', 'r+') as f:
            data = json.load(f)
        if len(data) < 200:
            print("Data lacks data")
            return False
        print("Data found")
        return data
    except:
        print("Data not found")
        return False


def write_data(data):
    with open('data.json', 'w') as f:
        json.dump(data, f, cls=NpEncoder)


async def update_data(data: dict):

    last_week = data[-1]['week']
    actualweek = datetime.now().isocalendar()[1]

    if last_week != actualweek - 1:
        res = await get_gross(httpx.AsyncClient(), str(datetime.now().year), str(actualweek - 1))
        try:
            table = pd.read_html(StringIO(res))[0]
        except:
            return False

        table_small = table.loc[:, ["Rank", "Release", "Gross"]]
        table_small["Gross"] = table_small["Gross"].apply(parse_gross)
        total_gross = table_small["Gross"].sum()
        top5_gross = table_small.head(5)
        others_gross = total_gross - top5_gross['Gross'].sum()
        top5_gross_dict = top5_gross.to_dict(orient='records')
        data.append({
            "year": str(datetime.now().year),
            "week": str(actualweek - 1),
            "total_gross": total_gross,
            "others_gross": others_gross,
            "top5_gross": top5_gross_dict
        })

        write_data(data)

        return True

    return False
