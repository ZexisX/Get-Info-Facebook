from flask import Flask, render_template, request, jsonify
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

def get_user_id(username):
    hd = {
        "Cookie": "sb=r5GuZSVFfQzuwJfUIR0KUgOt;datr=r5GuZWAt8-o6iRc3NN4o_OLR;ps_n=0;ps_l=0;c_user=100009028428284;xs=33%3AmNb4wsrfOnnmhA%3A2%3A1706285865%3A-1%3A6168%3A%3AAcULCQlbNBT7-OvGCjJ7K0MRi5m2MQySgehHN9Dmag;fr=1mQwQpBIQZK8jq4sr.AWVMex8I58Qcbtq6QrSSWLSjFSI.BlzOsZ.Sd.AAA.0.0.BlzOsZ.AWWcAhUCAGg;wd=1432x721;presence=C%7B%22t3%22%3A%5B%7B%22o%22%3A0%2C%22i%22%3A%22u.100004577359075%22%7D%2C%7B%22o%22%3A0%2C%22i%22%3A%22u.100015861317638%22%7D%2C%7B%22o%22%3A0%2C%22i%22%3A%22u.100040037740246%22%7D%5D%2C%22utc3%22%3A1707928349124%2C%22v%22%3A1%7D;"
    }
    get = requests.get(f"https://www.facebook.com/{username}", headers=hd).text
    id_acc = get.split('"userID":"')[1].split('"')[0]
    return id_acc

@app.route('/_/<username>', methods=['GET'])
def get_user_json(username):
    try:
        user_id = get_user_id(username)
        return jsonify({'uid': user_id})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'User information not found.'}), 404

@app.route('/user-details/<user_id>', methods=['GET'])
def get_user_details(user_id):
    try:
        access_token = "EAAD6V7os0gcBO23tZBBv2uiZAzUyDWkeH4hNww5JbIWdNpnONjOUpTWj7y1GwoHODJq8piiI5pmNWsUWsmeZCqh2IYbhoWks0UTm8vTtHS2u85J1Y49Xnb1LIg76YohZCISIZAdNpkwEuY1P66z0SXLyZA6PjVXzmxQs6ap6dy7pWGCYi18UmZA5F2DlZAUBMLxG0PN4GnXeRgZDZD"
        graph_api_url = f"https://graph.facebook.com/{user_id}?fields=id,is_verified,cover,created_time,link,name,locale,gender,first_name,subscribers.limit(0)&access_token={access_token}"
        response = requests.get(graph_api_url)
        response.raise_for_status()
        user_details = response.json()

        user_details['created_time'] = datetime.strptime(user_details['created_time'], '%Y-%m-%dT%H:%M:%S+0000').strftime('%H:%M:%S %d/%m/%Y UTC')
        user_details['followers'] = user_details['subscribers']['summary']['total_count']
        del user_details['subscribers']

        return jsonify(user_details)

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to fetch user details.'}), 500

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
