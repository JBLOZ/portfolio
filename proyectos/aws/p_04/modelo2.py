from flask import Flask, jsonify, request
import time

app = Flask(__name__)
MODEL_ID = "V2 - DeepLearning - Canary"

@app.route('/api/v1/recommendation', methods=['POST'])
def recommend_v2():
    start_time = time.time()
    data = request.get_json()
    user_id = data.get('user_id', 'N/A')
    time.sleep(0.05)  # Simula latencia mayor
    recommendations = ["item_A_new", "item_B_new", "item_C_new"]
    latency = round((time.time() - start_time) * 1000)
    print(f"[LOG] USER:{user_id}, MODEL:{MODEL_ID}, LATENCY:{latency}ms")
    return jsonify({
        "event_log": f"User {user_id} purchase processed. Metrics available.",
        "recommendation": recommendations,
        "model_id": MODEL_ID,
        "latency_ms": latency
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)