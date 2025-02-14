from flask import Flask, render_template_string, request
import requests
import time

app = Flask(__name__)

# HTML Form as String
HTML_FORM = """
<!DOCTYPE html>
<html>
<head>
    <title>Facebook Auto Comment</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: black; color: white; text-align: center; }
        form { margin: 20px auto; width: 50%; padding: 20px; background: #222; border-radius: 10px; }
        input, textarea { width: 100%; padding: 10px; margin: 5px 0; background: #333; color: white; border: none; }
        button { padding: 10px 20px; background: green; color: white; border: none; cursor: pointer; }
    </style>
</head>
<body>
    <h1>Facebook Auto Comment</h1>
    <form method="POST">
        <label>Facebook Cookies:</label>
        <textarea name="cookies" required></textarea><br>
        
        <label>Post URL:</label>
        <input type="text" name="post_url" required><br>
        
        <label>Comment:</label>
        <input type="text" name="comment" required><br>
        
        <label>Time Interval (Seconds):</label>
        <input type="number" name="interval" min="5" value="10" required><br>
        
        <button type="submit">Submit</button>
    </form>
    <h3>{{ result }}</h3>
</body>
</html>
"""

# Facebook पर Auto Comment करने का Function
def post_comment(cookie, post_url, comment):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cookie": cookie
    }
    
    # Extract Post ID from URL
    if "facebook.com" in post_url:
        post_id = post_url.split("posts/")[-1].split("/")[0]
    else:
        return "Invalid Post URL"
    
    comment_url = f"https://graph.facebook.com/{post_id}/comments"
    payload = {"message": comment}
    
    response = requests.post(comment_url, data=payload, headers=headers)
    
    if response.status_code == 200:
        return "✅ Comment Successfully Posted!"
    else:
        return f"❌ Error: {response.text}"

# HTML Form Page
@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    if request.method == "POST":
        cookies = request.form["cookies"]
        post_url = request.form["post_url"]
        comment = request.form["comment"]
        interval = int(request.form["interval"])
        
        result = post_comment(cookies, post_url, comment)
        
        time.sleep(interval)  # Set Time Delay

    return render_template_string(HTML_FORM, result=result)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
