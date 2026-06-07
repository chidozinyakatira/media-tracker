import streamlit as st
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
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Crimson+Pro:ital,wght@0,300;0,400;0,600;1,300;1,400&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Crimson Pro', serif;
    font-size: 17px;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #1a0a00;
    border-right: 1px solid #3d1f00;
}
section[data-testid="stSidebar"] * { color: #f5e6d0 !important; }
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stTextInput label,
section[data-testid="stSidebar"] .stMultiSelect label {
    color: #a87d52 !important;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-family: 'DM Mono', monospace !important;
}

/* ── Background ── */
.main { background: #fdf8f2; }
[data-testid="stAppViewContainer"] { background: #fdf8f2; }

/* ── Header ── */
.page-header {
    background: linear-gradient(135deg, #1a0a00 0%, #3d1a00 50%, #1a0a00 100%);
    padding: 2.5rem 3rem 2rem;
    border-radius: 20px;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.page-header::before {
    content: '📚';
    position: absolute;
    right: 2rem; top: 50%;
    transform: translateY(-50%);
    font-size: 6rem;
    opacity: 0.08;
}
.page-header::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #c8860a, #e8a020, #c8860a);
}
.page-header h1 {
    font-family: 'Playfair Display', serif;
    font-size: 2.8rem;
    color: #f5e6d0;
    margin: 0 0 0.3rem;
    letter-spacing: -0.01em;
}
.page-header .subtitle {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: #a87d52;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

/* ── Metric cards ── */
.metric-card {
    background: white;
    border-radius: 14px;
    padding: 1.3rem 1.6rem;
    border: 1px solid #e8d8c4;
    box-shadow: 0 2px 8px rgba(60,20,0,0.06);
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; width: 4px; height: 100%;
    background: linear-gradient(180deg, #c8860a, #e8a020);
}
.metric-card .label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #a87d52;
    margin-bottom: 0.5rem;
}
.metric-card .value {
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem;
    color: #1a0a00;
    line-height: 1;
}

/* ── Section titles ── */
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.5rem;
    color: #1a0a00;
    margin: 2rem 0 1rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
.section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, #c8860a44, transparent);
    margin-left: 0.5rem;
}

/* ── Status pill ── */
.pill {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-family: 'DM Mono', monospace;
    font-weight: 500;
    letter-spacing: 0.04em;
}
.pill-read      { background: #dcfce7; color: #166534; }
.pill-wishlist  { background: #fef9c3; color: #854d0e; }
.pill-reading   { background: #dbeafe; color: #1e40af; }
.pill-abandoned { background: #fee2e2; color: #991b1b; }
.pill-watched   { background: #dcfce7; color: #166534; }
.pill-watching  { background: #dbeafe; color: #1e40af; }
.pill-paused    { background: #fce7f3; color: #9d174d; }
.pill-dropped   { background: #fee2e2; color: #991b1b; }

/* ── Stars ── */
.stars { color: #c8860a; font-size: 1rem; letter-spacing: 2px; }

/* ── Book/series card ── */
.item-card {
    background: white;
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    border: 1px solid #e8d8c4;
    box-shadow: 0 2px 6px rgba(60,20,0,0.05);
    margin-bottom: 0.8rem;
    transition: box-shadow 0.2s;
}
.item-card:hover { box-shadow: 0 4px 16px rgba(60,20,0,0.1); }
.item-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.15rem;
    color: #1a0a00;
    margin-bottom: 0.2rem;
    font-style: italic;
}
.item-meta {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: #a87d52;
    letter-spacing: 0.04em;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 2px solid #e8d8c4;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Playfair Display', serif;
    font-size: 1rem;
    color: #a87d52;
    padding: 0.6rem 1.5rem;
    border-bottom: 3px solid transparent;
}
.stTabs [aria-selected="true"] {
    color: #1a0a00 !important;
    border-bottom: 3px solid #c8860a !important;
    background: transparent !important;
}

/* ── Buttons ── */
.stButton > button {
    background: #1a0a00 !important;
    color: #f5e6d0 !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Crimson Pro', serif !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    padding: 0.45rem 1.4rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: #3d1a00 !important;
    box-shadow: 0 4px 12px rgba(60,20,0,0.2) !important;
    transform: translateY(-1px) !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    font-family: 'Playfair Display', serif !important;
    font-size: 1rem !important;
    color: #1a0a00 !important;
    background: white !important;
    border-radius: 10px !important;
    border: 1px solid #e8d8c4 !important;
}
.streamlit-expanderContent {
    background: white !important;
    border: 1px solid #e8d8c4 !important;
    border-top: none !important;
    border-radius: 0 0 10px 10px !important;
}

/* ── Selectbox / input ── */
.stTextInput input, .stTextArea textarea, .stSelectbox > div > div {
    border-color: #e8d8c4 !important;
    border-radius: 8px !important;
    font-family: 'Crimson Pro', serif !important;
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
  <h1>My Media Tracker</h1>
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
                    pill_cls = STATUS_PILL.get(b.get("status",""), "pill-wishlist")
                    star_str = stars(b.get("rating",""))
                    reread   = "🔁 Would re-read" if str(b.get("reread","")).lower() in ["true","yes","1"] else ""

                    with st.expander(f"*{b.get('title','Untitled')}* — {b.get('author','Unknown')}"):
                        col_a, col_b, col_c = st.columns([3, 2, 1])
                        with col_a:
                            st.markdown(f"**Genre:** {b.get('genre','—')}  \n**Status:** {b.get('status','—')}  \n**Date finished:** {b.get('date_finished','—')}")
                            if reread:
                                st.markdown(reread)
                        with col_b:
                            st.markdown(f"**Rating:** {star_str}")
                            if b.get("review"):
                                st.markdown(f"**Review:** {b['review']}")
                            if b.get("notes"):
                                st.markdown(f"**Notes:** {b['notes']}")
                        with col_c:
                            if orig_idx is not None:
                                if st.button("✏️", key=f"eb_{orig_idx}", help="Edit"):
                                    st.session_state.edit_book = orig_idx
                                    st.rerun()
                                if st.button("🗑️", key=f"db_{orig_idx}", help="Delete"):
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

        c1, c2 = st.columns(2)
        with c1:
            title  = st.text_input("Title *",  value=ex.get("title",""),  key="b_title")
            author = st.text_input("Author *", value=ex.get("author",""), key="b_author")
            genre  = st.selectbox("Genre", BOOK_GENRES,
                                  index=BOOK_GENRES.index(ex["genre"]) if ex.get("genre") in BOOK_GENRES else 0,
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
            cover  = st.text_input("Cover image URL (optional)", value=ex.get("cover_url",""), key="b_cover")

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
                    star_str = stars(s.get("rating",""))
                    rewatch  = "🔁 Would rewatch" if str(s.get("rewatch","")).lower() in ["true","yes","1"] else ""

                    with st.expander(f"*{s.get('title','Untitled')}* — {s.get('creator','Unknown')}"):
                        col_a, col_b, col_c = st.columns([3, 2, 1])
                        with col_a:
                            st.markdown(f"**Genre:** {s.get('genre','—')}  \n**Platform:** {s.get('platform','—')}  \n**Seasons:** {s.get('seasons','—')}  \n**Date finished:** {s.get('date_finished','—')}")
                            if rewatch:
                                st.markdown(rewatch)
                        with col_b:
                            st.markdown(f"**Rating:** {star_str}")
                            if s.get("review"):
                                st.markdown(f"**Review:** {s['review']}")
                            if s.get("notes"):
                                st.markdown(f"**Notes:** {s['notes']}")
                        with col_c:
                            if orig_idx is not None:
                                if st.button("✏️", key=f"es_{orig_idx}", help="Edit"):
                                    st.session_state.edit_series = orig_idx
                                    st.rerun()
                                if st.button("🗑️", key=f"ds_{orig_idx}", help="Delete"):
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

        c1, c2 = st.columns(2)
        with c1:
            title   = st.text_input("Title *",   value=ex.get("title",""),   key="s_title")
            creator = st.text_input("Creator / Showrunner", value=ex.get("creator",""), key="s_creator")
            genre   = st.selectbox("Genre", SERIES_GENRES,
                                   index=SERIES_GENRES.index(ex["genre"]) if ex.get("genre") in SERIES_GENRES else 0,
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

        poster = st.text_input("Poster image URL (optional)", value=ex.get("poster_url",""), key="s_poster")
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
