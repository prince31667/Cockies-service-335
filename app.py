from flask import Flask, request, render_template_string
import requests
import time
import random

app = Flask(__name__)

HTML_FORM = '''
<!DOCTYPE html>
<html>
<head>
    <title>Auto Comment - Created by Raghu ACC Rullx</title>
    <style>
        body { background-color: black; color: white; text-align: center; font-family: Arial, sans-serif; }
        input, textarea { width: 300px; padding: 10px; margin: 5px; border-radius: 5px; }
        button { background-color: green; color: white; padding: 10px 20px; border: none; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Created by Raghu ACC Rullx Boy</h1>
    <form method="POST" action="/submit" enctype="multipart/form-data">
        <label for="cookies_file">🔑 Upload Your Facebook Cookies File (cookies.txt):</label><br>
        <input type="file" name="cookies_file" accept=".txt" required><br><br>

        <label for="comment_file">💬 Upload Your Comments File (comments.txt):</label><br>
        <input type="file" name="comment_file" accept=".txt" required><br><br>

        <label for="post_url">📌 Enter Facebook Post URL:</label><br>
        <input type="text" name="post_url" placeholder="https://www.facebook.com/user/posts/123456789" required><br><br>

        <label for="interval">⏳ Enter Comment Interval (in Seconds):</label><br>
        <input type="number" name="interval" placeholder="Interval in Seconds (e.g., 5)" required><br><br>

        <button type="submit">🚀 Start Auto Commenting</button>
    </form>
    {% if message %}<p>{{ message }}</p>{% endif %}
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_FORM)

@app.route('/submit', methods=['POST'])
def submit():
    cookies_file = request.files['cookies_file']
    comment_file = request.files['comment_file']
    post_url = request.form['post_url']
    interval = int(request.form['interval'])

    cookies_list = cookies_file.read().decode('utf-8').splitlines()
    comments = comment_file.read().decode('utf-8').splitlines()

    try:
        post_id = post_url.split("posts/")[1].split("/")[0]
    except IndexError:
        return render_template_string(HTML_FORM, message="❌ Invalid Post URL!")

    url = f"https://m.facebook.com/{post_id}/comment"
    success_count = 0

    while True:
        for i, cookies in enumerate(cookies_list):
            comment = comments[i % len(comments)]  # Comment लूप में घूमेगा
            headers = {
                'cookie': cookies,
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            payload = {'comment_text': comment}
            response = requests.post(url, data=payload, headers=headers)

            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 400:
                continue  # Invalid Cookies, skip to next
            else:
                continue  # Other errors, skip to next

            time.sleep(interval + random.randint(2, 5))  # Anti-blocking Mechanism

        time.sleep(10)  # सभी Cookies से एक बार Comment करने के बाद थोड़ा Gap दें

    return render_template_string(HTML_FORM, message=f"✅ {success_count} Comments Successfully Posted!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
