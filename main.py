from flask import Flask, request, render_template_string, redirect, url_for
import requests
from bs4 import BeautifulSoup
import logging
import os

# ------------------------
# Logging Configuration
# ------------------------
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger()

# Flask Application Setup
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Set a secret key for session management

# In-memory cache for storing scraped texts
scraped_text_cache = {}

# Route: Display Scraped Text
@app.route('/text/<text_id>')
def show_text(text_id):
    # Retrieve the text from the cache using the provided ID
    text = scraped_text_cache.get(text_id, 'No text available.')

    # Render the text along with an option to copy to clipboard
    return render_template_string('''
        <style>
            #scrapedText {
                white-space: pre-wrap; /* This line is added */
            }
        </style>
        <button onclick="copyToClipboard()">Copy to Clipboard</button>
        <script>
        function copyToClipboard() {
            var text = document.getElementById("scrapedText").innerText;
            navigator.clipboard.writeText(text);
        }
        </script>
        <pre id="scrapedText">{{ text }}</pre>
        <a href="/">Back to form</a>
        ''', text=text)

# Route: Main Index
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()

            # Generate a unique ID and store the text in the cache
            text_id = os.urandom(8).hex()
            scraped_text_cache[text_id] = text

            # Redirect to the text display page
            return redirect(url_for('show_text', text_id=text_id))
        except Exception as e:
            logging.error(f"Error scraping URL: {e}")
            return render_template_string('<p>Error occurred: {}</p><a href="/">Back to form</a>'.format(e))

    # Render the main form for input
    return render_template_string('''
        <form method="post">
            URL: <input type="text" name="url"><br>
            <input type="submit" value="Submit">
        </form>
        ''')

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080, debug=True)