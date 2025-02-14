from flask import Flask, request, render_template_string
import requests
import re
import time

app = Flask(__name__)

class FacebookCommenter:
    def __init__(self):
        self.comment_count = 0

    def comment_with_cookie(self, cookies, post_id, comment):
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13)',
            'Accept-Language': 'en-US,en;q=0.9',
        })

        response = session.get(f'https://mbasic.facebook.com/{post_id}', cookies={"cookie": cookies})
        next_action_match = re.search('method="post" action="([^"]+)"', response.text)
        fb_dtsg_match = re.search('name="fb_dtsg" value="([^"]+)"', response.text)
        jazoest_match = re.search('name="jazoest" value="([^"]+)"', response.text)

        if not (next_action_match and fb_dtsg_match and jazoest_match):
            return False

        next_action = next_action_match.group(1).replace('amp;', '')
        fb_dtsg = fb_dtsg_match.group(1)
        jazoest = jazoest_match.group(1)

        data = {
            'fb_dtsg': fb_dtsg,
            'jazoest': jazoest,
            'comment_text': comment,
            'comment': 'Submit',
        }

        session.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
        response2 = session.post(f'https://mbasic.facebook.com{next_action}', data=data, cookies={"cookie": cookies})

        if 'comment_success' in response2.url and response2.status_code == 200:
            self.comment_count += 1
            return True
        return False

    def comment_with_token(self, token, post_id, comment):
        url = f"https://graph.facebook.com/{post_id}/comments"
        data = {"message": comment, "access_token": token}
        response = requests.post(url, data=data)

        if response.status_code == 200:
            self.comment_count += 1
            return True
        return False

    def process_inputs(self, post_id, comment, cookies, tokens):
        for _ in range(10):  # 10 बार कोशिश करेगा
            if cookies and self.comment_with_cookie(cookies, post_id, comment):
                return "Comment posted using Cookies!"
            if tokens and self.comment_with_token(tokens, post_id, comment):
                return "Comment posted using Token!"
            time.sleep(5)  # 5 सेकंड का गैप रखेगा
        return "Failed to post comment."

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        post_id = request.form["post_id"]
        comment = request.form["comment"]
        cookies = request.form["cookies"]
        token = request.form["token"]

        commenter = FacebookCommenter()
        result = commenter.process_inputs(post_id, comment, cookies, token)

        return f"<h3>{result}</h3>"

    form_html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Facebook Auto Comment</title>
        <style>
            body { background-color: black; color: yellow; text-align: center; }
            .container { margin-top: 50px; padding: 20px; border-radius: 10px; }
            input, button { margin: 10px; padding: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Facebook Auto Comment</h1>
            <form method="POST">
                <label>Post ID:</label>
                <input type="text" name="post_id"><br>
                <label>Comment:</label>
                <input type="text" name="comment"><br>
                <label>Cookies:</label>
                <input type="text" name="cookies"><br>
                <label>Token:</label>
                <input type="text" name="token"><br>
                <button type="submit">Start Commenting</button>
            </form>
        </div>
    </body>
    </html>
    '''
    return render_template_string(form_html)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
