import os, json, time, datetime, urllib.request, urllib.error

UA = {"User-Agent": "Mozilla/5.0 weekly-video-bot"}
HOOK = os.environ.get("DISCORD_WEBHOOK", "").strip()
KEY = os.environ.get("YOUTUBE_API_KEY", "").strip()
MAX_AGE_DAYS = 0   # 0 = always post each channel's latest video; 7 = only uploads from the last 7 days

if not HOOK:
    raise SystemExit("ERROR: Discord webhook secret is empty (NOTIBOT_PUBLIC).")
if not KEY:
    raise SystemExit("ERROR: YOUTUBE_API_KEY secret is empty.")

def post(text):
    req = urllib.request.Request(
        HOOK,
        data=json.dumps({"content": text}).encode(),
        headers={"Content-Type": "application/json", **UA},
    )
    try:
        urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"ERROR: Discord rejected the message ({e.code}). Check the webhook URL.")
    time.sleep(3)

def latest_video(channel_id):
    uploads = "UU" + channel_id[2:]   # a channel's uploads playlist
    url = ("https://www.googleapis.com/youtube/v3/playlistItems"
           f"?part=contentDetails&maxResults=1&playlistId={uploads}&key={KEY}")
    data = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA)).read())
    item = data["items"][0]["contentDetails"]
    published = datetime.datetime.fromisoformat(item["videoPublishedAt"].replace("Z", "+00:00"))
    return f"https://www.youtube.com/watch?v={item['videoId']}", published

ids = [l.split("#")[0].strip() for l in open("channels.txt").read().splitlines()]
ids = [i for i in ids if i]
now = datetime.datetime.now(datetime.timezone.utc)
sent = 0

post("**Weekly knowledge videos**")

for cid in ids:
    try:
        link, published = latest_video(cid)
    except urllib.error.HTTPError as e:
        print(f"SKIPPED {cid}: HTTP {e.code} {e.read().decode()[:200]}")
        continue
    except Exception as e:
        print(f"SKIPPED {cid}: {e}")
        continue
    if MAX_AGE_DAYS and (now - published).days > MAX_AGE_DAYS:
        print(f"SKIPPED {cid}: older than {MAX_AGE_DAYS} days")
        continue
    post(link)
    sent += 1

print(f"Done. Posted {sent} videos from {len(ids)} channels.")
