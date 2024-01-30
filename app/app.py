from flask import Flask, render_template, request, jsonify
import requests
import re
import json
import os
from datetime import datetime

app = Flask(__name__)

def get_user_id(username):
    hd = {
        "Cookie": "sb=vZKuZUvhBAjDFehqIdRke6M_;datr=vZKuZYB6tAvMoBBbMIOaw3PH;locale=vi_VN;c_user=100000519583426;ps_n=0;ps_l=0;dpr=1.3333333730697632;i_user=61555552843696;xs=24%3ANZMOlc-RoWfPJw%3A2%3A1706022493%3A-1%3A10645%3A%3AAcUxQzkp1NS5lgh4Hz8Q3Dy2F9Zl7gv0FXBxfHFeFaQ;fr=1K9OstgLKbtvL5NKU.AWWln3qhWfAh60mZ7qG7lQ2KUFw.BluMo8.Yh.AAA.0.0.BluMo8.AWUzpU_dtek;presence=EDvF3EtimeF1706609220EuserFA21B00519583426A2EstateFDutF0CEchF_7bCC;wd=1429x721;"
    }
    get = requests.get(f"https://www.facebook.com/{username}", headers=hd).text
    
    # Regex để tìm kiếm ID người dùng trong URL
    match = re.search(r'(profile\.php\?id=\d+|\d+)', get)
    
    if match:
        user_id = match.group(1)
        return user_id
    else:
        raise ValueError("User ID not found in the URL")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        try:
            user_id = get_user_id(username)
            return jsonify({'uid': user_id})
        except Exception as e:
            print(f"Error: {e}")
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
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
