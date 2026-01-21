from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
API_KEY = os.getenv("YOUTUBE_API_KEY")

@app.route("/", methods=["GET", "POST"])
def index():
    channel = None
    error = None

    if request.method == "POST":
        query = request.form.get("query")

        search_url = "https://www.googleapis.com/youtube/v3/search"
        search_params = {
            "part": "snippet",
            "q": query,
            "type": "channel",
            "maxResults": 1,
            "key": API_KEY
        }

        search_response = requests.get(search_url, params=search_params).json()

        if "items" not in search_response or len(search_response["items"]) == 0:
            error = "Channel not found"
        else:
            # ✅ FIXED LINE
            channel_id = search_response["items"][0]["id"]["channelId"]

            channel_url = "https://www.googleapis.com/youtube/v3/channels"
            channel_params = {
                "part": "snippet,statistics",
                "id": channel_id,
                "key": API_KEY
            }

            channel_response = requests.get(channel_url, params=channel_params).json()

            if "items" not in channel_response or len(channel_response["items"]) == 0:
                error = "Unable to fetch channel details"
            else:
                data = channel_response["items"][0]

                views = int(data["statistics"].get("viewCount", 0))
                videos = int(data["statistics"].get("videoCount", 0))
                subscribers = int(data["statistics"].get("subscriberCount", 0))

                # Revenue estimation (CPM based)
                min_rev = round((views / 1000) * 0.25, 2)
                max_rev = round((views / 1000) * 4, 2)

                channel = {
                    "name": data["snippet"]["title"],
                    "description": data["snippet"]["description"],
                    "logo": data["snippet"]["thumbnails"]["high"]["url"],
                    "created_at": data["snippet"]["publishedAt"][:10],
                    "views": views,
                    "videos": videos,
                    "subscribers": subscribers,
                    "min_rev": min_rev,
                    "max_rev": max_rev
                }

    return render_template("index.html", channel=channel, error=error)

if __name__ == "__main__":
    app.run(debug=True)
