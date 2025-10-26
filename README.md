
# Spotify Top Tracks (Regional)
A desktop GUI that uses the **Spotify Web API** to list an artist’s top tracks for any chosen region.

---
## 1) Create a Spotify developer app (Web API)
1. Go to <https://developer.spotify.com/dashboard> and **Log in**.
2. Click **Create app** → give it any name/description.
3. For **APIs/SDKs**, select **Web API** only.
4. **Redirect URI** is **not required** for this app (Client Credentials flow).
   - The form will require one, however, so just use a placeholder like `http://127.0.0.1:8080/callback`.
5. Save the app and copy your **Client ID** and **Client Secret**. You will use these for your '.env' file.

> This project uses the **Client Credentials** grant (no user login). You do **not** need scopes
> or OAuth redirects for basic read-only endpoints like top tracks and metadata.

---
## 2) Local environment setup (Python version 3.8 to 3.12)

### Quick start
1. **Clone or download** this repository.
2. (Optional) Create and activate a **virtual environment**:
   ```bash
   # Windows PowerShell
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Windows CMD
   python -m venv venv
   .\venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Create a `.env` file** in the project folder (do NOT commit your secrets):
   ```env
   SPOTIFY_CLIENT_ID=your_client_id
   SPOTIFY_CLIENT_SECRET=your_client_secret
   ```
   The app will read this automatically. If `.env` is missing, it will prompt you on first run and save one.

---
## 3) Run the app
```bash
python spotify_top_tracks_gui.py
```

### How to use
1. Paste an **artist URL or ID** (e.g. `https://open.spotify.com/artist/4NJxtQzTTeO3ObGlBcxVAh`).
2. Set the **Market** (default `US`, others can be found at the end of the README).
3. Choose a mode:
   - **Top 10** — Uses Spotify's Top Tracks endpoint (always returns up to 10).
   - **All tracks (slow)** — Crawls the artist's releases and aggregates every track, sorted by popularity.
     Use **Max results** to cap how many rows you want.
4. **Double‑click** a track to open it on Spotify.
5. Columns are **resizable**. Row height is increased so album art is visible.

---
## 4) Notes & limitations
- Spotify’s public API does **not** provide raw play counts. This program displays **`popularity` (0–100)** instead.
- Tkinter Treeview can only show images in the **leftmost column**; album art is positioned there by design.
- For “All tracks”, the app calls:
  `/v1/artists/{id}/albums` → `/v1/albums/{id}/tracks` → batches of `/v1/tracks`
  (kept within normal API limits).

---
## 5) Troubleshooting
- **“Missing SPOTIFY_CLIENT_ID/SECRET”**: Ensure `.env` exists or env vars are set in the **same shell**.
- **401 Unauthorized when getting a token**:
  - Verify the **Client Secret** (no trailing spaces).
  - Ensure your app has **Web API** enabled.
- **No tracks shown**: Try a different **Market** (e.g., `GB`, `CA`) — availability can be region‑specific.

---
## 6) Files
- `spotify_top_tracks_gui.py` — the app
- `requirements.txt` — dependencies (`requests`, `Pillow`)
- `.env.example` — sample credentials file (copy to `.env` and fill in)
- `.gitignore` — excludes `.env`, venvs, and typical build artifacts
- `LICENSE` — MIT

