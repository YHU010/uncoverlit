import streamlit as st
import urllib.parse

st.set_page_config(
    page_title="UncoverLit",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
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

# ── SESSION STATE ──────────────────────────────────────────────────────────────

if "dismissed" not in st.session_state:
    st.session_state.dismissed = {cat: set() for cat in BOOKS}

# ── HEADER ─────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="site-header">
    <div class="site-header-left">
        <h1>📚 UncoverLit</h1>
        <p>Curated reads that change lives &nbsp;·&nbsp; Handpicked across every genre that matters</p>
    </div>
    <div class="site-header-right">
        🏛 Library links search <a href="https://www.newprovlibrary.org" target="_blank">New Providence Memorial Library</a><br>
        📖 Everand links open a direct search for each title
    </div>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### Options")
    st.markdown("Books you dismiss are hidden and replaced with the next queued pick.")
    st.divider()
    if st.button("↺  Show all books again", use_container_width=True):
        for cat in BOOKS:
            st.session_state.dismissed[cat] = set()
        st.rerun()
    st.divider()
    for cat in BOOKS:
        n = len(st.session_state.dismissed[cat])
        if n:
            label = cat.split("  ", 1)[1]
            if st.button(f"Reset {label} ({n} hidden)", use_container_width=True, key=f"reset_{cat}"):
                st.session_state.dismissed[cat] = set()
                st.rerun()

# ── TABS ───────────────────────────────────────────────────────────────────────

tabs = st.tabs(list(BOOKS.keys()))

for tab, category in zip(tabs, BOOKS.keys()):
    with tab:
        dismissed = st.session_state.dismissed[category]
        visible   = [b for b in BOOKS[category] if b["id"] not in dismissed]
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
            info = f"Showing **{len(showing)}** of **{len(BOOKS[category])}** books"
            if len(dismissed):
                remaining = len(visible) - len(showing)
                info += f"&nbsp;&nbsp;·&nbsp;&nbsp;{len(dismissed)} hidden"
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
                    with st.container(border=True):

                        # ── Cover + text in ONE markdown call (fixes HTML rendering in Streamlit 1.57) ──
                        st.markdown(f"""
                        <div style="width:100%;aspect-ratio:2/3;overflow:hidden;background:#EEF1F5;line-height:0;">
                            <img src="{img}" alt="{book['title']}"
                                 style="width:100%;height:100%;object-fit:cover;display:block;"
                                 onerror="this.src='{fallback}'">
                        </div>
                        <div style="padding:0.9rem 1rem 0.5rem 1rem;">
                            <span style="display:inline-block;background:{bg};color:{fg};font-size:0.65rem;
                                         font-weight:700;padding:2px 8px;border-radius:4px;
                                         text-transform:uppercase;letter-spacing:0.07em;
                                         margin-bottom:0.55rem;">{book['badge']}</span>
                            <p style="font-size:0.95rem;font-weight:700;color:#0D1B2A;
                                      line-height:1.3;margin:0 0 0.2rem 0;">{book['title']}</p>
                            <p style="font-size:0.8rem;color:#7A8FA6;margin:0 0 0.65rem 0;
                                      font-style:italic;">{book['author']}</p>
                            <p style="font-size:0.8rem;color:#4A5568;line-height:1.6;
                                      margin:0 0 0.85rem 0;">{book['summary']}</p>
                        </div>
                        """, unsafe_allow_html=True)

                        # ── Action buttons ──
                        with st.container():
                            st.markdown('<div style="padding: 0 1rem 0.5rem 1rem;">', unsafe_allow_html=True)
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

                            if st.button(
                                "✕  Already read · Not for me",
                                key=f"dismiss_{book['id']}",
                                use_container_width=True,
                            ):
                                st.session_state.dismissed[category].add(book["id"])
                                st.rerun()

                            st.markdown('</div>', unsafe_allow_html=True)
