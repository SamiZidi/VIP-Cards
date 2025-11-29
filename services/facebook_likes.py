import re
import requests

def get_video_likes_from_url(video_url, ACCESS_TOKEN):
    # Extract video ID from the URL
    match = re.search(r"(\d{8,})", video_url)
    if not match:
        return {"error": "Invalid video URL"}

    video_id = match.group(1)
    #print("Video ID:", video_id)
    
    # Updated URL to match your working curl command
    url = f"https://graph.facebook.com/v24.0/{video_id}"
    params = {
        "fields": "video_insights",
        "access_token": ACCESS_TOKEN
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        total_reactions = 0
        views = 0

        # Navigate through the nested structure
        video_insights = data.get("video_insights", {}).get("data", [])
        
        for item in video_insights:
            if item["name"] == "post_video_likes_by_reaction_type":
                reactions = item["values"][0].get("value", {})
                # print("Reactions:", reactions)
                total_reactions = sum(reactions.values())
            elif item["name"] == "fb_reels_total_plays":
                views = item["values"][0].get("value", 0)
                # print("Views:", views)

        return total_reactions, views
        

    except Exception as e:
        # print("Error:", str(e))
        return {"error": str(e)}
    