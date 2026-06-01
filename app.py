import streamlit as st
import urllib.parse
import requests

st.set_page_config(
    page_title="UncoverLit",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── SUPABASE (direct REST API — no package needed) ─────────────────────────────

SUPA_URL = st.secrets["SUPABASE_URL"]
SUPA_KEY = st.secrets["SUPABASE_KEY"]

def _headers():
    return {
        "apikey": SUPA_KEY,
        "Authorization": f"Bearer {SUPA_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }

def db_load_dismissed(user_name: str) -> set:
    """Load all dismissed book_ids for a user."""
    r = requests.get(
        f"{SUPA_URL}/rest/v1/dismissed_books",
        headers=_headers(),
        params={"user_name": f"eq.{user_name}", "select": "book_id"},
    )
    if r.ok:
        return {row["book_id"] for row in r.json()}
    return set()

def db_dismiss(user_name: str, book_id: str):
    """Save a single dismissal."""
    requests.post(
        f"{SUPA_URL}/rest/v1/dismissed_books",
        headers=_headers(),
        json={"user_name": user_name, "book_id": book_id},
    )

def db_reset_all(user_name: str):
    """Remove all dismissals for a user."""
    requests.delete(
        f"{SUPA_URL}/rest/v1/dismissed_books",
        headers=_headers(),
        params={"user_name": f"eq.{user_name}"},
    )

def db_reset_category(user_name: str, book_ids: list):
    """Remove dismissals for a specific category."""
    for bid in book_ids:
        requests.delete(
            f"{SUPA_URL}/rest/v1/dismissed_books",
            headers=_headers(),
            params={"user_name": f"eq.{user_name}", "book_id": f"eq.{bid}"},
        )

def db_get_known_users() -> list:
    """Return all users who have ever dismissed a book."""
    r = requests.get(
        f"{SUPA_URL}/rest/v1/dismissed_books",
        headers=_headers(),
        params={"select": "user_name"},
    )
    if r.ok:
        return sorted({row["user_name"] for row in r.json()})
    return []

def db_load_ratings(user_name: str) -> dict:
    """Load all ratings for a user — returns {book_id: rating}."""
    r = requests.get(
        f"{SUPA_URL}/rest/v1/book_ratings",
        headers=_headers(),
        params={"user_name": f"eq.{user_name}", "select": "book_id,rating"},
    )
    if r.ok:
        return {row["book_id"]: row["rating"] for row in r.json()}
    return {}

def db_save_rating(user_name: str, book_id: str, rating: int):
    """Upsert a rating (insert or update if exists)."""
    upsert_headers = {**_headers(), "Prefer": "resolution=merge-duplicates"}
    requests.post(
        f"{SUPA_URL}/rest/v1/book_ratings?on_conflict=user_name,book_id",
        headers=upsert_headers,
        json={"user_name": user_name, "book_id": book_id, "rating": rating},
    )

# ── STYLES ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Reset & base ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

[data-testid="stAppViewContainer"],
[data-testid="stMain"] { background: #FFFFFF; }

.block-container {
    padding-top: 0 !important;
    padding-bottom: 3rem !important;
    max-width: 1400px !important;
}

/* ── Top header bar ── */
.site-header {
    background: #0D1B2A;
    margin: 0 -6rem 0 -6rem;
    padding: 1.8rem 6rem 1.6rem 6rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 3px solid #C5973A;
}
.site-header-left h1 {
    font-size: 1.9rem;
    font-weight: 800;
    color: #FFFFFF;
    margin: 0;
    letter-spacing: -0.5px;
    font-family: Georgia, 'Times New Roman', serif;
}
.site-header-left p {
    color: #8A9BB0;
    font-size: 0.82rem;
    margin: 0.2rem 0 0 0;
    letter-spacing: 0.03em;
    text-transform: uppercase;
}
.site-header-right {
    font-size: 0.75rem;
    color: #556677;
    text-align: right;
    line-height: 1.6;
}
.site-header-right a {
    color: #C5973A;
    text-decoration: none;
}

/* ── Tab bar ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: #FFFFFF;
    border-bottom: 1px solid #E8ECF0;
    padding: 0;
    margin: 0 -6rem;
    padding: 0 6rem;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 0;
    border: none;
    border-bottom: 3px solid transparent;
    color: #6B7A8D;
    font-weight: 500;
    font-size: 0.88rem;
    padding: 1rem 1.4rem 0.85rem 1.4rem;
    margin-bottom: -1px;
    transition: color 0.15s;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #0D1B2A;
}
.stTabs [aria-selected="true"] {
    background: transparent !important;
    color: #0D1B2A !important;
    border-bottom: 3px solid #C5973A !important;
    font-weight: 700 !important;
}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none; }

/* ── Tab content padding ── */
.stTabs [data-baseweb="tab-panel"] {
    padding: 2rem 0 0 0;
}

/* ── Card grid spacing ── */
[data-testid="column"] {
    padding: 0 0.5rem !important;
}

/* ── Book card (bordered container) ── */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 10px !important;
    border: 1px solid #E8ECF0 !important;
    box-shadow: 0 2px 10px rgba(13, 27, 42, 0.06) !important;
    background: #FFFFFF !important;
    transition: box-shadow 0.2s ease, transform 0.2s ease !important;
    overflow: hidden !important;
    padding: 0 !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: 0 8px 28px rgba(13, 27, 42, 0.13) !important;
    transform: translateY(-3px) !important;
}

/* ── Buttons ── */
.stButton > button {
    border-radius: 6px !important;
    font-size: 0.75rem !important;
    border: 1px solid #DDE2E8 !important;
    background: #F8FAFB !important;
    color: #4A5568 !important;
    width: 100% !important;
    font-weight: 500 !important;
    padding: 0.4rem 0.5rem !important;
    letter-spacing: 0.01em !important;
    transition: all 0.15s !important;
}
.stButton > button:hover {
    background: #EEF2F7 !important;
    border-color: #9AAFC7 !important;
    color: #0D1B2A !important;
}

/* ── Link buttons ── */
[data-testid="stLinkButton"] > a {
    border-radius: 6px !important;
    font-size: 0.75rem !important;
    border: 1px solid #DDE2E8 !important;
    background: #F8FAFB !important;
    color: #4A5568 !important;
    display: block;
    text-align: center;
    text-decoration: none !important;
    font-weight: 500;
    padding: 0.4rem 0.5rem;
    letter-spacing: 0.01em;
    transition: all 0.15s;
}
[data-testid="stLinkButton"] > a:hover {
    background: #EEF2F7 !important;
    border-color: #9AAFC7 !important;
    color: #0D1B2A !important;
}

/* ── Caption ── */
[data-testid="stCaptionContainer"] p {
    color: #9AAFC7;
    font-size: 0.75rem;
    margin: 0 0 1.2rem 0;
    font-weight: 400;
    letter-spacing: 0.02em;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] { background: #F8FAFB; }
[data-testid="stSidebar"] button {
    font-size: 0.82rem !important;
}

/* ── Star rating select slider ── */
[data-testid="stSlider"] { padding: 0 !important; }
[data-testid="stSlider"] > div { padding: 0 !important; }

/* ── Dismiss button — muted, clearly secondary ── */
[data-testid="stVerticalBlockBorderWrapper"] .stButton:last-of-type > button {
    background: #FAFAFA !important;
    color: #9AAAB8 !important;
    border: 1px solid #E8ECF0 !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.04em !important;
    font-weight: 400 !important;
}
[data-testid="stVerticalBlockBorderWrapper"] .stButton:last-of-type > button:hover {
    background: #FFF0F0 !important;
    color: #C05050 !important;
    border-color: #F0CCCC !important;
}
</style>
""", unsafe_allow_html=True)

# ── BOOK DATA ──────────────────────────────────────────────────────────────────

BOOKS = {
    "📖  Memoirs": [
        {"id": "m01", "title": "Educated", "author": "Tara Westover",
         "isbn": "9780399590504", "badge": "Memoir",
         "summary": "Raised off-grid by survivalists in Idaho, Tara Westover educates herself out of isolation to earn a Cambridge PhD — a breathtaking story of self-invention and the cost of truth."},
        {"id": "m02", "title": "When Breath Becomes Air", "author": "Paul Kalanithi",
         "isbn": "9780812988406", "badge": "Memoir · Asian Voices",
         "summary": "A neurosurgeon diagnosed with terminal cancer at 36 reflects on what makes life meaningful. Devastating, luminous, and impossible to put down."},
        {"id": "m03", "title": "Becoming", "author": "Michelle Obama",
         "isbn": "9781524763138", "badge": "Memoir",
         "summary": "The former First Lady traces her journey from Chicago's South Side to the White House — a story of identity, ambition, and purpose that resonates long after the last page."},
        {"id": "m04", "title": "Crying in H Mart", "author": "Michelle Zauner",
         "isbn": "9780525657743", "badge": "Memoir · Asian Voices",
         "summary": "The Japanese Breakfast musician grieves her Korean mother through food, memory, and cultural identity. Raw, beautiful, and universally moving."},
        {"id": "m05", "title": "The Glass Castle", "author": "Jeannette Walls",
         "isbn": "9780743247542", "badge": "Memoir",
         "summary": "A journalist recounts her chaotic childhood raised by eccentric, neglectful parents — a story of resilience, forgiveness, and carving your own path."},
        {"id": "m06", "title": "Born a Crime", "author": "Trevor Noah",
         "isbn": "9780399588174", "badge": "Memoir",
         "summary": "The Daily Show host grew up mixed-race in apartheid South Africa — illegal by birth, wise by necessity. Equal parts hilarious and heartbreaking."},
        {"id": "m07", "title": "The Unwinding of the Miracle", "author": "Julie Yip-Williams",
         "isbn": "9780525508106", "badge": "Memoir · Asian Voices",
         "summary": "A Chinese-American woman who survived the Killing Fields writes unflinchingly about terminal cancer and the fierce art of living fully while you still can."},
        {"id": "m08", "title": "Know My Name", "author": "Chanel Miller",
         "isbn": "9780735223714", "badge": "Memoir",
         "summary": "The woman known as 'Emily Doe' in the Stanford assault case reclaims her identity in a memoir that is both a searing indictment and a remarkable act of healing."},
        {"id": "m09", "title": "Wild", "author": "Cheryl Strayed",
         "isbn": "9780307476074", "badge": "Memoir",
         "summary": "Broke and grief-stricken, a young woman hikes 1,100 miles of the Pacific Crest Trail alone, finding herself by losing everything familiar."},
        {"id": "m10", "title": "Minor Feelings", "author": "Cathy Park Hong",
         "isbn": "9781984820365", "badge": "Essays · Asian Voices",
         "summary": "A Korean-American poet examines the psychology of Asian-American identity — the small slights, the inherited silence, and the radical act of claiming your own story."},
        {"id": "m11", "title": "I Am Malala", "author": "Malala Yousafzai",
         "isbn": "9780316322409", "badge": "Memoir",
         "summary": "The youngest Nobel Peace Prize winner recounts being shot by the Taliban at 15 for speaking up for girls' education — and choosing courage over fear."},
        {"id": "m12", "title": "The Woman Warrior", "author": "Maxine Hong Kingston",
         "isbn": "9780679721888", "badge": "Memoir · Asian Voices",
         "summary": "A foundational work of Asian-American literature weaving Chinese myth and girlhood into a fierce meditation on being female and foreign in America."},
    ],

    "✨  Self-Help": [
        {"id": "s01", "title": "Never Split the Difference", "author": "Chris Voss",
         "isbn": "9780062407801", "badge": "Communication",
         "summary": "An FBI hostage negotiator reveals that the highest-stakes listening skills apply to every conversation — radical empathy as your most powerful tool."},
        {"id": "s02", "title": "Man's Search for Meaning", "author": "Viktor Frankl",
         "isbn": "9780807014271", "badge": "Purpose",
         "summary": "A psychiatrist who survived Auschwitz argues that meaning — not pleasure or power — is the core human drive. One of the most important books of the 20th century."},
        {"id": "s03", "title": "Start With Why", "author": "Simon Sinek",
         "isbn": "9781591846444", "badge": "Purpose & Impact",
         "summary": "Great leaders and movements all begin with a clear answer to WHY — Sinek shows how to discover and communicate yours in a way that inspires others."},
        {"id": "s04", "title": "Dare to Lead", "author": "Brené Brown",
         "isbn": "9780399592522", "badge": "Leadership",
         "summary": "Based on seven years of research, Brown makes the case that brave leadership and vulnerability aren't opposites — they're the same thing."},
        {"id": "s05", "title": "How to Win Friends and Influence People", "author": "Dale Carnegie",
         "isbn": "9780671027032", "badge": "Communication",
         "summary": "Written in 1936 and still unmatched: the definitive guide to understanding people, building trust, and becoming someone others genuinely want to be around."},
        {"id": "s06", "title": "Atomic Habits", "author": "James Clear",
         "isbn": "9780735211292", "badge": "Purpose",
         "summary": "A practical, science-backed framework for building good habits — the compound effect applied to how you actually live, one tiny change at a time."},
        {"id": "s07", "title": "Crucial Conversations", "author": "Kerry Patterson et al.",
         "isbn": "9780071771320", "badge": "Communication",
         "summary": "The book that changes how you handle high-stakes conversations at work and home — when emotions run hot and outcomes matter most."},
        {"id": "s08", "title": "Drive", "author": "Daniel Pink",
         "isbn": "9781594484803", "badge": "Purpose & Impact",
         "summary": "Pink dismantles the old carrot-and-stick model of motivation and reveals that autonomy, mastery, and purpose are what truly move human beings."},
        {"id": "s09", "title": "Essentialism", "author": "Greg McKeown",
         "isbn": "9780804137386", "badge": "Purpose",
         "summary": "The disciplined pursuit of less: a rigorous approach to figuring out what matters most, then eliminating everything that doesn't."},
        {"id": "s10", "title": "Ikigai", "author": "Héctor García & Francesc Miralles",
         "isbn": "9780143130727", "badge": "Purpose",
         "summary": "Drawing on the world's longest-living people, this book explores the Japanese concept of your reason for being — and why it's the key to a long, fulfilling life."},
        {"id": "s11", "title": "Let Your Life Speak", "author": "Parker J. Palmer",
         "isbn": "9780787947354", "badge": "Purpose",
         "summary": "A quiet, profound invitation to stop performing and start listening — to who you truly are and the life that is genuinely yours to live."},
        {"id": "s12", "title": "The 7 Habits of Highly Effective People", "author": "Stephen R. Covey",
         "isbn": "9780743269513", "badge": "Impact",
         "summary": "A character-based philosophy for living with integrity and effectiveness — still the gold standard of personal development literature after 35 years."},
    ],

    "🌍  Geopolitics": [
        {"id": "g01", "title": "Prisoners of Geography", "author": "Tim Marshall",
         "isbn": "9781501121463", "badge": "Geopolitics",
         "summary": "Ten maps that explain how mountains, rivers, and coastlines have shaped every war, alliance, and power struggle in human history — geography as destiny."},
        {"id": "g02", "title": "Why Nations Fail", "author": "Daron Acemoglu & James A. Robinson",
         "isbn": "9780307719225", "badge": "Development",
         "summary": "A landmark work arguing that prosperity and poverty are determined not by geography or culture, but by institutions — and who controls them."},
        {"id": "g03", "title": "Sapiens", "author": "Yuval Noah Harari",
         "isbn": "9780062316097", "badge": "Big History",
         "summary": "A sweeping history of humankind that asks how one unremarkable primate came to dominate the planet — and what that means for our shared future."},
        {"id": "g04", "title": "The Silk Roads", "author": "Peter Frankopan",
         "isbn": "9781101912379", "badge": "History",
         "summary": "A radical retelling of world history from Central Asia and the ancient trade routes that connected civilizations long before Europe rose to dominance."},
        {"id": "g05", "title": "On China", "author": "Henry Kissinger",
         "isbn": "9780143121312", "badge": "Geopolitics · Asia",
         "summary": "The architect of US-China détente reveals the deep historical and strategic logic behind how China thinks — essential reading for understanding today's world order."},
        {"id": "g06", "title": "How Asia Works", "author": "Joe Studwell",
         "isbn": "9780802121547", "badge": "Development · Asia",
         "summary": "Why did Japan, South Korea, and China succeed where so many developing nations failed? Studwell's answer upends conventional economic wisdom."},
        {"id": "g07", "title": "Factfulness", "author": "Hans Rosling",
         "isbn": "9781250107817", "badge": "Big Picture",
         "summary": "Using data to dismantle our most persistent misconceptions, Rosling shows the world is better — and more complex — than the news would have us believe."},
        {"id": "g08", "title": "Destined for War", "author": "Graham Allison",
         "isbn": "9780544935273", "badge": "Geopolitics",
         "summary": "Harvard's Allison examines whether the US and China are heading toward collision — and what 16 historical cases of rising vs. ruling powers teach us."},
        {"id": "g09", "title": "Age of Ambition", "author": "Evan Osnos",
         "isbn": "9780374535278", "badge": "China",
         "summary": "A New Yorker correspondent's intimate portrait of China's transformation — through ordinary people navigating ambition, nationalism, and a remaking world."},
        {"id": "g10", "title": "The Bottom Billion", "author": "Paul Collier",
         "isbn": "9780195373387", "badge": "Development",
         "summary": "Why has development aid failed the world's poorest billion people? Collier identifies four traps keeping nations stuck — and what might actually work."},
        {"id": "g11", "title": "Upheaval", "author": "Jared Diamond",
         "isbn": "9780316409230", "badge": "Big History",
         "summary": "Diamond examines how nations respond to crisis, and what coping strategies separate those that adapt and thrive from those that collapse."},
        {"id": "g12", "title": "The World Is Flat", "author": "Thomas L. Friedman",
         "isbn": "9780312425074", "badge": "Globalization",
         "summary": "How technology leveled the playing field for global competition — a foundational text for understanding the economic shifts still reshaping our world."},
    ],

    "📚  Fiction": [
        {"id": "f01", "title": "All the Light We Cannot See", "author": "Anthony Doerr",
         "isbn": "9781476746586", "badge": "Historical Fiction",
         "summary": "A blind French girl and a German orphan's paths converge during WWII in this Pulitzer winner — a masterpiece of moral beauty and devastating loss."},
        {"id": "f02", "title": "Pachinko", "author": "Min Jin Lee",
         "isbn": "9781455563937", "badge": "Historical Fiction · Asian",
         "summary": "Four generations of a Korean family in Japan struggle with identity, sacrifice, and belonging in an epic spanning nearly a century. Impossible to put down."},
        {"id": "f03", "title": "The Alice Network", "author": "Kate Quinn",
         "isbn": "9780062654199", "badge": "Historical Fiction",
         "summary": "A real WWI spy network and a post-WWII search for a missing cousin interweave in a propulsive, brilliantly researched novel of female courage."},
        {"id": "f04", "title": "Hamnet", "author": "Maggie O'Farrell",
         "isbn": "9780525657606", "badge": "Historical Fiction",
         "summary": "The story of Shakespeare's son who died at 11 — told through his mother's perspective in prose so achingly beautiful it redefines what historical fiction can do."},
        {"id": "f05", "title": "The Tattooist of Auschwitz", "author": "Heather Morris",
         "isbn": "9780062870834", "badge": "Historical Fiction",
         "summary": "Based on a true story: a prisoner assigned to tattoo incoming inmates finds love in the most impossible of places — humanity surviving the unimaginable."},
        {"id": "f06", "title": "People We Meet on Vacation", "author": "Emily Henry",
         "isbn": "9781984806758", "badge": "Romance",
         "summary": "A friends-to-lovers story told in alternating timelines — funny, heartfelt, and achingly romantic. The book that made Emily Henry a phenomenon."},
        {"id": "f07", "title": "Happy Place", "author": "Emily Henry",
         "isbn": "9780593441282", "badge": "Romance",
         "summary": "Two exes secretly broken up for months must share their beloved vacation cottage with friends — Henry at her most emotionally devastating and delightful."},
        {"id": "f08", "title": "The Hating Game", "author": "Sally Thorne",
         "isbn": "9780062439598", "badge": "Romance",
         "summary": "Two rivals fighting for the same executive job discover there's a thin line between loathing and longing — the ultimate enemies-to-lovers romance."},
        {"id": "f09", "title": "One Day in December", "author": "Josie Silver",
         "isbn": "9780451490971", "badge": "Romance",
         "summary": "She spots the man of her dreams through a bus window; months later he's her best friend's boyfriend. A tender, agonizing love story that spans years."},
        {"id": "f10", "title": "Blacktop Wasteland", "author": "S.A. Cosby",
         "isbn": "9781250252449", "badge": "Thriller",
         "summary": "A former getaway driver going straight gets pulled into one last heist — Cosby's breakout novel is ferocious, propulsive, and heartbreakingly human."},
        {"id": "f11", "title": "The Guest List", "author": "Lucy Foley",
         "isbn": "9780062868930", "badge": "Thriller",
         "summary": "A wedding on a remote Irish island, a body by morning, and everyone's hiding something. Claustrophobic, twisty, and compulsively readable."},
        {"id": "f12", "title": "The Silent Patient", "author": "Alex Michaelides",
         "isbn": "9781250301697", "badge": "Thriller",
         "summary": "A famous painter shoots her husband five times and never speaks again. A psychotherapist becomes obsessed with unlocking her silence — and the twist will wreck you."},
    ],

    "💰  Wealth & Investing": [
        {"id": "w01", "title": "The Psychology of Money", "author": "Morgan Housel",
         "isbn": "9780857197689", "badge": "Mindset",
         "summary": "Financial success is less about what you know and more about how you behave — 19 short chapters that will permanently change how you think about money."},
        {"id": "w02", "title": "The Intelligent Investor", "author": "Benjamin Graham",
         "isbn": "9780060555665", "badge": "Investing",
         "summary": "Warren Buffett calls it 'by far the best book on investing ever written.' Graham's value investing principles remain the bedrock of rational long-term wealth building."},
        {"id": "w03", "title": "I Will Teach You to Be Rich", "author": "Ramit Sethi",
         "isbn": "9781523505746", "badge": "Personal Finance",
         "summary": "The no-guilt money guide for 20- and 30-somethings: automate your finances, invest wisely, and spend freely on what you truly love."},
        {"id": "w04", "title": "A Random Walk Down Wall Street", "author": "Burton G. Malkiel",
         "isbn": "9780393330335", "badge": "Investing",
         "summary": "The definitive case for index funds: most professional investors can't beat the market over time, and the data is overwhelming. Join it, don't try to beat it."},
        {"id": "w05", "title": "Rich Dad Poor Dad", "author": "Robert T. Kiyosaki",
         "isbn": "9781612680194", "badge": "Mindset",
         "summary": "Kiyosaki's contrast between two father figures reshaped how millions think about assets, liabilities, and the difference between earning a salary and building wealth."},
        {"id": "w06", "title": "Die With Zero", "author": "Bill Perkins",
         "isbn": "9780358099765", "badge": "Philosophy",
         "summary": "A provocative argument that the goal isn't maximum net worth — it's maximizing life experiences while you're healthy enough to fully enjoy them."},
        {"id": "w07", "title": "The Little Book of Common Sense Investing", "author": "John C. Bogle",
         "isbn": "9781119404507", "badge": "Investing",
         "summary": "The founder of Vanguard makes the elegant, devastating case for index funds: low costs and broad diversification beat nearly every other strategy over time."},
        {"id": "w08", "title": "Principles", "author": "Ray Dalio",
         "isbn": "9781501124020", "badge": "Wealth & Life",
         "summary": "The founder of the world's largest hedge fund shares the radical transparency and decision-making systems that built Bridgewater — and how they apply to life."},
        {"id": "w09", "title": "The Millionaire Next Door", "author": "Thomas J. Stanley & William D. Danko",
         "isbn": "9781589795471", "badge": "Mindset",
         "summary": "America's wealthy aren't who you think: they drive used cars, live below their means, and build wealth quietly. The data-driven case for frugality over flash."},
        {"id": "w10", "title": "Same as Ever", "author": "Morgan Housel",
         "isbn": "9780593332702", "badge": "Mindset",
         "summary": "Housel identifies the timeless human behaviors that never change — a brilliant lens for understanding risk, luck, and decision-making in financial life."},
        {"id": "w11", "title": "Your Money or Your Life", "author": "Vicki Robin",
         "isbn": "9780143115762", "badge": "Personal Finance",
         "summary": "The foundational text of the financial independence movement: transform your relationship with money by asking whether what you spend is worth the life energy it costs."},
        {"id": "w12", "title": "The Total Money Makeover", "author": "Dave Ramsey",
         "isbn": "9781595555274", "badge": "Personal Finance",
         "summary": "Dave Ramsey's no-nonsense baby-step plan for getting out of debt and building lasting wealth — blunt, practical, and life-changing for millions of families."},
    ],
}

SHOW_COUNT = 8

# ── HELPERS ────────────────────────────────────────────────────────────────────

def cover_url(isbn):
    return f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"

def library_url(isbn, title, author):
    # Direct ISBN search in New Providence Memorial Library catalog (Aspen Discovery)
    q = urllib.parse.quote(isbn)
    return f"https://newprovidence.aspendiscovery.org/Search/Results?lookfor={q}&type=ISN"

def everand_url(title):
    q = urllib.parse.quote(title)
    return f"https://www.everand.com/search?query={q}"

# Badge color mapping
BADGE_COLORS = {
    "Memoir": ("#EBF3FF", "#1B5EA8"),
    "Memoir · Asian Voices": ("#FFF0F5", "#A8165A"),
    "Essays · Asian Voices": ("#FFF0F5", "#A8165A"),
    "Communication": ("#F0FBF0", "#1A7A2A"),
    "Purpose": ("#FFF8EC", "#8A5A00"),
    "Purpose & Impact": ("#FFF8EC", "#8A5A00"),
    "Leadership": ("#F5F0FF", "#5B2CA8"),
    "Impact": ("#F5F0FF", "#5B2CA8"),
    "Geopolitics": ("#F0F4FF", "#1B3A9E"),
    "Geopolitics · Asia": ("#F0F4FF", "#1B3A9E"),
    "Development": ("#F0FFF5", "#1A6B40"),
    "Development · Asia": ("#F0FFF5", "#1A6B40"),
    "Big History": ("#FFF5F0", "#8A3010"),
    "History": ("#FFF5F0", "#8A3010"),
    "Big Picture": ("#F5FFFC", "#0A6B50"),
    "China": ("#FFF0F0", "#8A1010"),
    "Globalization": ("#F0F8FF", "#005B8A"),
    "Historical Fiction": ("#FFF8EC", "#6B3A00"),
    "Historical Fiction · Asian": ("#FFF0F5", "#8A1A3A"),
    "Romance": ("#FFF0F5", "#A8165A"),
    "Thriller": ("#F2F2F2", "#2A2A2A"),
    "Mindset": ("#F0F4FF", "#1B3A9E"),
    "Investing": ("#F0FFF5", "#1A6B40"),
    "Personal Finance": ("#FFF8EC", "#6B3A00"),
    "Philosophy": ("#F5F0FF", "#5B2CA8"),
    "Wealth & Life": ("#F0F4FF", "#1B3A9E"),
}
DEFAULT_BADGE = ("#F2F4F8", "#3A4A5C")

# ── NAME PICKER ───────────────────────────────────────────────────────────────

PRESET_USERS = ["YHU010", "SPJEN"]

# ── LOGO SVG ──────────────────────────────────────────────────────────────────
# Open book: two pages with text lines, clear spine, unmistakably a book
LOGO_SVG = """<svg width="40" height="48" viewBox="0 0 40 48" xmlns="http://www.w3.org/2000/svg">
  <!-- page stack visible on right edge -->
  <rect x="9" y="5" width="29" height="39" rx="2" fill="#D8E2EE"/>
  <rect x="8" y="4" width="29" height="39" rx="2" fill="#E4EBF4"/>
  <!-- front cover -->
  <rect x="6" y="3" width="29" height="40" rx="2" fill="#2A5FAF"/>
  <!-- spine / binding — left strip -->
  <rect x="2" y="3" width="7" height="40" rx="2" fill="#1A3A80"/>
  <!-- groove between spine and cover -->
  <line x1="9" y1="3" x2="9" y2="43" stroke="#0D2456" stroke-width="1.2" opacity="0.6"/>
  <!-- gold band on spine -->
  <rect x="2" y="17" width="7" height="11" fill="#C5973A" opacity="0.75"/>
  <!-- decorative title lines on cover -->
  <line x1="13" y1="14" x2="31" y2="14" stroke="white" stroke-width="1.4" opacity="0.55"/>
  <line x1="13" y1="19" x2="31" y2="19" stroke="white" stroke-width="1.4" opacity="0.55"/>
  <line x1="13" y1="24" x2="26" y2="24" stroke="white" stroke-width="1.4" opacity="0.45"/>
  <line x1="13" y1="32" x2="31" y2="32" stroke="white" stroke-width="1" opacity="0.3"/>
  <line x1="13" y1="36" x2="28" y2="36" stroke="white" stroke-width="1" opacity="0.3"/>
</svg>"""

# ── AVATAR SVGs ────────────────────────────────────────────────────────────────
BOY_AVATAR_SVG = """<svg width="80" height="80" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg_b" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0A1628"/><stop offset="100%" stop-color="#162952"/>
    </linearGradient>
    <clipPath id="cp_b"><circle cx="40" cy="40" r="40"/></clipPath>
  </defs>
  <circle cx="40" cy="40" r="40" fill="url(#bg_b)"/>
  <g clip-path="url(#cp_b)">
    <!-- jacket / shoulders -->
    <path d="M10,85 Q14,62 26,60 Q33,70 40,72 Q47,70 54,60 Q66,62 70,85Z" fill="#1A2840"/>
    <path d="M32,60 Q36,67 40,69 Q44,67 48,60" stroke="#2D4060" stroke-width="2" fill="none" stroke-linecap="round"/>
    <!-- collar detail -->
    <rect x="35" y="59" width="10" height="6" rx="1" fill="#0D1E35"/>
    <!-- neck -->
    <rect x="35" y="54" width="10" height="8" fill="#E8A870"/>
    <!-- head -->
    <ellipse cx="40" cy="38" rx="18" ry="20" fill="#EAAA78"/>
    <path d="M22,43 Q22,59 40,61 Q58,59 58,43Z" fill="#EAAA78"/>
    <ellipse cx="22" cy="39" rx="3" ry="4" fill="#DE9C68"/>
    <ellipse cx="58" cy="39" rx="3" ry="4" fill="#DE9C68"/>
    <!-- hair — side-swept cool style, dark with a highlight -->
    <path d="M22,26 Q24,8 40,6 Q56,8 58,26 Q52,14 40,12 Q28,14 22,26Z" fill="#0F0805"/>
    <!-- side-swept fringe sweeping left-to-right across forehead -->
    <path d="M18,22 Q28,12 50,16 Q54,18 56,24 Q44,14 28,16 Q22,18 18,22Z" fill="#1A100A"/>
    <!-- a few loose hair strands for texture -->
    <path d="M22,24 Q24,20 26,22" stroke="#0A0604" stroke-width="2" fill="none" stroke-linecap="round"/>
    <path d="M50,14 Q53,16 54,20" stroke="#0A0604" stroke-width="2" fill="none" stroke-linecap="round"/>
    <!-- eyebrows — sharp, slightly angled -->
    <path d="M25,30 Q30,27.5 35,29" stroke="#150C06" stroke-width="2.2" fill="none" stroke-linecap="round"/>
    <path d="M45,29 Q50,27.5 55,30" stroke="#150C06" stroke-width="2.2" fill="none" stroke-linecap="round"/>
    <!-- eyes — large anime eyes, no glasses -->
    <path d="M24,36 Q30,30 36,36 Q30,41 24,36Z" fill="#0D0806"/>
    <path d="M44,36 Q50,30 56,36 Q50,41 44,36Z" fill="#0D0806"/>
    <!-- iris -->
    <circle cx="30" cy="36" r="3.5" fill="#2C4E8A"/>
    <circle cx="50" cy="36" r="3.5" fill="#2C4E8A"/>
    <!-- pupil -->
    <circle cx="30" cy="36" r="2" fill="#050302"/>
    <circle cx="50" cy="36" r="2" fill="#050302"/>
    <!-- eye highlights -->
    <circle cx="31.5" cy="34.5" r="1.2" fill="white" opacity="0.9"/>
    <circle cx="51.5" cy="34.5" r="1.2" fill="white" opacity="0.9"/>
    <circle cx="29" cy="37.5" r="0.6" fill="white" opacity="0.5"/>
    <circle cx="49" cy="37.5" r="0.6" fill="white" opacity="0.5"/>
    <!-- lower lash line -->
    <path d="M24,38 Q30,40.5 36,38" stroke="#0D0806" stroke-width="0.8" fill="none" opacity="0.6"/>
    <path d="M44,38 Q50,40.5 56,38" stroke="#0D0806" stroke-width="0.8" fill="none" opacity="0.6"/>
    <!-- nose -->
    <path d="M38,42 Q40,44 42,42" stroke="#C88858" stroke-width="1.2" fill="none" stroke-linecap="round"/>
    <!-- mouth — slight confident smirk -->
    <path d="M33,50 Q37,54 43,52 Q47,50 48,49" stroke="#B87040" stroke-width="1.8" fill="none" stroke-linecap="round"/>
  </g>
</svg>"""

GIRL_AVATAR_SVG = """<svg width="80" height="80" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg_g" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#FFE4F0"/><stop offset="100%" stop-color="#FFBBD5"/>
    </linearGradient>
    <clipPath id="cp_g"><circle cx="40" cy="40" r="40"/></clipPath>
  </defs>
  <circle cx="40" cy="40" r="40" fill="url(#bg_g)"/>
  <g clip-path="url(#cp_g)">
    <!-- blouse / shoulders -->
    <path d="M10,85 Q14,64 26,62 Q33,70 40,72 Q47,70 54,62 Q66,64 70,85Z" fill="#FFCCE5"/>
    <!-- small stud earrings -->
    <circle cx="22" cy="41" r="1.8" fill="#E8C050"/>
    <circle cx="58" cy="41" r="1.8" fill="#E8C050"/>
    <!-- head — rounder, less tall -->
    <ellipse cx="40" cy="36" rx="17" ry="17" fill="#F8D0A0"/>
    <!-- jaw — stays compact, no drooping chin -->
    <path d="M23,40 Q23,52 40,54 Q57,52 57,40Z" fill="#F8D0A0"/>
    <ellipse cx="23" cy="38" rx="2.5" ry="3.5" fill="#F0C090"/>
    <ellipse cx="57" cy="38" rx="2.5" ry="3.5" fill="#F0C090"/>
    <!-- hair back -->
    <path d="M19,28 Q14,50 16,84 L28,84 Q23,52 24,28Z" fill="#1E0C06"/>
    <path d="M61,28 Q66,50 64,84 L52,84 Q57,52 56,28Z" fill="#1E0C06"/>
    <!-- hair top -->
    <path d="M23,24 Q25,7 40,5 Q55,7 57,24 Q50,13 40,11 Q30,13 23,24Z" fill="#1E0C06"/>
    <!-- pink bow -->
    <path d="M53,18 Q58,14 63,18 Q58,22 53,18Z" fill="#FF80A8"/>
    <path d="M53,18 Q58,22 63,18 Q58,14 53,18Z" fill="#FF6090" opacity="0.7"/>
    <circle cx="58" cy="18" r="2" fill="#FF4A88"/>
    <!-- eyebrows — soft, normal thickness -->
    <path d="M27,27 Q31,25 35,26.5" stroke="#1E0C06" stroke-width="1.6" fill="none" stroke-linecap="round"/>
    <path d="M45,26.5 Q49,25 53,27" stroke="#1E0C06" stroke-width="1.6" fill="none" stroke-linecap="round"/>
    <!-- eyes — round, normal size, not overdone -->
    <ellipse cx="31" cy="34" rx="6" ry="5.5" fill="white"/>
    <ellipse cx="49" cy="34" rx="6" ry="5.5" fill="white"/>
    <!-- upper lid — simple clean line, NO individual lash strokes -->
    <path d="M25,34 Q31,28.5 37,34" stroke="#1E0C06" stroke-width="1.6" fill="#1E0C06"/>
    <path d="M43,34 Q49,28.5 55,34" stroke="#1E0C06" stroke-width="1.6" fill="#1E0C06"/>
    <!-- iris -->
    <circle cx="31" cy="34.5" r="3.8" fill="#7A4020"/>
    <circle cx="49" cy="34.5" r="3.8" fill="#7A4020"/>
    <!-- pupil -->
    <circle cx="31" cy="34.5" r="2.1" fill="#100804"/>
    <circle cx="49" cy="34.5" r="2.1" fill="#100804"/>
    <!-- highlights -->
    <circle cx="32.5" cy="32.8" r="1.4" fill="white" opacity="0.95"/>
    <circle cx="50.5" cy="32.8" r="1.4" fill="white" opacity="0.95"/>
    <circle cx="29.5" cy="35.8" r="0.7" fill="white" opacity="0.6"/>
    <circle cx="47.5" cy="35.8" r="0.7" fill="white" opacity="0.6"/>
    <!-- lower lid — very subtle -->
    <path d="M25,36 Q31,38.5 37,36" stroke="#1E0C06" stroke-width="0.6" fill="none" opacity="0.3"/>
    <path d="M43,36 Q49,38.5 55,36" stroke="#1E0C06" stroke-width="0.6" fill="none" opacity="0.3"/>
    <!-- rosy cheeks -->
    <ellipse cx="23" cy="40" rx="5" ry="3" fill="#FFAAAA" opacity="0.32"/>
    <ellipse cx="57" cy="40" rx="5" ry="3" fill="#FFAAAA" opacity="0.32"/>
    <!-- nose -->
    <path d="M38.5,43 Q40,44.5 41.5,43" stroke="#D09878" stroke-width="1" fill="none" stroke-linecap="round"/>
    <!-- smile — warm and natural -->
    <path d="M33,49 Q37,53 40,53.5 Q43,53 47,49" stroke="#C86070" stroke-width="1.8" fill="none" stroke-linecap="round"/>
  </g>
</svg>"""

AVATAR_SVG = {"YHU010": BOY_AVATAR_SVG, "SPJEN": GIRL_AVATAR_SVG}

# Single-click login via URL query param (set by clicking the card link)
_qp = st.query_params.get("user", "")
if _qp in PRESET_USERS:
    st.session_state.current_user = _qp
    st.session_state.dismissed = db_load_dismissed(_qp)
    st.session_state.ratings = db_load_ratings(_qp)
    st.query_params.clear()
    st.rerun()

if "current_user" not in st.session_state:
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] { background: #0D1B2A; }
    .block-container { padding-top: 0 !important; max-width: 1400px !important; }
    a.profile-link { text-decoration: none !important; display: block; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:#0D1B2A;margin:0 -6rem;padding:2rem 6rem 1.6rem 6rem;
                border-bottom:3px solid #C5973A;">
        <div style="display:flex;align-items:center;gap:14px;">
            {LOGO_SVG}
            <div>
                <div style="font-size:1.9rem;font-weight:800;margin:0;
                            font-family:Georgia,serif;letter-spacing:-0.5px;line-height:1.1;">
                    <span style="color:#FFFFFF;">Uncover</span><span style="color:#C5973A;">Lit</span>
                </div>
                <div style="color:#8A9BB0;font-size:0.78rem;margin:0.15rem 0 0 0;
                            text-transform:uppercase;letter-spacing:0.06em;">
                    Curated reads that change lives
                </div>
            </div>
        </div>
    </div>
    <div style="text-align:center;padding:4rem 0 2.5rem 0;">
        <p style="font-size:1.9rem;font-weight:700;color:#FFFFFF;margin:0;
                  font-family:Georgia,serif;">Who's reading today?</p>
    </div>
    """, unsafe_allow_html=True)

    # Profile cards — each card is a plain HTML link, one click enters the profile
    _, c1, gap, c2, _ = st.columns([1.2, 1, 0.15, 1, 1.2])

    for col, name in zip([c1, c2], PRESET_USERS):
        avatar = AVATAR_SVG.get(name, "")
        with col:
            st.markdown(f"""
            <a href="?user={name}" class="profile-link">
            <div style="
                background: #132030;
                border: 2px solid #1E3048;
                border-radius: 20px;
                padding: 2rem 1rem 1.8rem 1rem;
                text-align: center;
                transition: border-color 0.2s, box-shadow 0.2s;
                cursor: pointer;
            " onmouseover="this.style.borderColor='#C5973A';this.style.boxShadow='0 8px 32px rgba(197,151,58,0.22)'"
              onmouseout="this.style.borderColor='#1E3048';this.style.boxShadow='none'">
                <div style="width:80px;height:80px;border-radius:50%;overflow:hidden;
                            margin:0 auto 1rem auto;box-shadow:0 4px 20px rgba(0,0,0,0.4);">
                    {avatar}
                </div>
                <p style="color:#FFFFFF;font-size:1.1rem;font-weight:700;
                           margin:0 0 0.2rem 0;letter-spacing:0.08em;">{name}</p>
                <p style="color:#4A6A8A;font-size:0.75rem;margin:0;">Tap to continue</p>
            </div>
            </a>
            """, unsafe_allow_html=True)

    st.stop()

# ── SESSION STATE (user is now logged in) ──────────────────────────────────────

# dismissed is a flat set of book_ids (loaded from Supabase on login)
if "dismissed" not in st.session_state:
    st.session_state.dismissed = db_load_dismissed(st.session_state.current_user)

# ratings: {book_id: 1-5}
if "ratings" not in st.session_state:
    st.session_state.ratings = db_load_ratings(st.session_state.current_user)

# Flat list of all books across categories (used by smart sort)
BOOKS_ALL = [b for cat_books in BOOKS.values() for b in cat_books]
BOOK_BY_ID = {b["id"]: b for b in BOOKS_ALL}

def smart_sort(books: list) -> list:
    """Reorder books so liked-badge books come first, disliked-badge books last."""
    ratings = st.session_state.ratings
    liked_badges, disliked_badges = set(), set()
    for bid, r in ratings.items():
        b = BOOK_BY_ID.get(bid)
        if b:
            if r >= 4:
                liked_badges.add(b["badge"])
            elif r <= 2:
                disliked_badges.add(b["badge"])
    def _score(book):
        if book["badge"] in liked_badges and book["badge"] not in disliked_badges:
            return 0
        if book["badge"] in disliked_badges and book["badge"] not in liked_badges:
            return 2
        return 1
    return sorted(books, key=_score)

def dismiss_book(book_id: str):
    st.session_state.dismissed.add(book_id)
    db_dismiss(st.session_state.current_user, book_id)

def reset_all():
    st.session_state.dismissed = set()
    db_reset_all(st.session_state.current_user)

def reset_category(cat_book_ids: list):
    for bid in cat_book_ids:
        st.session_state.dismissed.discard(bid)
    db_reset_category(st.session_state.current_user, cat_book_ids)

# ── HEADER ─────────────────────────────────────────────────────────────────────

user = st.session_state.current_user
st.markdown(f"""
<div class="site-header">
    <div class="site-header-left">
        <div style="display:flex;align-items:center;gap:14px;">
            {LOGO_SVG}
            <div>
                <div style="font-size:1.9rem;font-weight:800;font-family:Georgia,serif;
                            letter-spacing:-0.5px;line-height:1.1;">
                    <span style="color:#FFFFFF;">Uncover</span><span style="color:#C5973A;">Lit</span>
                </div>
                <div style="color:#8A9BB0;font-size:0.78rem;margin-top:0.15rem;
                            text-transform:uppercase;letter-spacing:0.06em;">
                    Curated reads that change lives
                </div>
            </div>
        </div>
    </div>
    <div class="site-header-right">
        👤 Reading as <strong style="color:#E8C97A">{user}</strong><br>
        <span style="font-size:0.7rem;color:#445566;">
        🏛 Library = New Providence Memorial &nbsp;·&nbsp; 📖 Everand = direct search
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.current_user}")
    st.markdown("Dismissed books are saved — they'll stay hidden next time you visit.")
    st.divider()

    total_hidden = len(st.session_state.dismissed)
    if st.button(f"↺  Show all books again ({total_hidden} hidden)", use_container_width=True):
        reset_all()
        st.rerun()

    st.divider()

    # Per-category reset buttons
    for cat, books in BOOKS.items():
        cat_ids = [b["id"] for b in books]
        n = len(st.session_state.dismissed & set(cat_ids))
        if n:
            label = cat.split("  ", 1)[1]
            if st.button(f"Reset {label} ({n} hidden)", use_container_width=True, key=f"reset_{cat}"):
                reset_category(cat_ids)
                st.rerun()

    st.divider()
    if st.button("🔄  Switch reader", use_container_width=True):
        del st.session_state.current_user
        del st.session_state.dismissed
        st.rerun()

# ── TABS ───────────────────────────────────────────────────────────────────────

tabs = st.tabs(list(BOOKS.keys()))

for tab, category in zip(tabs, BOOKS.keys()):
    with tab:
        visible   = smart_sort([b for b in BOOKS[category] if b["id"] not in st.session_state.dismissed])
        showing   = visible[:SHOW_COUNT]

        if not showing:
            st.markdown("""
            <div style="text-align:center;padding:5rem 0;color:#9AAFC7;">
                <div style="font-size:2.8rem;margin-bottom:1rem">✦</div>
                <p style="font-size:1.1rem;font-weight:600;color:#5A7A9A;margin:0 0 0.4rem 0">
                    You've explored every pick in this category.
                </p>
                <p style="font-size:0.85rem;margin:0">
                    Use <b>Reset</b> in the sidebar to browse them again.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            cat_ids   = {b["id"] for b in BOOKS[category]}
            n_hidden  = len(st.session_state.dismissed & cat_ids)
            info = f"Showing **{len(showing)}** of **{len(BOOKS[category])}** books"
            if n_hidden:
                remaining = len(visible) - len(showing)
                info += f"&nbsp;&nbsp;·&nbsp;&nbsp;{n_hidden} hidden"
                if remaining:
                    info += f"&nbsp;&nbsp;·&nbsp;&nbsp;{remaining} more queued"
            st.caption(info)

            cols = st.columns(4, gap="large")

            for i, book in enumerate(showing):
                bg, fg = BADGE_COLORS.get(book["badge"], DEFAULT_BADGE)
                img    = cover_url(book["isbn"])
                # Fallback placeholder with book emoji
                fallback = "https://placehold.co/300x450/E8ECF0/8A9BB0?text=Book"

                with cols[i % 4]:
                    # Compute "For You" recommendation signal
                    ratings = st.session_state.ratings
                    liked_badges = {BOOK_BY_ID[bid]["badge"] for bid, r in ratings.items()
                                    if r >= 4 and bid in BOOK_BY_ID}
                    disliked_badges = {BOOK_BY_ID[bid]["badge"] for bid, r in ratings.items()
                                       if r <= 2 and bid in BOOK_BY_ID}
                    is_recommended = (book["badge"] in liked_badges and
                                      book["badge"] not in disliked_badges)
                    saved_rating = ratings.get(book["id"], 0)
                    stars_html = ""
                    if saved_rating:
                        filled = "★" * saved_rating
                        empty  = "☆" * (5 - saved_rating)
                        stars_html = f"""<div style="font-size:0.85rem;color:#C5973A;
                            letter-spacing:1px;margin:0 0 0.5rem 0;">{filled}{empty}
                            <span style="font-size:0.68rem;color:#8A9BB0;margin-left:4px;">
                                {saved_rating}/5</span></div>"""

                    for_you_html = ""
                    if is_recommended:
                        for_you_html = """<div style="display:inline-block;background:#FFF8E8;
                            color:#A07010;font-size:0.62rem;font-weight:700;padding:2px 7px;
                            border-radius:4px;text-transform:uppercase;letter-spacing:0.07em;
                            margin-bottom:0.4rem;">♥ For You</div><br>"""

                    with st.container(border=True):

                        # ── Cover + text in ONE markdown call ──
                        st.markdown(f"""
                        <div style="width:100%;aspect-ratio:2/3;overflow:hidden;background:#EEF1F5;line-height:0;">
                            <img src="{img}" alt="{book['title']}"
                                 style="width:100%;height:100%;object-fit:cover;display:block;"
                                 onerror="this.src='{fallback}'">
                        </div>
                        <div style="padding:0.9rem 1rem 0.5rem 1rem;">
                            {for_you_html}<span style="display:inline-block;background:{bg};color:{fg};font-size:0.65rem;
                                         font-weight:700;padding:2px 8px;border-radius:4px;
                                         text-transform:uppercase;letter-spacing:0.07em;
                                         margin-bottom:0.55rem;">{book['badge']}</span>
                            <p style="font-size:0.95rem;font-weight:700;color:#0D1B2A;
                                      line-height:1.3;margin:0 0 0.2rem 0;">{book['title']}</p>
                            <p style="font-size:0.8rem;color:#7A8FA6;margin:0 0 0.65rem 0;
                                      font-style:italic;">{book['author']}</p>
                            <p style="font-size:0.8rem;color:#4A5568;line-height:1.6;
                                      margin:0 0 0.5rem 0;">{book['summary']}</p>
                            {stars_html}
                        </div>
                        """, unsafe_allow_html=True)

                        # ── Action buttons ──
                        c1, c2 = st.columns(2)
                        with c1:
                            st.link_button(
                                "🏛  Library",
                                library_url(book["isbn"], book["title"], book["author"]),
                                use_container_width=True,
                            )
                        with c2:
                            st.link_button(
                                "📖  Everand",
                                everand_url(book["title"]),
                                use_container_width=True,
                            )

                        # Star rating
                        star_opts = ["☆ Not rated", "★ 1", "★★ 2", "★★★ 3", "★★★★ 4", "★★★★★ 5"]
                        cur_idx = saved_rating
                        chosen = st.select_slider(
                            "Rate",
                            options=star_opts,
                            value=star_opts[cur_idx],
                            key=f"rate_{book['id']}",
                            label_visibility="collapsed",
                        )
                        new_idx = star_opts.index(chosen)
                        if new_idx != cur_idx:
                            if new_idx == 0:
                                st.session_state.ratings.pop(book["id"], None)
                            else:
                                st.session_state.ratings[book["id"]] = new_idx
                                db_save_rating(st.session_state.current_user,
                                               book["id"], new_idx)
                            st.rerun()

                        if st.button(
                            "Mark as read / not for me",
                            key=f"dismiss_{book['id']}",
                            use_container_width=True,
                        ):
                            dismiss_book(book["id"])
                            st.rerun()
