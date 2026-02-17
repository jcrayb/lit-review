from flask import Flask, render_template, redirect, request
from flask_cors import CORS
import socketio
import sqlite3
import time
import random 
import pandas as pd
import itertools

import utils.db as db
import utils

sio = socketio.Server(async_mode=None)
app = Flask(__name__)
CORS(app)
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)


@app.route('/')
def main():
    return render_template('main.html')

@app.route('/<hex_code>')
def results(hex_code):
    return render_template('results.html')


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

@app.route('/query', methods=["POST"])
def query():
    json_data = request.get_json()
    description = json_data['description']
    keywords = json_data['keywords']

    if (not keywords) or (not description): return {'message': 'ERROR: empty fields'}
    
    return {'message': 'test'}

@app.route('/results/<hex_code>', methods=["GET"])
def get_results(hex_code):
    
    res = db.get_results(hex_code)
    
    return res

@app.route('/dummy_scrape/<hex_code>', methods=["POST"])
def dummy_scrape(hex_code):
    print(hex_code)

    papers = pd.read_csv('mess_relevance.csv').drop('Unnamed: 0', axis=1)
    papers = papers.reindex(columns=['Name','Year','Authors','Journal', "Categories\n(e.g., SLO, ILO, Decision rule, etc.)", 'Relevance','Hyperlink', 'Key ideas',])

    for i, r in enumerate(papers.iloc()):
        print(i)
        db.add_result(hex_code, [str(e) for e in r.to_list()[:-1]])
        sio.emit(f'scrape_{hex_code}', {'paper': [hex_code] + [str(e) for e in r.to_list()[:-1]]})
        time.sleep(1)
    return {'message': 'SUCCESS'}


@app.route('/scrape/<hex_code>', methods=["POST"])
def scrape(hex_code):
    data = request.get_json()
    description = data['description']
    mkeywords = data['mkeywords']
    okeywords = data['okeywords']

    df = pd.DataFrame(columns=['name', 'year', 'authors', 'journal', 'categories', 'link'])

    combinations = []

    for L in range(len(okeywords) + 1):
        for subset in itertools.combinations(okeywords, L):
                combinations.append(tuple(mkeywords + [s for s in subset]))

    for c in combinations:
        articles = utils.scrape(description)

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

                new_row = pd.DataFrame(columns=['name', 'year', 'authors', 'journal', 'categories', 'link'], index=[0])
                r = [title, date, authors, journal, query, link] 
                db.add_result(hex_code, [str(e) for e in r])
                sio.emit(f'scrape_{hex_code}', {'paper': [hex_code] + [str(e) for e in r]})

                new_df.iloc[i] = [title, date, authors, journal, query, link] 
                
                #new_df = pd.concat(new_df, new_row)
            except:
                continue
        new_df = new_df.dropna()

        df = pd.concat([df, new_df])
        time.sleep(2)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=4321)