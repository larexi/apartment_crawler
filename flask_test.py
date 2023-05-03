import json

from crawler import RentalApartmentCrawler
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET'])
def get_apartments():
    return render_template('index.html')

@app.route('/results', methods=['POST'])
def get_ads():
    print(request.form)

    crawler = RentalApartmentCrawler()
    max_rent = request.form.get('max_rent')
    no_of_rooms = request.form.get('rooms')
    area = request.form.get('area')

    travel_targets = request.form.getlist('travel')
    # for address in travel_targets:
    #     crawler.commuting_calculator.add_address(address)

    crawler.set_criteria({
        'max_rent': max_rent,
        'no_of_rooms': no_of_rooms,
        'area': area
    })

    values = crawler.crawl_vuokraovi()
    return '<hmtl><div><pre>' + json.dumps(values, indent=2) + '</pre></div></html>'

if __name__ =="__main__":  
    app.run(debug = True)  