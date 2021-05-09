import requests
from flask import Flask
from bs4 import BeautifulSoup
import json
import re

app = Flask(__name__)


def scraper(route, method):
    foreign_lang = False
    try:
        my_url = "https://en.wikipedia.org/wiki/"

        if method == "keyword":

            #################################################################################################
            # Parameters for the GET requests was referenced from https://www.mediawiki.org/wiki/API:Search #
            #################################################################################################

            # url = "https://en.wikipedia.org/w/api.php"
            #
            # payload = {
            #     "action": "query",
            #     "format": "json",
            #     "list": "search",
            #     "srsearch": route  # search for pages containing 'route'
            # }
            #
            # response = requests.get(url=url, params=payload)
            #
            # if response.json()['query']['search'][0]['title'] == route:
            #     replacement = route.replace(" ", "_")
            #     my_url += replacement
            #     print("done replacement: ", my_url)

            replacement = route.replace(" ", "_")
            my_url += replacement

        elif method == "url":
            my_url = route

        # print(my_url)
        result = requests.get(my_url)
        package = result.content

        soup = BeautifulSoup(package, "html.parser")
        # find all paragraphs under the div element that has this specific ID

        # print(soup)

        lang = soup.find(id="bodyContent").find_all("span")
        body = soup.find(id="bodyContent").find_all("p")

        for x in lang:
            string = str(x)
            # print(type(string), string)
            if "<span lang" in string:
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
def index():
    return "Welcome to Daniel's Web Scraper Microservice!"


@app.route('/get_data/<keyword>')
def get_data(keyword):
    json_data = scraper(keyword, "keyword")
    return json_data


# the user must provide the "domain" and "endpoint" of the wiki url
# for example: http://127.0.0.1:5000/get_url/wikipedia.org/Nintendo
# in this case, domain = wikipedia.org & endpoint is Nintendo
# so user must format the url to be: wikipedia.org/<endpoint>
# Can Alex help format actual urls into this format to use my service?
@app.route('/get_url/<string:domain>/<string:endpoint>')
def get_data2(domain, endpoint):
    url = "http://en." + domain + "/wiki/" + endpoint
    json_data = scraper(url, "url")
    return json_data

# if user wants a random wiki article
@app.route('/get_random')
def get_data1():
    url = "https://en.wikipedia.org/wiki/Special:Random"
    json_data = scraper(url, "url")
    return json_data