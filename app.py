import streamlit as st
import requests
import pandas as pd
from datetime import date
import plotly.express as px
from google.oauth2.service_account import Credentials
import gspread

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sandra · Media Tracker",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] { background: #18181b; border-right: 1px solid #27272a; }
section[data-testid="stSidebar"] * { color: #f4f4f5 !important; }
section[data-testid="stSidebar"] label {
    color: #a1a1aa !important; font-size: 0.7rem;
    text-transform: uppercase; letter-spacing: 0.1em;
}

/* ── Background ── */
.main, [data-testid="stAppViewContainer"] { background: #f0f0ff; }

/* ── Header ── */
.page-header {
    background: linear-gradient(135deg, #6d28d9 0%, #7c3aed 40%, #db2777 100%);
    padding: 2rem 2.5rem 1.8rem;
    border-radius: 20px;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(109,40,217,0.3);
}
.page-header::before {
    content: '✨';
    position: absolute; right: 1.5rem; top: 50%;
    transform: translateY(-50%);
    font-size: 5rem; opacity: 0.15;
}
.page-header h1 {
    font-family: 'Nunito', sans-serif;
    font-size: 2.2rem; font-weight: 900;
    color: white; margin: 0 0 0.2rem;
    letter-spacing: -0.02em;
}
.page-header .subtitle {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem; color: #e9d5ff;
    letter-spacing: 0.1em; text-transform: uppercase;
}

/* ── Metric cards ── */
.metric-card {
    background: white; border-radius: 16px;
    padding: 1.2rem 1.4rem;
    border: none;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}
.metric-card .label {
    font-size: 0.65rem; text-transform: uppercase;
    letter-spacing: 0.1em; color: #71717a; margin-bottom: 0.4rem;
    font-family: 'DM Mono', monospace;
}
.metric-card .value {
    font-size: 2rem; font-weight: 900;
    color: #18181b; line-height: 1;
}

/* ── Section titles ── */
.section-title {
    font-size: 1.1rem; font-weight: 800;
    color: #18181b; margin: 1.5rem 0 0.8rem;
    display: flex; align-items: center; gap: 0.5rem;
}

/* ── Book / Series card ── */
.media-card {
    background: white;
    border-radius: 16px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.7rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.07);
    border-left: 5px solid #6d28d9;
    position: relative;
}
.media-card.status-read, .media-card.status-watched {
    border-left-color: #16a34a;
}
.media-card.status-reading, .media-card.status-watching {
    border-left-color: #2563eb;
}
.media-card.status-wishlist {
    border-left-color: #d97706;
}
.media-card.status-abandoned, .media-card.status-dropped {
    border-left-color: #dc2626;
}
.media-card.status-paused {
    border-left-color: #db2777;
}
.media-card-title {
    font-size: 1rem; font-weight: 800;
    color: #18181b; margin-bottom: 0.15rem;
    line-height: 1.3;
}
.media-card-sub {
    font-size: 0.8rem; color: #71717a;
    margin-bottom: 0.5rem; font-weight: 600;
}
.media-card-tags {
    display: flex; flex-wrap: wrap; gap: 0.4rem;
    margin-bottom: 0.5rem;
}
.tag {
    display: inline-block; padding: 2px 10px;
    border-radius: 20px; font-size: 0.7rem;
    font-weight: 700; letter-spacing: 0.03em;
}
.tag-genre   { background: #ede9fe; color: #5b21b6; }
.tag-status-read, .tag-status-watched  { background: #dcfce7; color: #166534; }
.tag-status-reading, .tag-status-watching { background: #dbeafe; color: #1e40af; }
.tag-status-wishlist  { background: #fef9c3; color: #92400e; }
.tag-status-abandoned, .tag-status-dropped { background: #fee2e2; color: #991b1b; }
.tag-status-paused    { background: #fce7f3; color: #9d174d; }
.tag-platform { background: #f0fdf4; color: #166534; }
.media-card-stars { color: #f59e0b; font-size: 0.95rem; letter-spacing: 1px; }
.media-card-review {
    font-size: 0.82rem; color: #52525b;
    font-style: italic; margin-top: 0.4rem;
    border-top: 1px solid #f4f4f5; padding-top: 0.4rem;
    line-height: 1.5;
}
.reread-badge {
    font-size: 0.72rem; color: #7c3aed;
    font-weight: 700;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #6d28d9, #7c3aed) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    padding: 0.45rem 1.4rem !important;
    transition: all 0.2s !important;
    box-shadow: 0 2px 8px rgba(109,40,217,0.25) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 16px rgba(109,40,217,0.35) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab"] {
    font-family: 'Nunito', sans-serif;
    font-size: 0.9rem; font-weight: 700;
}
.stTabs [aria-selected="true"] {
    color: #6d28d9 !important;
}

/* ── Inputs ── */
.stTextInput input, .stTextArea textarea {
    border-color: #e4e4e7 !important;
    border-radius: 10px !important;
    font-family: 'Nunito', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

# ── Constants ──────────────────────────────────────────────────────────────────
SPREADSHEET_NAME = "MediaTracker"

BOOK_COLS = ["title","author","genre","status","rating","date_finished",
             "reread","review","notes","cover_url"]
SERIES_COLS = ["title","creator","genre","status","rating","platform",
               "seasons","date_finished","rewatch","review","notes","poster_url"]

BOOK_GENRES   = ["Fiction","Literary Fiction","Fantasy","Sci-Fi","Mystery/Thriller",
                 "Romance","Historical Fiction","Non-Fiction","Biography/Memoir",
                 "Self-Help","Business","Science","History","Philosophy","Other"]
SERIES_GENRES = ["Drama","Comedy","Crime/Thriller","Sci-Fi","Fantasy","Horror",
                 "Romance","Documentary","Reality","Anime","Action","Historical","Other"]

BOOK_STATUS   = ["Read","Currently Reading","Wishlist","Abandoned"]
SERIES_STATUS = ["Watched","Currently Watching","Wishlist","Paused","Dropped"]

PLATFORMS = ["Netflix","Prime Video","Showmax","Disney+","Apple TV+","HBO Max",
             "Hulu","YouTube","DSTV","Physical/DVD","Other"]

RATINGS = ["⭐⭐⭐⭐⭐ (5)","⭐⭐⭐⭐ (4)","⭐⭐⭐ (3)","⭐⭐ (2)","⭐ (1)","Not rated"]

STATUS_PILL = {
    "Read":"pill-read","Currently Reading":"pill-reading",
    "Wishlist":"pill-wishlist","Abandoned":"pill-abandoned",
    "Watched":"pill-watched","Currently Watching":"pill-watching",
    "Paused":"pill-paused","Dropped":"pill-dropped",
}

# ── Auto-lookup helpers ────────────────────────────────────────────────────────
def search_books(query):
    """Search Open Library — no key needed."""
    try:
        r = requests.get(
            "https://openlibrary.org/search.json",
            params={"q": query, "limit": 6, "fields": "key,title,author_name,subject,cover_i,first_publish_year"},
            timeout=8
        )
        docs = r.json().get("docs", [])
        results = []
        for d in docs:
            cover = f"https://covers.openlibrary.org/b/id/{d['cover_i']}-L.jpg" if d.get("cover_i") else ""
            results.append({
                "title":      d.get("title",""),
                "author":     ", ".join(d.get("author_name", [])[:2]),
                "genre":      d.get("subject", [""])[0][:40] if d.get("subject") else "",
                "cover_url":  cover,
                "year":       str(d.get("first_publish_year","")),
            })
        return results
    except Exception:
        return []


def search_series(query):
    """Search TMDB — free API key."""
    try:
        token = st.secrets["tmdb"]["token"]
        r = requests.get(
            "https://api.themoviedb.org/3/search/tv",
            params={"query": query, "page": 1},
            headers={"Authorization": f"Bearer {token}"},
            timeout=8
        )
        items = r.json().get("results", [])[:6]
        results = []
        for d in items:
            poster = f"https://image.tmdb.org/t/p/w500{d['poster_path']}" if d.get("poster_path") else ""
            results.append({
                "title":      d.get("name",""),
                "first_air":  d.get("first_air_date","")[:4],
                "overview":   d.get("overview","")[:120],
                "poster_url": poster,
                "genre_ids":  d.get("genre_ids",[]),
                "id":         d.get("id"),
            })
        return results
    except Exception:
        return []


TMDB_GENRES = {
    10759:"Action", 16:"Anime", 35:"Comedy", 80:"Crime/Thriller",
    99:"Documentary", 18:"Drama", 10751:"Drama", 10762:"Drama",
    9648:"Mystery/Thriller", 10763:"Drama", 10764:"Reality",
    10765:"Sci-Fi", 10766:"Romance", 10767:"Drama", 10768:"Drama",
    37:"Drama"
}

def tmdb_genre(genre_ids):
    for gid in genre_ids:
        if gid in TMDB_GENRES:
            return TMDB_GENRES[gid]
    return "Other"

def ol_genre_to_app(raw):
    """Map Open Library subject to our genre list."""
    raw = raw.lower()
    mapping = {
        "fiction": "Fiction", "romance": "Romance", "fantasy": "Fantasy",
        "science fiction": "Sci-Fi", "mystery": "Mystery/Thriller",
        "thriller": "Mystery/Thriller", "historical": "Historical Fiction",
        "biography": "Biography/Memoir", "memoir": "Biography/Memoir",
        "self-help": "Self-Help", "business": "Business",
        "science": "Science", "history": "History",
        "philosophy": "Philosophy", "non-fiction": "Non-Fiction",
    }
    for key, val in mapping.items():
        if key in raw:
            return val
    return "Fiction"


# ── Google Sheets ──────────────────────────────────────────────────────────────
@st.cache_resource
def get_sheets():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"]
    )
    gc = gspread.authorize(creds)
    sh = gc.open(SPREADSHEET_NAME)
    return {
        "books":  sh.worksheet("Books"),
        "series": sh.worksheet("Series"),
    }


def load(sheet_key):
    try:
        ws = get_sheets()[sheet_key]
        return ws.get_all_records()
    except Exception as e:
        st.error(f"Could not load data: {e}")
        return []


def save_all(sheet_key, data, cols):
    ws = get_sheets()[sheet_key]
    ws.clear()
    ws.append_row(cols)
    if data:
        rows = [[str(d.get(c,"")) for c in cols] for d in data]
        ws.append_rows(rows, value_input_option="USER_ENTERED")


def to_df(data, cols):
    if not data:
        return pd.DataFrame(columns=cols)
    df = pd.DataFrame(data)
    for c in cols:
        if c not in df.columns:
            df[c] = ""
    return df


def stars(r):
    if not r or r == "Not rated":
        return "—"
    n = int(r[0]) if r and r[0].isdigit() else 0
    return "★" * n + "☆" * (5 - n)


# ── Session state ──────────────────────────────────────────────────────────────
for key, loader in [("books", "books"), ("series", "series")]:
    if key not in st.session_state:
        with st.spinner(f"Loading {key}…"):
            st.session_state[key] = load(loader)
for key in ["edit_book", "edit_series"]:
    if key not in st.session_state:
        st.session_state[key] = None

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 Filters")
    sb_type   = st.radio("Section", ["📚 Books", "📺 TV Series"], label_visibility="collapsed")
    st.markdown("---")
    if "Books" in sb_type:
        f_status = st.multiselect("Status", BOOK_STATUS,   default=BOOK_STATUS)
        f_genre  = st.multiselect("Genre",  BOOK_GENRES,   default=BOOK_GENRES)
    else:
        f_status = st.multiselect("Status",   SERIES_STATUS, default=SERIES_STATUS)
        f_genre  = st.multiselect("Genre",    SERIES_GENRES, default=SERIES_GENRES)
        f_platform = st.multiselect("Platform", PLATFORMS,   default=PLATFORMS)
    f_search = st.text_input("Search title / creator", "")
    st.markdown("---")
    if st.button("🔄 Refresh"):
        for k in ["books","series"]:
            st.session_state[k] = load(k)
        st.rerun()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <h1>✨ My Media Tracker</h1>
  <div class="subtitle">Sandra · Books &amp; TV Series · Personal Library</div>
</div>
""", unsafe_allow_html=True)

# ── Top-level tabs ─────────────────────────────────────────────────────────────
book_tab, series_tab = st.tabs(["📚  Books", "📺  TV Series"])


# ═══════════════════════════════════════════════════════════════════════════════
# BOOKS
# ═══════════════════════════════════════════════════════════════════════════════
with book_tab:
    books = st.session_state.books

    # Metrics
    total_b   = len(books)
    read_b    = sum(1 for b in books if b.get("status") == "Read")
    reading_b = sum(1 for b in books if b.get("status") == "Currently Reading")
    wish_b    = sum(1 for b in books if b.get("status") == "Wishlist")
    def safe_rating(r):
        val = str(r.get("rating",""))
        return int(val[0]) if val and val[0].isdigit() else None

    rated  = [b for b in books if safe_rating(b) is not None]
    avg_b  = f"{sum(safe_rating(r) for r in rated)/len(rated):.1f} ★" if rated else "—"

    c1,c2,c3,c4,c5 = st.columns(5)
    for col, lbl, val in zip([c1,c2,c3,c4,c5],
        ["Total Books","Read","Reading Now","Wishlist","Avg Rating"],
        [total_b, read_b, reading_b, wish_b, avg_b]):
        col.markdown(f'<div class="metric-card"><div class="label">{lbl}</div><div class="value">{val}</div></div>', unsafe_allow_html=True)

    st.markdown("")
    btab1, btab2, btab3 = st.tabs(["📖  Library", "➕  Add / Edit", "📊  Stats"])

    # ── BOOKS — Library ──────────────────────────────────────────────────────
    with btab1:
        filtered_b = [b for b in books
                      if b.get("status","") in f_status
                      and b.get("genre","")  in f_genre
                      and (f_search.lower() in b.get("title","").lower()
                           or f_search.lower() in b.get("author","").lower())]

        if not filtered_b:
            st.info("No books match your filters. Add one in ➕!")
        else:
            # Group by status
            for status in BOOK_STATUS:
                group = [b for b in filtered_b if b.get("status") == status]
                if not group:
                    continue
                emoji = {"Read":"✅","Currently Reading":"📖","Wishlist":"🔖","Abandoned":"🚫"}.get(status,"")
                st.markdown(f'<div class="section-title">{emoji} {status} <span style="font-family:DM Mono,monospace;font-size:0.8rem;color:#a87d52;">({len(group)})</span></div>', unsafe_allow_html=True)

                for b in group:
                    orig_idx = next((i for i,x in enumerate(books)
                                     if x.get("title")==b.get("title") and x.get("author")==b.get("author")), None)
                    star_str = stars(b.get("rating",""))
                    reread   = str(b.get("reread","")).lower() in ["true","yes","1"]
                    status_cls = b.get("status","wishlist").lower().replace(" ","")
                    genre_tag  = f'<span class="tag tag-genre">{b.get("genre","")}</span>' if b.get("genre") else ""
                    st_key     = b.get("status","").lower().replace(" ","")
                    status_tag = f'<span class="tag tag-status-{st_key}">{b.get("status","")}</span>'
                    reread_html = '<div class="reread-badge">🔁 Would re-read</div>' if reread else ""
                    review_html = f'<div class="media-card-review">"{b["review"]}"</div>' if b.get("review") else ""
                    date_str    = f'📅 {b["date_finished"]}' if b.get("date_finished") else ""
                    st.markdown(f'''
                    <div class="media-card status-{status_cls}">
                      <div class="media-card-title">📖 {b.get("title","Untitled")}</div>
                      <div class="media-card-sub">{b.get("author","Unknown")} {f"· {date_str}" if date_str else ""}</div>
                      <div class="media-card-tags">{genre_tag}{status_tag}</div>
                      <div class="media-card-stars">{star_str}</div>
                      {reread_html}{review_html}
                    </div>''', unsafe_allow_html=True)
                    if orig_idx is not None:
                        ca, cb = st.columns([1,1])
                        with ca:
                            if st.button("✏️ Edit", key=f"eb_{orig_idx}"):
                                st.session_state.edit_book = orig_idx
                                st.rerun()
                        with cb:
                            if st.button("🗑️ Delete", key=f"db_{orig_idx}"):
                                st.session_state.books.pop(orig_idx)
                                with st.spinner("Saving…"):
                                    save_all("books", st.session_state.books, BOOK_COLS)
                                st.rerun()

    # ── BOOKS — Add / Edit ───────────────────────────────────────────────────
    with btab2:
        ei = st.session_state.edit_book
        ex = books[ei] if ei is not None else {}
        mode = "Edit Book" if ei is not None else "Add a Book"
        st.markdown(f'<div class="section-title">{"✏️" if ei else "➕"} {mode}</div>', unsafe_allow_html=True)

        if ei is not None:
            if st.button("← Cancel", key="cancel_b"):
                st.session_state.edit_book = None
                st.rerun()

        # ── Search bar ──
        if ei is None:
            st.markdown("**🔍 Search to auto-fill** *(powered by Open Library)*")
            bsearch_col, bsearch_btn = st.columns([4,1])
            with bsearch_col:
                bquery = st.text_input("Search by title or author", placeholder="e.g. Charming Puckboy, Eden Finley...", key="b_search_query", label_visibility="collapsed")
            with bsearch_btn:
                do_bsearch = st.button("Search", key="b_search_btn")

            if do_bsearch and bquery:
                with st.spinner("Searching Open Library…"):
                    st.session_state.b_search_results = search_books(bquery)

            results = st.session_state.get("b_search_results", [])
            if results:
                st.markdown("**Pick a result to auto-fill the form:**")
                for i, res in enumerate(results):
                    rcol1, rcol2 = st.columns([1,5])
                    with rcol1:
                        if res.get("cover_url"):
                            st.image(res["cover_url"], width=55)
                        else:
                            st.markdown("📖")
                    with rcol2:
                        st.markdown(f"**{res['title']}**  \n*{res['author']}* {f'({res['year']})' if res.get('year') else ''}")
                        if st.button("Use this", key=f"bpick_{i}"):
                            st.session_state.b_prefill = res
                            st.session_state.b_search_results = []
                            st.rerun()
                st.markdown("---")

        # ── Pre-fill from search result ──
        pf = st.session_state.get("b_prefill", {}) if ei is None else {}
        def bv(field, fallback=""):
            return pf.get(field, ex.get(field, fallback))

        # Show cover preview if available
        cover_default = bv("cover_url")
        if cover_default:
            st.image(cover_default, width=100, caption="Cover found ✅")

        c1, c2 = st.columns(2)
        with c1:
            title  = st.text_input("Title *",  value=bv("title"),  key="b_title")
            author = st.text_input("Author *", value=bv("author"), key="b_author")
            raw_genre = ol_genre_to_app(bv("genre")) if bv("genre") else BOOK_GENRES[0]
            genre  = st.selectbox("Genre", BOOK_GENRES,
                                  index=BOOK_GENRES.index(raw_genre) if raw_genre in BOOK_GENRES else 0,
                                  key="b_genre")
            status = st.selectbox("Status", BOOK_STATUS,
                                  index=BOOK_STATUS.index(ex["status"]) if ex.get("status") in BOOK_STATUS else 2,
                                  key="b_status")
        with c2:
            rating = st.selectbox("Rating", RATINGS,
                                  index=RATINGS.index(ex["rating"]) if ex.get("rating") in RATINGS else 5,
                                  key="b_rating")
            raw_d  = ex.get("date_finished","")
            d_val  = date.fromisoformat(str(raw_d)[:10]) if raw_d else date.today()
            date_f = st.date_input("Date finished", value=d_val, key="b_date")
            reread = st.checkbox("Would re-read", value=str(ex.get("reread","")).lower() in ["true","yes","1"],
                                 key="b_reread")
            cover  = st.text_input("Cover image URL", value=cover_default, key="b_cover")

        review = st.text_area("Review",  value=ex.get("review",""), height=80, key="b_review")
        notes  = st.text_area("Notes",   value=ex.get("notes",""),  height=60, key="b_notes")

        if st.button("💾 Save Book", key="b_save"):
            if not title or not author:
                st.error("Title and Author are required.")
            else:
                entry = {"title":title,"author":author,"genre":genre,"status":status,
                         "rating":rating,"date_finished":str(date_f),"reread":str(reread),
                         "review":review,"notes":notes,"cover_url":cover}
                if ei is not None:
                    st.session_state.books[ei] = entry
                    st.session_state.edit_book = None
                else:
                    st.session_state.books.append(entry)
                    st.session_state.b_prefill = {}
                    st.session_state.b_search_results = []
                with st.spinner("Saving to Google Sheets…"):
                    save_all("books", st.session_state.books, BOOK_COLS)
                st.success("✅ Saved!")
                st.rerun()

    # ── BOOKS — Stats ────────────────────────────────────────────────────────
    with btab3:
        if not books:
            st.info("Add some books to see stats!")
        else:
            df_b = to_df(books, BOOK_COLS)
            c1, c2 = st.columns(2)
            with c1:
                sc = df_b["status"].value_counts().reset_index()
                sc.columns = ["Status","Count"]
                fig = px.pie(sc, names="Status", values="Count", hole=0.55,
                             title="Books by Status",
                             color_discrete_sequence=["#c8860a","#1a0a00","#e8a020","#f5e6d0","#a87d52"])
                fig.update_layout(font_family="Crimson Pro", paper_bgcolor="rgba(0,0,0,0)",
                                  plot_bgcolor="rgba(0,0,0,0)", title_font_size=14,
                                  margin=dict(t=40,b=0,l=0,r=0))
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                gc_ = df_b["genre"].value_counts().reset_index()
                gc_.columns = ["Genre","Count"]
                fig2 = px.bar(gc_, x="Count", y="Genre", orientation="h",
                              title="Books by Genre",
                              color_discrete_sequence=["#1a0a00"])
                fig2.update_layout(font_family="Crimson Pro", paper_bgcolor="rgba(0,0,0,0)",
                                   plot_bgcolor="rgba(0,0,0,0)", title_font_size=14,
                                   yaxis=dict(categoryorder="total ascending"),
                                   margin=dict(t=40,b=0,l=0,r=10))
                st.plotly_chart(fig2, use_container_width=True)

            rated_df = df_b[df_b["rating"].apply(lambda x: bool(x) and x != "Not rated")]
            if not rated_df.empty:
                rated_df = rated_df.copy()
                rated_df["stars"] = rated_df["rating"].apply(lambda x: int(x[0]) if x and x[0].isdigit() else 0)
                rc = rated_df["stars"].value_counts().sort_index().reset_index()
                rc.columns = ["Stars","Count"]
                rc["label"] = rc["Stars"].apply(lambda x: "★"*x)
                fig3 = px.bar(rc, x="label", y="Count", title="Rating Distribution",
                              color_discrete_sequence=["#c8860a"])
                fig3.update_layout(font_family="Crimson Pro", paper_bgcolor="rgba(0,0,0,0)",
                                   plot_bgcolor="rgba(0,0,0,0)", title_font_size=14,
                                   xaxis_title="", margin=dict(t=40,b=0,l=0,r=0))
                st.plotly_chart(fig3, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TV SERIES
# ═══════════════════════════════════════════════════════════════════════════════
with series_tab:
    series = st.session_state.series

    total_s   = len(series)
    watched_s = sum(1 for s in series if s.get("status") == "Watched")
    watching_s= sum(1 for s in series if s.get("status") == "Currently Watching")
    wish_s    = sum(1 for s in series if s.get("status") == "Wishlist")
    rated_s = [s for s in series if safe_rating(s) is not None]
    avg_s   = f"{sum(safe_rating(r) for r in rated_s)/len(rated_s):.1f} ★" if rated_s else "—"

    c1,c2,c3,c4,c5 = st.columns(5)
    for col, lbl, val in zip([c1,c2,c3,c4,c5],
        ["Total Series","Watched","Watching Now","Wishlist","Avg Rating"],
        [total_s, watched_s, watching_s, wish_s, avg_s]):
        col.markdown(f'<div class="metric-card"><div class="label">{lbl}</div><div class="value">{val}</div></div>', unsafe_allow_html=True)

    st.markdown("")
    stab1, stab2, stab3 = st.tabs(["📺  My List", "➕  Add / Edit", "📊  Stats"])

    # ── SERIES — My List ─────────────────────────────────────────────────────
    with stab1:
        filtered_s = [s for s in series
                      if s.get("status","")   in f_status
                      and s.get("genre","")   in f_genre
                      and s.get("platform","") in (f_platform if "TV" in sb_type else PLATFORMS)
                      and (f_search.lower() in s.get("title","").lower()
                           or f_search.lower() in s.get("creator","").lower())]

        if not filtered_s:
            st.info("No series match your filters. Add one in ➕!")
        else:
            for status in SERIES_STATUS:
                group = [s for s in filtered_s if s.get("status") == status]
                if not group:
                    continue
                emoji = {"Watched":"✅","Currently Watching":"📺","Wishlist":"🔖",
                         "Paused":"⏸️","Dropped":"🚫"}.get(status,"")
                st.markdown(f'<div class="section-title">{emoji} {status} <span style="font-family:DM Mono,monospace;font-size:0.8rem;color:#a87d52;">({len(group)})</span></div>', unsafe_allow_html=True)

                for s in group:
                    orig_idx = next((i for i,x in enumerate(series)
                                     if x.get("title")==s.get("title") and x.get("creator")==s.get("creator")), None)
                    star_str  = stars(s.get("rating",""))
                    rewatch   = str(s.get("rewatch","")).lower() in ["true","yes","1"]
                    status_cls = s.get("status","wishlist").lower().replace(" ","")
                    st_key     = s.get("status","").lower().replace(" ","")
                    genre_tag  = f'<span class="tag tag-genre">{s.get("genre","")}</span>' if s.get("genre") else ""
                    status_tag = f'<span class="tag tag-status-{st_key}">{s.get("status","")}</span>'
                    plat_tag   = f'<span class="tag tag-platform">📺 {s["platform"]}</span>' if s.get("platform") else ""
                    seasons_str = f'S{s["seasons"]}' if s.get("seasons") and str(s["seasons"]) not in ["0",""] else ""
                    rewatch_html = '<div class="reread-badge">🔁 Would rewatch</div>' if rewatch else ""
                    review_html  = f'<div class="media-card-review">"{s["review"]}"</div>' if s.get("review") else ""
                    date_str     = f'📅 {s["date_finished"]}' if s.get("date_finished") else ""
                    st.markdown(f'''
                    <div class="media-card status-{status_cls}">
                      <div class="media-card-title">🎬 {s.get("title","Untitled")}</div>
                      <div class="media-card-sub">{s.get("creator","Unknown")} {f"· {seasons_str}" if seasons_str else ""} {f"· {date_str}" if date_str else ""}</div>
                      <div class="media-card-tags">{genre_tag}{status_tag}{plat_tag}</div>
                      <div class="media-card-stars">{star_str}</div>
                      {rewatch_html}{review_html}
                    </div>''', unsafe_allow_html=True)
                    if orig_idx is not None:
                        ca, cb = st.columns([1,1])
                        with ca:
                            if st.button("✏️ Edit", key=f"es_{orig_idx}"):
                                st.session_state.edit_series = orig_idx
                                st.rerun()
                        with cb:
                            if st.button("🗑️ Delete", key=f"ds_{orig_idx}"):
                                st.session_state.series.pop(orig_idx)
                                with st.spinner("Saving…"):
                                    save_all("series", st.session_state.series, SERIES_COLS)
                                st.rerun()

    # ── SERIES — Add / Edit ──────────────────────────────────────────────────
    with stab2:
        ei = st.session_state.edit_series
        ex = series[ei] if ei is not None else {}
        mode = "Edit Series" if ei is not None else "Add a Series"
        st.markdown(f'<div class="section-title">{"✏️" if ei else "➕"} {mode}</div>', unsafe_allow_html=True)

        if ei is not None:
            if st.button("← Cancel", key="cancel_s"):
                st.session_state.edit_series = None
                st.rerun()

        # ── Search bar ──
        if ei is None:
            st.markdown("**🔍 Search to auto-fill** *(powered by TMDB)*")
            ssearch_col, ssearch_btn = st.columns([4,1])
            with ssearch_col:
                squery = st.text_input("Search by title", placeholder="e.g. Bridgerton, The Bear, Suits...", key="s_search_query", label_visibility="collapsed")
            with ssearch_btn:
                do_ssearch = st.button("Search", key="s_search_btn")

            if do_ssearch and squery:
                with st.spinner("Searching TMDB…"):
                    st.session_state.s_search_results = search_series(squery)

            sresults = st.session_state.get("s_search_results", [])
            if sresults:
                st.markdown("**Pick a result to auto-fill the form:**")
                for i, res in enumerate(sresults):
                    rcol1, rcol2 = st.columns([1,5])
                    with rcol1:
                        if res.get("poster_url"):
                            st.image(res["poster_url"], width=55)
                        else:
                            st.markdown("📺")
                    with rcol2:
                        st.markdown(f"**{res['title']}** {f'({res['first_air']})' if res.get('first_air') else ''} \n{res.get('overview','')}")
                        if st.button("Use this", key=f"spick_{i}"):
                            st.session_state.s_prefill = res
                            st.session_state.s_search_results = []
                            st.rerun()
                st.markdown("---")

        # ── Pre-fill from search result ──
        spf = st.session_state.get("s_prefill", {}) if ei is None else {}
        def sv(field, fallback=""):
            return spf.get(field, ex.get(field, fallback))

        poster_default = sv("poster_url")
        if poster_default:
            st.image(poster_default, width=100, caption="Poster found ✅")

        c1, c2 = st.columns(2)
        with c1:
            title   = st.text_input("Title *", value=sv("title"), key="s_title")
            creator = st.text_input("Creator / Showrunner", value=ex.get("creator",""), key="s_creator")
            raw_sg  = tmdb_genre(spf.get("genre_ids",[])) if spf.get("genre_ids") else ex.get("genre", SERIES_GENRES[0])
            genre   = st.selectbox("Genre", SERIES_GENRES,
                                   index=SERIES_GENRES.index(raw_sg) if raw_sg in SERIES_GENRES else 0,
                                   key="s_genre")
            status  = st.selectbox("Status", SERIES_STATUS,
                                   index=SERIES_STATUS.index(ex["status"]) if ex.get("status") in SERIES_STATUS else 2,
                                   key="s_status")
        with c2:
            rating   = st.selectbox("Rating", RATINGS,
                                    index=RATINGS.index(ex["rating"]) if ex.get("rating") in RATINGS else 5,
                                    key="s_rating")
            platform = st.selectbox("Platform", PLATFORMS,
                                    index=PLATFORMS.index(ex["platform"]) if ex.get("platform") in PLATFORMS else 0,
                                    key="s_platform")
            seasons  = st.number_input("Seasons watched", min_value=0, max_value=50,
                                       value=int(ex.get("seasons",0) or 0), key="s_seasons")
            raw_d    = ex.get("date_finished","")
            d_val    = date.fromisoformat(str(raw_d)[:10]) if raw_d else date.today()
            date_f   = st.date_input("Date finished", value=d_val, key="series_date")
            rewatch  = st.checkbox("Would rewatch", value=str(ex.get("rewatch","")).lower() in ["true","yes","1"],
                                   key="s_rewatch")

        poster = st.text_input("Poster image URL", value=poster_default, key="s_poster")
        review = st.text_area("Review", value=ex.get("review",""), height=80, key="s_review")
        notes  = st.text_area("Notes",  value=ex.get("notes",""),  height=60, key="s_notes")

        if st.button("💾 Save Series", key="s_save"):
            if not title:
                st.error("Title is required.")
            else:
                entry = {"title":title,"creator":creator,"genre":genre,"status":status,
                         "rating":rating,"platform":platform,"seasons":str(seasons),
                         "date_finished":str(date_f),"rewatch":str(rewatch),
                         "review":review,"notes":notes,"poster_url":poster}
                if ei is not None:
                    st.session_state.series[ei] = entry
                    st.session_state.edit_series = None
                else:
                    st.session_state.series.append(entry)
                    st.session_state.s_prefill = {}
                    st.session_state.s_search_results = []
                with st.spinner("Saving to Google Sheets…"):
                    save_all("series", st.session_state.series, SERIES_COLS)
                st.success("✅ Saved!")
                st.rerun()

    # ── SERIES — Stats ───────────────────────────────────────────────────────
    with stab3:
        if not series:
            st.info("Add some series to see stats!")
        else:
            df_s = to_df(series, SERIES_COLS)
            c1, c2 = st.columns(2)
            with c1:
                sc = df_s["status"].value_counts().reset_index()
                sc.columns = ["Status","Count"]
                fig = px.pie(sc, names="Status", values="Count", hole=0.55,
                             title="Series by Status",
                             color_discrete_sequence=["#c8860a","#1a0a00","#e8a020","#f5e6d0","#a87d52"])
                fig.update_layout(font_family="Crimson Pro", paper_bgcolor="rgba(0,0,0,0)",
                                  plot_bgcolor="rgba(0,0,0,0)", title_font_size=14,
                                  margin=dict(t=40,b=0,l=0,r=0))
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                gc_ = df_s["genre"].value_counts().reset_index()
                gc_.columns = ["Genre","Count"]
                fig2 = px.bar(gc_, x="Count", y="Genre", orientation="h",
                              title="Series by Genre",
                              color_discrete_sequence=["#1a0a00"])
                fig2.update_layout(font_family="Crimson Pro", paper_bgcolor="rgba(0,0,0,0)",
                                   plot_bgcolor="rgba(0,0,0,0)", title_font_size=14,
                                   yaxis=dict(categoryorder="total ascending"),
                                   margin=dict(t=40,b=0,l=0,r=10))
                st.plotly_chart(fig2, use_container_width=True)

            pc = df_s["platform"].value_counts().reset_index()
            pc.columns = ["Platform","Count"]
            fig3 = px.bar(pc, x="Platform", y="Count", title="Series by Platform",
                          color_discrete_sequence=["#c8860a","#e8a020","#1a0a00","#a87d52",
                                                   "#3d1a00","#f5e6d0","#6b3a00"])
            fig3.update_layout(font_family="Crimson Pro", paper_bgcolor="rgba(0,0,0,0)",
                               plot_bgcolor="rgba(0,0,0,0)", title_font_size=14,
                               xaxis_title="", showlegend=False,
                               margin=dict(t=40,b=0,l=0,r=0))
            st.plotly_chart(fig3, use_container_width=True)

            rated_df = df_s[df_s["rating"].apply(lambda x: bool(x) and x != "Not rated")]
            if not rated_df.empty:
                rated_df = rated_df.copy()
                rated_df["stars"] = rated_df["rating"].apply(lambda x: int(x[0]) if x and x[0].isdigit() else 0)
                rc = rated_df["stars"].value_counts().sort_index().reset_index()
                rc.columns = ["Stars","Count"]
                rc["label"] = rc["Stars"].apply(lambda x: "★"*x)
                fig4 = px.bar(rc, x="label", y="Count", title="Rating Distribution",
                              color_discrete_sequence=["#c8860a"])
                fig4.update_layout(font_family="Crimson Pro", paper_bgcolor="rgba(0,0,0,0)",
                                   plot_bgcolor="rgba(0,0,0,0)", title_font_size=14,
                                   xaxis_title="", margin=dict(t=40,b=0,l=0,r=0))
                st.plotly_chart(fig4, use_container_width=True)
