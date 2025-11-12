from flask import Flask, jsonify, request
import time

app = Flask(__name__)
MODELID = "V1 - Stable"

@app.route('/api/v1/recommendation', methods=['POST'])
def recommendv1():
    start_time = time.time()
    data = request.get_json()
    user_id = data.get('user_id', 'NA')
    recommendations = ["itemX_oldmodel", "itemY_oldmodel"]
    latency = round((time.time() - start_time) * 1000)
    return jsonify({
        "event_log": f"User {user_id} purchase processed.",
        "recommendation": recommendations,
        "model_id": MODELID,
        "latency_ms": latency
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
