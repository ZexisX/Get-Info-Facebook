from flask import Flask, render_template, request, jsonify
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

def get_user_id(username):
    hd = {
        "Cookie": "sb=vZKuZUvhBAjDFehqIdRke6M_;datr=vZKuZYB6tAvMoBBbMIOaw3PH;c_user=100000519583426;ps_n=0;ps_l=0;dpr=1.3333333730697632;xs=24%3ANZMOlc-RoWfPJw%3A2%3A1706022493%3A-1%3A10645%3A%3AAcWL1QoeXmUwjk-bSv0UOx63bttxHKbw4KX7rLWTtAs;i_user=61555552843696;fr=0GEMCQwUeRVKhqRbd.AWUIOrclAZ6HHo1x0YjIthVV7CE.BlvGj7.Yh.AAA.0.0.BlvGkL.AWVIzO2ZoyI;presence=EDvF3EtimeF1706846526EuserFA21B00519583426A2EstateFDutF0CEchF_7bCC;wd=878x721;"
    }
    get = requests.get(f"https://www.facebook.com/{username}", headers=hd).text
    id_acc = get.split('"userID":"')[1].split('"')[0]
    return id_acc

@app.route('/user/<username>', methods=['GET'])
def get_user_json(username):
    try:
        if username == "me":
            return jsonify({'error': 'Unauthorized access.'}), 401
        
        user_id = get_user_id(username)
        return jsonify({'uid': user_id})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'User information not found.'}), 404

@app.route('/user-details/<user_id>', methods=['GET'])
def get_user_details(user_id):
    try:
        access_token = "EAAD6V7os0gcBO55XAJ2PajkwegUZCCCiRZCBjhKJFmj24wy2zzKEEmqjqFZAluPEtsZAY1N0tpsbMbVn1SfusWoxLDN4ZChVEh0lApbghmZCDs9mI5ObnlrWPpZCXH1S4xoshxOngqqpSQUgWgrStEke92SGE7z5BfBFQW2683AvNjyD9O5LTtiOUES7QZDZD"
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
