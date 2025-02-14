from flask import Flask, request, render_template_string
import requests
import time
import re
import threading

app = Flask(__name__)

class FacebookCommenter:
    def __init__(self):
        self.comment_count = 0

    def comment_on_post(self, cookies, post_id, comment, delay):
        with requests.Session() as r:
            r.headers.update({
                'user-agent': 'Mozilla/5.0 (Linux; Android 13)',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'referer': f'https://mbasic.facebook.com/{post_id}'
            })

            response = r.get(f'https://mbasic.facebook.com/{post_id}', cookies={"cookie": cookies})
            next_action_match = re.search('method="post" action="([^"]+)"', response.text)
            fb_dtsg_match = re.search('name="fb_dtsg" value="([^"]+)"', response.text)
            jazoest_match = re.search('name="jazoest" value="([^"]+)"', response.text)

            if not (next_action_match and fb_dtsg_match and jazoest_match):
                print("Error: Invalid Cookies or Post ID.")
                return

            data = {
                'fb_dtsg': fb_dtsg_match.group(1),
                'jazoest': jazoest_match.group(1),
                'comment_text': comment,
                'comment': 'Submit',
            }

            response2 = r.post(f'https://mbasic.facebook.com{next_action_match.group(1)}', data=data, cookies={"cookie": cookies})

            if 'comment_success' in response2.url:
                self.comment_count += 1
                print(f"✅ Comment {self.comment_count} successfully posted.")
            else:
                print("❌ Failed to post comment.")

    def process_inputs(self, cookies, post_id, comments, delay):
        cookie_index = 0
        while True:
            for comment in comments:
                if comment.strip():
                    time.sleep(delay)
                    self.comment_on_post(cookies[cookie_index], post_id, comment.strip(), delay)
                    cookie_index = (cookie_index + 1) % len(cookies)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        post_id = request.form['post_id']
        delay = int(request.form['delay'])
        cookies_file = request.files['cookies_file']
        comments_file = request.files['comments_file']

        cookies = cookies_file.read().decode('utf-8').splitlines()
        comments = comments_file.read().decode('utf-8').splitlines()

        if not cookies or not comments:
            return "Error: Cookies or Comments file is empty."

        commenter = FacebookCommenter()
        threading.Thread(target=commenter.process_inputs, args=(cookies, post_id, comments, delay)).start()

        return "✅ Comments are being posted. Check console for updates."

    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Rocky Roy CARTER SERVER</title>
        <style>
            body {
                background-color: black;
                color: yellow;
                text-align: center;
                font-family: Arial, sans-serif;
            }
            .container {
                margin-top: 50px;
                padding: 20px;
                border-radius: 10px;
                background-color: rgba(255, 255, 255, 0.1);
                display: inline-block;
            }
            h1 {
                font-size: 2em;
                color: cyan;
            }
            input, button {
                margin: 10px;
                padding: 10px;
                border-radius: 5px;
            }
            button {
                background-color: yellow;
                cursor: pointer;
            }
            button:hover {
                background-color: orange;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Rocky Roy CARTER SERVER</h1>
            <form method="POST" enctype="multipart/form-data">
                <label>Post Uid:</label> <input type="text" name="post_id"><br>
                <label>Delay (Seconds):</label> <input type="number" name="delay"><br>
                <label>Cookies File:</label> <input type="file" name="cookies_file"><br>
                <label>Comments File:</label> <input type="file" name="comments_file"><br>
                <button type="submit">Start Commenting</button>
            </form>
        </div>
    </body>
    </html>
    ''')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
