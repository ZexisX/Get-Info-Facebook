

from flask import Flask, render_template, request, jsonify
import requests
import json
import re
import os
from datetime import datetime

app = Flask(__name__)

def get_html_source(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        html_source = response.text
        return html_source
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def find_user_info(html_source):
    try:
        match = re.search(r'"props":\s*({.*?})', html_source)
        if match:
            props_json_str = match.group(1)
            user_info = json.loads(props_json_str)
            return user_info
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        target_url = f"https://www.facebook.com/{username}"
        html_source = get_html_source(target_url)

        if html_source:
            user_info = find_user_info(html_source)
            if user_info:
                uid = user_info.get('userID')
                return jsonify({'uid': uid})
            else:
                return jsonify({'error': 'User information not found.'}), 404

    return render_template('index.html', uid=None)

@app.route('/user-details/<user_id>', methods=['GET'])
def get_user_details(user_id):
    try:
        access_token = "EAAD6V7os0gcBOz9kRngtUYZCiyeU5U3pw4UbaDZBezpaIMwLV8bW26D25BE6PZCNZCjKIIsKGob6HKxnFezirCRdP79oOFkTgZBddzAlZB4osoWIXuqlMS5iOIUgtjxagq4LS4cFTWdXEJhaPHSyuD4sqosEjHtExKRBSm0Bau2qDnZA81WsZAMkQTp15wZDZD"
        graph_api_url = f"https://graph.facebook.com/{user_id}?fields=id,is_verified,cover,created_time,link,name,locale,gender,first_name,subscribers.limit(0)&access_token={access_token}"
        response = requests.get(graph_api_url)
        response.raise_for_status()
        user_details = response.json()

        user_details['created_time'] = datetime.strptime(user_details['created_time'], '%Y-%m-%dT%H:%M:%S+0000').strftime('%H:%M:%S %d/%m/%Y')
        user_details['followers'] = user_details['subscribers']['summary']['total_count']
        del user_details['subscribers']

        return jsonify(user_details)

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to fetch user details.'}), 500

if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app._static_folder = os.path.abspath("static")
    app.run(debug=True)
