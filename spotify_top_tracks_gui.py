
import os
import io
import webbrowser
import threading
import tkinter as tk
from tkinter import ttk, simpledialog
from urllib.parse import urlparse
import requests
from PIL import Image, ImageTk

TOKEN_URL = "https://accounts.spotify.com/api/token"
BASE_API = "https://api.spotify.com/v1"

# -----------------------------
# .env helpers (no dependency)
# -----------------------------
def load_env_from_dotenv(dotenv_path: str = ".env") -> None:
    try:
        with open(dotenv_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip(); v = v.strip().strip('"').strip("'")
                if k and k not in os.environ:
                    os.environ[k] = v
    except FileNotFoundError:
        pass

def save_env_to_dotenv(client_id: str, client_secret: str, dotenv_path: str = ".env") -> None:
    with open(dotenv_path, "w", encoding="utf-8") as f:
        f.write(f"SPOTIFY_CLIENT_ID={client_id}\nSPOTIFY_CLIENT_SECRET={client_secret}\n")

def b64(s: str) -> str:
    import base64
    return base64.b64encode(s.encode("utf-8")).decode("utf-8")

def get_client_credentials_token(client_id: str, client_secret: str) -> str:
    headers = {
        "Authorization": "Basic " + b64(f"{client_id}:{client_secret}"),
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"grant_type": "client_credentials"}
    r = requests.post(TOKEN_URL, headers=headers, data=data, timeout=20)
    r.raise_for_status()
    return r.json()["access_token"]

def extract_artist_id(s: str) -> str:
    s = s.strip()
    if not s:
        raise ValueError("Artist link or ID is empty.")
    try:
        p = urlparse(s)
        if p.netloc.endswith("open.spotify.com"):
            parts = p.path.strip("/").split("/")
            if len(parts) >= 2 and parts[0] == "artist":
                return parts[1].split("?")[0]
    except Exception:
        pass
    return s

def get_artist_top_tracks(artist_id: str, token: str, market: str = "US") -> list:
    url = f"{BASE_API}/artists/{artist_id}/top-tracks"
    params = {"market": market}
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers, params=params, timeout=20)
    r.raise_for_status()
    tracks = r.json().get("tracks", [])
    tracks.sort(key=lambda t: t.get("popularity", 0), reverse=True)
    return tracks

