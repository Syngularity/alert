from flask import Flask, request, jsonify
import threading
import asyncio
import os
import time 


from discord_bot import run_discord_bot, bot 

ALERT_PORT = int(os.getenv('ALERT_PORT', 5000))

app = Flask(__name__)

@app.route('/send_momentum_alert', methods=['POST'])
def send_discord_message_endpoint():
    data = request.get_json()

    required_fields = ['ticker', 'price', 'multiplier', 'float_value', 'volume', 'tier', 'phase']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: '{field}'"}), 400

    ticker = data['ticker']
    price = data['price']
    multiplier = data['multiplier']
    float_value = data['float_value']
    volume = data['volume']
    tier = data['volume']
    phase = data['volume']

    payload = {
        'ticker': ticker,
        'price': price,
        'multiplier': multiplier,
        'float_value': float_value,
        'volume': volume,
        'tier': tier,
        'phase': phase
    }

    try:
        if not hasattr(bot, 'message_queue') or bot.message_queue is None:
            return jsonify({"error": "Discord bot not fully ready to receive messages. Please try again shortly."}), 503
            
        discord_loop = bot.loop 
        asyncio.run_coroutine_threadsafe(bot.message_queue.put(payload), discord_loop) # Access queue via bot.message_queue


        return jsonify({"status": "Alert queued for Discord", "data": payload}), 200
    
    except Exception as e:
        print(f"Error queuing message for Discord: {e}")
        return jsonify({"error": f"Failed to queue alert for Discord: {e}"}), 500

def start_discord_bot_in_thread():
    run_discord_bot()


if __name__ == '__main__':
    discord_thread = threading.Thread(target=start_discord_bot_in_thread, daemon=True)
    discord_thread.start()

    time.sleep(3)

    print(f"Starting Flask API on port {ALERT_PORT}...")
    app.run(debug=True, host='0.0.0.0', port=ALERT_PORT)