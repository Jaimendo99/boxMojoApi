import httpx
from bs4 import BeautifulSoup as bs
import pandas as pd
from datetime import timedelta
import io
from utils.utils import parse_gross, parse_date_range

base_url = 'https://www.boxofficemojo.com/'


def get_weekly_data(soup: bs, id):
    domestic, international, worldwide = tuple([
        parse_gross(item.text) for item in soup.select("div.mojo-performance-summary-table div.a-section span.money")])

    years = [item['href'].split('/')[2][:4] for item in soup.select("td a")]
    data = pd.read_html(io.StringIO(str(soup)))
    table = data[0].loc[:, [
        'Date',
        'Rank',
        'Weekly',
        'Week'
    ]]
    table['Date'] = table['Date'] + ' ' + years
    print(table['Date'])

    startWeekDate = generate_weekly_dates(table['Date'].iloc[0], len(table))

    table['WeekStart'] = startWeekDate

    table.drop(columns=['Date'], inplace=True)
    table['Weekly'] = table['Weekly'].apply(parse_gross)

    return {
        'domesticRealese': id,
        'sumGross': {
            'domestic': domestic,
            'international': international,
            'worldwide': worldwide
        },
        'weekly': table.to_dict(orient='records')
    }


def fetch_data(url: str):
    print(url)
    res = httpx.get(url)
    res.raise_for_status()
    return res.text


def get_rlis(soup: bs):
    return soup.select("table")[0].select_one("td a")['href'].split('/')[2]


def get_weekly_by_id(id: str):
    if id.startswith("tt"):
        html = fetch_data(f"{base_url}title/{id}/")
        soup = bs(html, "html.parser")
        rsid = get_rlis(soup)

        if rsid.startswith("rl"):
            dataa = fetch_data(f"{base_url}release/{rsid}/weekly/")
            print("rlis", rsid)
        else:
            grid_res = fetch_data(f"{base_url}releasegroup/{rsid}/")
            soup = bs(grid_res, 'html.parser')
            rsid = [x for x in soup.find_all(
                'option') if x.text == 'Domestic'][0]['value'].split('/')[-2]
            print("rlis", rsid)
            dataa = fetch_data(f"{base_url}release/{rsid}/weekly/")

        return get_weekly_data(bs(dataa, 'html.parser'), rsid)

    elif id.startswith("rl"):
        html = fetch_data(f"{base_url}release/{id}/weekly/")
        soup = bs(html, "html.parser")
        return get_weekly_data(soup, id)

    else:
        return {"error": "Invalid id"}


def generate_weekly_dates(start_date_str, num_weeks):

    # Parse the first date
    start_date, end_date = parse_date_range(start_date_str)
    print(start_date)
    dates = []

    for i in range(num_weeks):
        week_start = start_date + timedelta(weeks=i)
        week_end = week_start + timedelta(days=6)
        dates.append(f"{week_start.strftime('%b %d %Y')}")

    return dates