# ----------- Utilities for crawling all releases (more than 10) -----------
def _paginate(url, headers, params=None, limit=50):
    if params is None:
        params = {}
    params = dict(params)
    params.setdefault("limit", limit)
    params.setdefault("offset", 0)
    while True:
        r = requests.get(url, headers=headers, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        items = data.get("items", [])
        for it in items:
            yield it
        if data.get("next"):
            params["offset"] += params["limit"]
        else:
            break

def _chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

def get_all_tracks_for_artist(artist_id: str, token: str, market: str = "US",
                              include_groups: str = "album,single,compilation,appears_on") -> list:
    headers = {"Authorization": f"Bearer {token}"}
    # 1) Gather album ids
    albums_url = f"{BASE_API}/artists/{artist_id}/albums"
    seen_albums = set()
    album_ids = []
    for alb in _paginate(albums_url, headers, params={"include_groups": include_groups, "market": market, "limit": 50}):
        aid = alb.get("id")
        if aid and aid not in seen_albums:
            seen_albums.add(aid)
            album_ids.append(aid)

    # 2) Gather track ids
    seen_tracks = set()
    track_ids = []
    for aid in album_ids:
        tracks_url = f"{BASE_API}/albums/{aid}/tracks"
        for tr in _paginate(tracks_url, headers, params={"market": market, "limit": 50}):
            tid = tr.get("id")
            if tid and tid not in seen_tracks:
                seen_tracks.add(tid)
                track_ids.append(tid)

    if not track_ids:
        return []

    # 3) Batch fetch full track objects
    full_tracks = []
    for batch in _chunks(track_ids, 50):
        url = f"{BASE_API}/tracks"
        params = {"ids": ",".join(batch), "market": market}
        r = requests.get(url, headers=headers, params=params, timeout=30)
        r.raise_for_status()
        full_tracks.extend(r.json().get("tracks", []))

    # 4) Sort by popularity desc
    full_tracks.sort(key=lambda t: (t or {}).get("popularity", 0), reverse=True)
    return full_tracks

def image_from_url(url: str, size=(72, 72)) -> ImageTk.PhotoImage:
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        im = Image.open(io.BytesIO(r.content)).convert("RGBA")
    except Exception:
        im = Image.new("RGBA", size, (230, 230, 230, 255))
    im = im.resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(im)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Spotify Top Tracks")
        self.minsize(1040, 600)

        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Desired sizes
        self.row_height = 80
        self.art_size = (72, 72)

        self.style = ttk.Style(self)
        self.style.configure("Treeview", rowheight=self.row_height)

        # --- Header / inputs
        hdr = ttk.Frame(self, padding=(12, 12))
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_columnconfigure(1, weight=1)

        ttk.Label(hdr, text="Artist URL or ID:").grid(row=0, column=0, padx=(0,8))
        self.artist_var = tk.StringVar()
        ttk.Entry(hdr, textvariable=self.artist_var).grid(row=0, column=1, sticky="ew")
        self.artist_var.set("https://open.spotify.com/artist/4NJxtQzTTeO3ObGlBcxVAh")

        self.market_var = tk.StringVar(value="US")
        ttk.Label(hdr, text="Market:").grid(row=0, column=2, padx=(8,2))
        ttk.Entry(hdr, textvariable=self.market_var, width=6).grid(row=0, column=3)

        # Fetch mode controls
        mode = ttk.Frame(self, padding=(12, 0))
        mode.grid(row=1, column=0, sticky="ew")
        self.all_tracks_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(mode, text="All tracks (slow - crawls releases)", variable=self.all_tracks_var).grid(row=0, column=0, padx=(0,12))
        ttk.Label(mode, text="Max results:").grid(row=0, column=1)
        self.limit_var = tk.StringVar(value="100")
        ttk.Entry(mode, textvariable=self.limit_var, width=6).grid(row=0, column=2, padx=(4,12))

        ttk.Button(mode, text="Get tracks", command=self.on_fetch).grid(row=0, column=3)

        # --- Status
        self.status_var = tk.StringVar(value="Tip: Double‑click a track to open it in your browser.")
        ttk.Label(self, textvariable=self.status_var, padding=(12, 6)).grid(row=2, column=0, sticky="ew")

        # --- Table (Treeview)
        # Columns after the image column (#0): popularity, track, album, artists
        columns = ("popularity", "track", "album", "artists")
        self.tree = ttk.Treeview(self, columns=columns, show="tree headings")
        self.tree.heading("#0", text="Album art")
        self.tree.heading("popularity", text="Popularity")
        self.tree.heading("track", text="Track (double‑click to open)")
        self.tree.heading("album", text="Album")
        self.tree.heading("artists", text="Artist(s)")

        first_col_width = self.art_size[0] + 16
        self.tree.column("#0", width=first_col_width, minwidth=first_col_width, stretch=False, anchor="w")
        self.tree.column("popularity", width=90, minwidth=70, stretch=False, anchor="center")
        self.tree.column("track", width=420, minwidth=220, stretch=True, anchor="w")
        self.tree.column("album", width=260, minwidth=160, stretch=True, anchor="w")
        self.tree.column("artists", width=280, minwidth=160, stretch=True, anchor="w")

        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=4, column=0, sticky="nsew", padx=(12,0), pady=(0,12))
        vsb.grid(row=4, column=1, sticky="ns", pady=(0,12))

        self._image_refs = {}
        self._url_by_iid = {}

        self.tree.bind("<Double-1>", self.on_double_click)

        self.status_var.set("Choose mode (Top 10 or All tracks). Columns are resizable.")

    def ensure_credentials(self) -> bool:
        load_env_from_dotenv(".env")
        cid = os.getenv("SPOTIFY_CLIENT_ID", "").strip()
        sec = os.getenv("SPOTIFY_CLIENT_SECRET", "").strip()
        if cid and sec:
            return True
        cid = simpledialog.askstring("Spotify Client ID", "Enter your SPOTIFY_CLIENT_ID:", parent=self)
        if not cid:
            return False
        sec = simpledialog.askstring("Spotify Client Secret", "Enter your SPOTIFY_CLIENT_SECRET:", parent=self, show="*")
        if not sec:
            return False
        os.environ["SPOTIFY_CLIENT_ID"] = cid.strip()
        os.environ["SPOTIFY_CLIENT_SECRET"] = sec.strip()
        try:
            save_env_to_dotenv(cid.strip(), sec.strip(), ".env")
        except Exception:
            pass
        return True

    def on_fetch(self):
        if not self.ensure_credentials():
            self.status_var.set("Credentials are required.")
            return
        self.status_var.set("Fetching tracks...")
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        self._image_refs.clear()
        self._url_by_iid.clear()
        threading.Thread(target=self._fetch_worker, daemon=True).start()

    def _fetch_worker(self):
        try:
            artist_id = extract_artist_id(self.artist_var.get())
            cid = os.getenv("SPOTIFY_CLIENT_ID", "").strip()
            sec = os.getenv("SPOTIFY_CLIENT_SECRET", "").strip()
            token = get_client_credentials_token(cid, sec)
            market = (self.market_var.get() or "US").upper()
            if self.all_tracks_var.get():
                tracks = get_all_tracks_for_artist(artist_id, token, market=market)
            else:
                tracks = get_artist_top_tracks(artist_id, token, market=market)

            try:
                limit = int(self.limit_var.get())
            except Exception:
                limit = None
            if limit and limit > 0:
                tracks = tracks[:limit]

            self.after(0, lambda: self._populate(tracks, all_mode=self.all_tracks_var.get()))
        except Exception as e:
            self.after(0, lambda: self.status_var.set(f"Error: {e}"))

    def _populate(self, tracks: list, all_mode: bool = False):
        for tr in tracks:
            popularity = tr.get("popularity", 0)
            track_name = tr.get("name", "Unknown Track")
            album_name = (tr.get("album") or {}).get("name", "") or "Unknown Album"
            artists = ", ".join(a.get("name","") for a in tr.get("artists", [])) or "Unknown Artist"
            track_url = tr.get("external_urls", {}).get("spotify", "")

            images = (tr.get("album") or {}).get("images", [])
            img_url = images[-1]["url"] if images else None
            photo = image_from_url(img_url, size=self.art_size) if img_url else image_from_url("", size=self.art_size)

            iid = self.tree.insert("", "end", text="", image=photo, values=(popularity, track_name, album_name, artists))
            self._image_refs[iid] = photo
            self._url_by_iid[iid] = track_url

        mode_text = "all releases" if all_mode else "top tracks"
        self.status_var.set(f"Loaded {len(tracks)} {mode_text} (sorted by Spotify popularity).")

    def on_double_click(self, event):
        iid = self.tree.identify_row(event.y)
        if not iid:
            return
        url = self._url_by_iid.get(iid)
        if url:
            webbrowser.open(url)

def extract_artist_id(s: str) -> str:
    from urllib.parse import urlparse
    s = s.strip()
    if not s:
        raise ValueError("Artist link or ID is empty.")
    try:
        p = urlparse(s)
        if p.netloc.endswith("open.spotify.com"):
            parts = p.path.strip("/").split("/")
            if len(parts) >= 2 and parts[0] == "artist":
                return parts[1].split("?")[0]
    except Exception:
        pass
    return s

if __name__ == "__main__":
    app = App()
    app.mainloop()
