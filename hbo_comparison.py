import requests
import pandas as pd
import plotly.plotly as py
import plotly.graph_objs as go
import math

#wikipedia table web scraper
def wiki_table_generator(url):
    response = requests.get(url)
    i = 0
    df = pd.read_html(response.content)[i]
    while True:
        yield df
        i += 1
        df = pd.read_html(response.content)[i]

def get_data(url, seasons):
    generator = wiki_table_generator(url)
    throw_away = generator.__next__()
    df = generator.__next__()
    df.columns = df.iloc[0]
    df = df.ix[1:].reset_index()
    for i in range(1,seasons+1):
        next_season = generator.__next__()
        next_season.columns = next_season.iloc[0]
        next_season = next_season.ix[1:].reset_index()
        df = df.append(next_season)

    if url == "https://en.wikipedia.org/wiki/List_of_Silicon_Valley_episodes":
        df = df.ix[df['No. overall'].isin([str(x) for x in range(0,100)])]
    return(df)

def prep_data(df,index):
    df = df.reset_index()
    df['date'] = [x[-11:-1] for x in df['Original air date']]
    df.index = df['date']
    new_index = list(set(index).difference(set(df.date)))
    df = df.loc[df.index.tolist() + new_index]
    df['U.S. viewers (millions)'] = ["0.00" if isinstance(x,float) else x[:4] for x in df['U.S. viewers (millions)']]
    return(df)

def graph(game_of_thrones,silicon_valley):
    got = go.Scatter(
        x=game_of_thrones['date'], # assign x as the dataframe column 'x'
        y=game_of_thrones['U.S. viewers (millions)'],
        name= "Game of Thrones"
    )

    sv = go.Scatter(
        x=silicon_valley['date'], # assign x as the dataframe column 'x'
        y=silicon_valley['U.S. viewers (millions)'],
        name= "Silicon Valley"
    )


    decision_boundary = go.Scatter(
        x=['2016-04-01'],
        y=[5],
        text=['Without Game of Thrones'],
        mode='text',
        name="Without Game of Thrones"
    )

    data = [got,sv, decision_boundary]

    layout = {
        'title':'Silicon Valley ratings with and without Game of Thrones',

        'xaxis': {
            'title': "Date",
            'titlefont': dict(
                family='Courier New, monospace',
                size=18,
                color='#7f7f7f'
            )
        },
        'yaxis': {
            'title': 'Number of Viewers (in millions)',
            'titlefont': dict(
                family='Courier New, monospace',
                size=18,
                color='#7f7f7f'
            )
        },
        'shapes': [
            # Line Vertical
            {
                'type': 'line',
                'x0': '2016-11-01',
                'y0': 0,
                'x1': '2016-11-01',
                'y1': 10,
                'line': {
                    'color': 'rgb(128,128,128)',
                    'width': 2,
                },
            }
        ]
    }

    fig = go.Figure(data=data, layout=layout)
    url = py.plot(fig, filename='hbo_comparison')

if __name__ == "__main__":
    idx = pd.date_range('04/17/11', '06/25/17')
    idx = [str(x.date()) for x in idx]

    game_of_thrones = get_data("https://en.wikipedia.org/wiki/List_of_Game_of_Thrones_episodes",5)
    game_of_thrones = prep_data(game_of_thrones,idx)

    silicon_valley = get_data("https://en.wikipedia.org/wiki/List_of_Silicon_Valley_episodes",4)
    silicon_valley = prep_data(silicon_valley,idx)

    graph(game_of_thrones,silicon_valley)
