from flask import Flask, render_template, redirect
from flask_cors import CORS
import socketio
import sqlite3
import time
import random 
import pandas as pd
import itertools

import utils

connection = sqlite3.Connection('db.db')


sio = socketio.Server(async_mode=None)
app = Flask(__name__)
CORS(app)
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)


@app.route('/')
def main():
    return render_template('main.html')

@app.route('/start')
def start():
    return redirect('/start/1')

@sio.on('message')
def message(sid, data):
    print(sid, data['message'])

@sio.event
def connect(sid, environ, auth):
    sio.emit('connected', {'sid':sid}, to=sid)

    print(f'CONNECTED ${sid}')

@sio.event
def disconnect(sid):
    print(f'DISCONNECTED ${sid}')

@app.route('/scrape')
def scrape():
    df = pd.DataFrame(columns=['name', 'year', 'authors', 'journal', 'categories', 'key ideas', 'link'])
    keywords = {'optional': ['Energy storage', 'Multistage', 'SDDP', 'rolling horizon'],
                'required': ['disaster']}

    min_length = 3
    combinations = []

    optional = keywords['optional']
    for L in range(len(optional) + 1):
        for subset in itertools.combinations(optional, L):
            if len(subset) + len(keywords['required']) >= min_length:
                combinations.append(tuple(keywords['required'] + [s for s in subset]))

    for c in combinations:
        articles = utils.scrape()

        new_df = pd.DataFrame(columns=['name', 'year', 'authors', 'journal', 'categories', 'key ideas', 'link'], index=[i for i in range(len(articles)-1)])

        for i, article in enumerate(articles):
            try:
                title_data =  article.find('div', {'class': 'gs_ri'}).find('h3').find('a')
                title = title_data.text
                link = title_data['href']

                author_data = article.find('div', {'class': 'gs_ri'}).find('div', {'class': 'gs_a'})
                date = int(author_data.text.split("-")[-2].split(',')[-1].strip())
                journal = author_data.text.split("-")[-1]

                authors_list = author_data.text.split("-")[0][:-1].split(',')

                if len(authors_list) > 3:
                    authors = authors_list[0] + " et al."
                else:
                    authors = " &".join(authors_list)

                authors

                print(title, authors, date, link)

                new_row = pd.DataFrame(columns=['name', 'year', 'authors', 'journal', 'categories', 'key ideas', 'link'], index=[0])

                if date >= min_year:
                    new_df.iloc[i] = [title, date, authors, journal, query, "", link] 
                
                #new_df = pd.concat(new_df, new_row)
            except:
                continue
        new_df = new_df.dropna()

        df = pd.concat([df, new_df])
        time.sleep(2)

min_year = 2022

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=4321)