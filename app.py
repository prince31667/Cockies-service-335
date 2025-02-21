from flask import Flask, request, render_template_string
import requests
import time
import random

app = Flask(__name__)

HTML_FORM = '''
<!DOCTYPE html>
<html>
<head>
    <title>Facebook Auto Comment (Token + Cookies)</title>
    <style>
        body { background-color: black; color: white; text-align: center; font-family: Arial, sans-serif; }
        input, button { width: 300px; padding: 10px; margin: 5px; border-radius: 5px; }
        button { background-color: green; color: white; padding: 10px 20px; border: none; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Facebook Auto Comment (Token + Cookies)</h1>
    <form method="POST" action="/submit" enctype="multipart/form-data">
        <input type="file" name="token_file" accept=".txt"><br>
        <input type="file" name="cookie_file" accept=".txt"><br>
        <input type="file" name="comment_file" accept=".txt" required><br>
        <input type="text" name="post_url" placeholder="Enter Facebook Post URL" required><br>
        <input type="number" name="interval" placeholder="Time Interval in Seconds (e.g., 30)" required><br>
        <button type="submit">Start Commenting</button>
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
    token_file = request.files.get('token_file')
    cookie_file = request.files.get('cookie_file')
    comment_file = request.files['comment_file']
    post_url = request.form['post_url']
    interval = int(request.form['interval'])

    tokens = token_file.read().decode('utf-8').splitlines() if token_file else []
    cookies = cookie_file.read().decode('utf-8').splitlines() if cookie_file else []
    comments = comment_file.read().decode('utf-8').splitlines()

    try:
        post_id = post_url.split("posts/")[1].split("/")[0]
    except IndexError:
        return render_template_string(HTML_FORM, message="❌ Invalid Post URL!")

    url = f"https://graph.facebook.com/{post_id}/comments"
    success_count = 0
    active_tokens = list(tokens)
    active_cookies = list(cookies)

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X)"
    ]

    def modify_comment(comment):
        emojis = ["🔥", "✅", "💯", "👏", "😊", "👍", "🙌", "🎉", "😉", "💪"]
        variations = ["!!", "!!!", "✔️", "...", "🤩", "💥"]
        return f"{random.choice(variations)} {comment} {random.choice(emojis)}"

    def post_with_token(token, comment):
        headers = {"User-Agent": random.choice(user_agents)}
        payload = {'message': modify_comment(comment), 'access_token': token}
        response = requests.post(url, data=payload, headers=headers)
        return response

    def post_with_cookie(cookie, comment):
        headers = {
            "User-Agent": random.choice(user_agents),
            "Cookie": cookie
        }
        payload = {'message': modify_comment(comment)}
        response = requests.post(url, data=payload, headers=headers)
        return response

    comment_index = 0
    while True:
        if not active_tokens and not active_cookies:
            active_tokens = list(tokens)
            active_cookies = list(cookies)
            print("🔄 सभी Tokens & Cookies Reset कर दिए गए!")

        token = active_tokens.pop(0) if active_tokens else None
        cookie = active_cookies.pop(0) if active_cookies else None
        comment = comments[comment_index % len(comments)]

        if token:
            response = post_with_token(token, comment)
            if response.status_code == 200:
                success_count += 1
                print(f"✅ Token से Comment Success!")
            else:
                print(f"❌ Token Blocked, Switching to Cookies...")

        if not token or (response.status_code != 200 and cookie):
            response = post_with_cookie(cookie, comment)
            if response.status_code == 200:
                success_count += 1
                print(f"✅ Cookies से Comment Success!")
            else:
                print(f"❌ Cookies भी Blocked!")

        comment_index += 1

        safe_delay = interval + random.randint(10, 30)
        print(f"⏳ Waiting {safe_delay} seconds before next comment...")
        time.sleep(safe_delay)

    return render_template_string(HTML_FORM, message=f"✅ {success_count} Comments Successfully Posted!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
