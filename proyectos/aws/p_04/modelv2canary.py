from flask import Flask, jsonify, request
import time, os

app = Flask(__name__)
MODELID = "V2 - Docker - DeepLearning - Canary"

@app.route('/api/v1/recommendation', methods=['POST'])
def recommendv2():
    start_time = time.time()
    data = request.get_json()
    user_id = data.get('user_id', 'NA')
    time.sleep(0.05)  # Simula latencia mayor
    recommendations = ["itemA_new", "itemB_new", "itemC_new"]
    latency = round((time.time() - start_time) * 1000)
    # TITLE Simula la lgica de recomendacin...
    log_data = f"LOG_S3: USER={user_id}, LATENCY={latency}ms"
    print(log_data)
    return jsonify({
        "event_log": f"User {user_id} purchase processed. Metrics logged to S3.",
        "recommendation": recommendations,
        "model_id": MODELID,
        "latency_ms": latency
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