---
## 7) Market IDs
| Code | Country                          |
| ---- | -------------------------------- |
| AD   | Andorra                          |
| AE   | United Arab Emirates             |
| AG   | Antigua and Barbuda              |
| AL   | Albania                          |
| AM   | Armenia                          |
| AO   | Angola                           |
| AR   | Argentina                        |
| AT   | Austria                          |
| AU   | Australia                        |
| AZ   | Azerbaijan                       |
| BA   | Bosnia and Herzegovina           |
| BB   | Barbados                         |
| BD   | Bangladesh                       |
| BE   | Belgium                          |
| BF   | Burkina Faso                     |
| BG   | Bulgaria                         |
| BH   | Bahrain                          |
| BI   | Burundi                          |
| BJ   | Benin                            |
| BN   | Brunei                           |
| BO   | Bolivia                          |
| BR   | Brazil                           |
| BS   | Bahamas                          |
| BT   | Bhutan                           |
| BW   | Botswana                         |
| BY   | Belarus                          |
| BZ   | Belize                           |
| CA   | Canada                           |
| CD   | DR Congo                         |
| CG   | Republic of the Congo            |
| CH   | Switzerland                      |
| CI   | Côte d’Ivoire (Ivory Coast)      |
| CL   | Chile                            |
| CM   | Cameroon                         |
| CO   | Colombia                         |
| CR   | Costa Rica                       |
| CV   | Cabo Verde (Cape Verde)          |
| CW   | Curaçao                          |
| CY   | Cyprus                           |
| CZ   | Czechia                          |
| DE   | Germany                          |
| DJ   | Djibouti                         |
| DK   | Denmark                          |
| DM   | Dominica                         |
| DO   | Dominican Republic               |
| DZ   | Algeria                          |
| EC   | Ecuador                          |
| EE   | Estonia                          |
| EG   | Egypt                            |
| ES   | Spain                            |
| ET   | Ethiopia                         |
| FI   | Finland                          |
| FJ   | Fiji                             |
| FM   | Micronesia                       |
| FR   | France                           |
| GA   | Gabon                            |
| GB   | United Kingdom                   |
| GD   | Grenada                          |
| GE   | Georgia                          |
| GH   | Ghana                            |
| GM   | Gambia                           |
| GN   | Guinea                           |
| GQ   | Equatorial Guinea                |
| GR   | Greece                           |
| GT   | Guatemala                        |
| GW   | Guinea-Bissau                    |
| GY   | Guyana                           |
| HK   | Hong Kong SAR                    |
| HN   | Honduras                         |
| HR   | Croatia                          |
| HT   | Haiti                            |
| HU   | Hungary                          |
| ID   | Indonesia                        |
| IE   | Ireland                          |
| IL   | Israel                           |
| IN   | India                            |
| IQ   | Iraq                             |
| IS   | Iceland                          |
| IT   | Italy                            |
| JM   | Jamaica                          |
| JO   | Jordan                           |
| JP   | Japan                            |
| KE   | Kenya                            |
| KG   | Kyrgyzstan                       |
| KH   | Cambodia                         |
| KI   | Kiribati                         |
| KM   | Comoros                          |
| KN   | Saint Kitts and Nevis            |
| KR   | South Korea (Republic of Korea)  |
| KW   | Kuwait                           |
| KZ   | Kazakhstan                       |
| LA   | Laos (Lao PDR)                   |
| LB   | Lebanon                          |
| LC   | Saint Lucia                      |
| LI   | Liechtenstein                    |
| LK   | Sri Lanka                        |
| LR   | Liberia                          |
| LS   | Lesotho                          |
| LT   | Lithuania                        |
| LU   | Luxembourg                       |
| LV   | Latvia                           |
| LY   | Libya                            |
| MA   | Morocco                          |
| MC   | Monaco                           |
| MD   | Moldova                          |
| ME   | Montenegro                       |
| MG   | Madagascar                       |
| MH   | Marshall Islands                 |
| MK   | North Macedonia                  |
| ML   | Mali                             |
| MN   | Mongolia                         |
| MO   | Macao SAR                        |
| MR   | Mauritania                       |
| MT   | Malta                            |
| MU   | Mauritius                        |
| MV   | Maldives                         |
| MW   | Malawi                           |
| MX   | Mexico                           |
| MY   | Malaysia                         |
| MZ   | Mozambique                       |
| NA   | Namibia                          |
| NE   | Niger                            |
| NG   | Nigeria                          |
| NI   | Nicaragua                        |
| NL   | Netherlands                      |
| NO   | Norway                           |
| NP   | Nepal                            |
| NR   | Nauru                            |
| NZ   | New Zealand                      |
| OM   | Oman                             |
| PA   | Panama                           |
| PE   | Peru                             |
| PG   | Papua New Guinea                 |
| PH   | Philippines                      |
| PK   | Pakistan                         |
| PL   | Poland                           |
| PR   | Puerto Rico                      |
| PS   | Palestine                        |
| PT   | Portugal                         |
| PW   | Palau                            |
| PY   | Paraguay                         |
| QA   | Qatar                            |
| RO   | Romania                          |
| RS   | Serbia                           |
| RW   | Rwanda                           |
| SA   | Saudi Arabia                     |
| SB   | Solomon Islands                  |
| SC   | Seychelles                       |
| SE   | Sweden                           |
| SG   | Singapore                        |
| SI   | Slovenia                         |
| SK   | Slovakia                         |
| SL   | Sierra Leone                     |
| SM   | San Marino                       |
| SN   | Senegal                          |
| SR   | Suriname                         |
| ST   | São Tomé and Príncipe            |
| SV   | El Salvador                      |
| SZ   | Eswatini                         |
| TD   | Chad                             |
| TG   | Togo                             |
| TH   | Thailand                         |
| TJ   | Tajikistan                       |
| TL   | Timor-Leste                      |
| TN   | Tunisia                          |
| TO   | Tonga                            |
| TR   | Türkiye (Turkey)                 |
| TT   | Trinidad and Tobago              |
| TV   | Tuvalu                           |
| TW   | Taiwan                           |
| TZ   | Tanzania                         |
| UA   | Ukraine                          |
| UG   | Uganda                           |
| US   | United States                    |
| UY   | Uruguay                          |
| UZ   | Uzbekistan                       |
| VC   | Saint Vincent and the Grenadines |
| VE   | Venezuela                        |
| VN   | Vietnam                          |
| VU   | Vanuatu                          |
| WS   | Samoa                            |
| XK   | Kosovo*                          |
| ZA   | South Africa                     |
| ZM   | Zambia                           |
| ZW   | Zimbabwe                         |

* `XK` isn’t an official ISO code, but Spotify commonly uses it for Kosovo.

---
## 8) License
MIT — see [LICENSE](LICENSE).
