import requests
from flask import Flask
from flask_cors import CORS, cross_origin
from bs4 import BeautifulSoup
import json
import re

app = Flask(__name__)
cors = CORS(app, support_credentials=True)

def scraper(route, method):
    foreign_lang = False
    try:
        my_url = "https://en.wikipedia.org/wiki/"

        if method == "keyword":
            replacement = route.replace(" ", "_")
            my_url += replacement

        elif method == "url":
            my_url = route

        # print(my_url)
        result = requests.get(my_url)
        package = result.content

        # assign the parser for BeautifulSoup
        soup = BeautifulSoup(package, "html.parser")

        # find all span and p tags in elements that has the id "bodyContent"
        lang = soup.find(id="bodyContent").find_all("span")
        body = soup.find(id="bodyContent").find_all("p")

        for x in lang:
            string = str(x)
            # print(type(string), string)
            if "<span lang" in string or '<span class="IPA nopopups noexcerpt"':
                foreign_lang = True
                break

        target_paragraph = 0

        for x in body:
            if 'class="mw-empty-elt"' not in str(x):
                break
            target_paragraph += 1

        first_paragraph = BeautifulSoup(str(body[target_paragraph]), features="html.parser")
        final_text = first_paragraph.find('p').get_text()  # text is now a string

        target = "\[[^[]*\]"
        final_text = re.sub(target, "", final_text)
        final_text = re.sub("\n", "", final_text)
        final_text = re.sub(u"\u00A0", "", final_text)
        final_text = re.sub(u"\u2013", "-", final_text)

        target = ""

        # print(final_text)

        if foreign_lang:
            target = "\([^.]*\)"
            final_text = re.sub(target, "", final_text)


        data = {"title": route, "content": final_text}
        json_data = json.dumps(data)

        return json_data

    except (IndexError, ConnectionError ):
        data = {"Error": "Wikipedia does not have an article with this keyword or url."}
        json_data = json.dumps(data)

        return json_data

@app.route('/')
@cross_origin()
def index():
    return "Welcome to Daniel's Web Scraper Microservice!"


@app.route('/get_data/<keyword>')
@cross_origin()
def get_data(keyword):
    json_data = scraper(keyword, "keyword")
    return json_data


# user provide a website's domain and endpoint for the domain and endpoint placeholders, respectively
@app.route('/get_url/<string:domain>/<string:endpoint>')
@cross_origin()
def get_data2(domain, endpoint):
    url = "http://en." + domain + "/wiki/" + endpoint
    json_data = scraper(url, "url")
    return json_data

# if user wants a random wiki article
@app.route('/get_random')
@cross_origin()
def get_data1():
    url = "https://en.wikipedia.org/wiki/Special:Random"
    json_data = scraper(url, "url")
    return json_data