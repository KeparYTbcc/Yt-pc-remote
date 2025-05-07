# youtube_remote.py
from flask import Flask, render_template_string, request
import pyautogui
import webbrowser
from threading import Timer
import socket
from io import BytesIO
import qrcode
import base64

app = Flask(__name__)
PIN = "1234"  # Change this PIN

# Get local IP address
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return socket.gethostbyname(socket.gethostname())

LOCAL_IP = get_local_ip()
URL = f"http://{LOCAL_IP}:5000"

# Generate QR code
def generate_qr(url):
    qr = qrcode.QRCode(version=1, box_size=4, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

QR_CODE = generate_qr(URL)

# HTML templates
MOBILE_HTML = f'''
<!DOCTYPE html>
<html>
<head>
    <title>YouTube Remote</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ background: #1a1a1a; color: white; }}
        .container {{ max-width: 400px; margin: 0 auto; padding: 20px; }}
        .btn {{ 
            width: 100%; padding: 15px; margin: 5px 0; 
            background: #2d2d2d; border: none; color: white; 
            border-radius: 8px; font-size: 18px;
            touch-action: manipulation;
        }}
        .btn:active {{ background: #404040; }}
        .warning {{ 
            background: #ff4444; padding: 10px; 
            border-radius: 8px; text-align: center;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2 style="text-align: center;">🎮 YouTube Remote</h2>
        <div class="warning">Keep YouTube focused on PC!</div>
        
        <button class="btn" onclick="sendCmd('playpause')">⏯ Play/Pause</button>
        <div style="display: flex; gap: 5px; margin: 5px 0;">
            <button class="btn" style="flex:1" onclick="sendCmd('seekb')">⏪ -10s</button>
            <button class="btn" style="flex:1" onclick="sendCmd('seekf')">⏩ +10s</button>
        </div>
        <button class="btn" onclick="sendCmd('next')">⏭ Next Track</button>
        <button class="btn" onclick="sendCmd('prev')">⏮ Previous</button>
        
        <div style="display: flex; gap: 5px; margin: 5px 0;">
            <button class="btn" style="flex:1" onclick="sendCmd('voldown')">🔉 Vol-</button>
            <button class="btn" style="flex:1" onclick="sendCmd('volup')">🔊 Vol+</button>
        </div>
        
        <button class="btn" onclick="sendCmd('fullscreen')">📺 Fullscreen</button>
    </div>
    <script>
        const PIN = "{PIN}";
        function sendCmd(cmd) {{
            fetch(`/control?cmd=${{cmd}}&pin=${{PIN}}`)
                .catch(console.error);
        }}
    </script>
</body>
</html>
'''

DESKTOP_HTML = f'''
<!DOCTYPE html>
<html>
<head>
    <title>YouTube Remote - Controller</title>
    <style>
        body {{ 
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 2rem;
            background: #f0f0f0;
        }}
        .qr-container {{ 
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin: 20px;
        }}
        .instructions {{ 
            max-width: 500px;
            text-align: center;
            margin: 20px 0;
            line-height: 1.6;
        }}
        .url {{ 
            background: #e0e0e0;
            padding: 10px;
            border-radius: 6px;
            font-family: monospace;
            margin: 10px;
        }}
    </style>
</head>
<body>
    <h1>📱 YouTube Remote Control</h1>
    
    <div class="instructions">
        <h2>Scan this QR code with your phone:</h2>
        <div class="qr-container">
            <img src="data:image/png;base64,{QR_CODE}" style="width: 200px; height: 200px;">
        </div>
        
        <p>Or visit this URL on your phone:</p>
        <div class="url">{URL}</div>
        
        <h3>Requirements:</h3>
        <ul style="text-align: left;">
            <li>Both devices must be on the same network</li>
            <li>Keep this window open</li>
            <li>YouTube must be focused in your browser</li>
        </ul>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    user_agent = request.headers.get('User-Agent', '').lower()
    is_mobile = 'mobi' in user_agent
    
    if is_mobile:
        return render_template_string(MOBILE_HTML)
    else:
        return render_template_string(DESKTOP_HTML)

@app.route('/control')
def control():
    if request.args.get('pin', '') != PIN:
        return "Invalid PIN", 403
    
    cmd = request.args.get('cmd', '')
    handle_command(cmd)
    return "OK"

def handle_command(cmd):
    pyautogui.sleep(0.1)
    keymap = {
        'playpause': 'k',
        'next': 'shift+n',
        'prev': 'shift+p',
        'volup': 'up',
        'voldown': 'down',
        'fullscreen': 'f',
        'seekf': 'l',
        'seekb': 'j'
    }
    
    if cmd in keymap:
        key_combination = keymap[cmd]
        # Split multi-key commands (e.g., "shift+n" into ["shift", "n"])
        if '+' in key_combination:
            keys = key_combination.split('+')
            pyautogui.hotkey(*keys)  # Press keys simultaneously
        else:
            pyautogui.press(key_combination)  # Single key press

def open_browser():
    webbrowser.open_new('http://localhost:5000')

if __name__ == '__main__':
    # Print connection info
    print(f"\n🔗 Local access: http://localhost:5000")
    print(f"📱 Mobile access: {URL}")
    
    # Open browser after 1 second
    Timer(1, open_browser).start()
    
    # Run the app
    app.run(host='0.0.0.0', port=5000)