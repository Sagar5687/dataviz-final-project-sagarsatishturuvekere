import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Steam Games Analytics Dashboard",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

from pathlib import Path

def load_css():
    css_path = Path(__file__).parent / "style.css"

    with open(css_path) as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )
load_css()

hide_streamlit_style = """
<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
</style>
"""

st.markdown(
    hide_streamlit_style,
    unsafe_allow_html=True
)
# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():
    return pd.read_csv("data/steam_cleaned.csv")

df = load_data()

# ============================================================
# COLOUR PALETTE
# ============================================================

COLORS = [
    "#0072B2",
    "#E69F00",
    "#009E73",
    "#CC79A7",
    "#D55E00",
    "#56B4E9"
]

# ============================================================
# HEADER
# ============================================================

st.markdown("""
# 🎮 Steam Games Analytics Dashboard

Explore **82,000+ Steam games** through interactive visualisations.
Use the filters on the left to investigate pricing trends,
genre popularity and player engagement.
""")

st.markdown("---")

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown("# 🎮 Filters")

st.sidebar.markdown("### 🎯 Genre")

genres = sorted(df["primary_genre"].dropna().unique())

selected_genres = st.sidebar.multiselect(
    "Genre",
    genres
)

st.sidebar.markdown("---")

st.sidebar.markdown("### 📅 Release Year")

years = sorted(df["release_year"].unique())

selected_years = st.sidebar.multiselect(
    "Year",
    years
)

st.sidebar.markdown("---")

st.sidebar.markdown("### 💰 Price")

price_range = st.sidebar.slider(
    "Price ($)",
    float(df.price.min()),
    float(df.price.max()),
    (
        float(df.price.min()),
        float(df.price.max())
    )
)

st.sidebar.markdown("---")

st.sidebar.markdown("### ⭐ Reviews")

minimum_score = st.sidebar.slider(
    "Minimum Review Score",
    0,
    100,
    0
)

minimum_reviews = st.sidebar.slider(
    "Minimum Review Count",
    0,
    int(df.review_count.max()),
    0
)

st.sidebar.markdown("---")

free_games = st.sidebar.checkbox(
    "Show Free Games Only"
)


# ============================================================
# FILTER DATA
# ============================================================

filtered_df = df.copy()

if selected_genres:
    filtered_df = filtered_df[
        filtered_df.primary_genre.isin(selected_genres)
    ]

if selected_years:
    filtered_df = filtered_df[
        filtered_df.release_year.isin(selected_years)
    ]

filtered_df = filtered_df[
    filtered_df.price.between(
        price_range[0],
        price_range[1]
    )
]

filtered_df = filtered_df[
    filtered_df.review_score >= minimum_score
]

filtered_df = filtered_df[
    filtered_df.review_count >= minimum_reviews
]

if free_games:
    filtered_df = filtered_df[
        filtered_df.price == 0
    ]

if filtered_df.empty:
    st.warning("⚠️ No games match the selected filters. Please adjust your filters.")
    st.stop()
# ============================================================
# DASHBOARD SUMMARY
# ============================================================

st.subheader("📊 Dashboard Summary")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "🎮 Games",
        f"{len(filtered_df):,}"
    )

with c2:
    st.metric(
        "📂 Genres",
        filtered_df.primary_genre.nunique()
    )

with c3:
    st.metric(
        "💰 Avg Price",
        f"${filtered_df.price.mean():.2f}"
    )

with c4:
    st.metric(
        "⭐ Avg Review",
        f"{filtered_df.review_score.mean():.1f}"
    )

st.markdown("---")

with st.expander("ℹ️ About this Dashboard"):

    st.markdown("""
This interactive dashboard explores **82,928 Steam games**.

It allows users to analyse:

- 🎮 Genre popularity
- 💰 Pricing strategies
- ⭐ Player satisfaction
- 👥 Community engagement
- 🏢 Developer performance

Use the filters in the sidebar to interactively explore the data.
""")
    
# ============================================================
# ACTIVE FILTERS
# ============================================================

with st.expander("📌 Current Filters", expanded=False):

    st.write(f"**Games Displayed:** {len(filtered_df):,}")

    if selected_genres:
        st.write("**Genres:**", ", ".join(selected_genres))
    else:
        st.write("**Genres:** All")

    if selected_years:
        st.write(
            f"**Years:** {min(selected_years)} - {max(selected_years)}"
        )
    else:
        st.write("**Years:** All")

    st.write(
        f"**Price Range:** ${price_range[0]:.2f} - ${price_range[1]:.2f}"
    )

    st.write(
        f"**Minimum Review Score:** {minimum_score}"
    )

# ============================================================
# TABS
# ============================================================

home, market, genre, players = st.tabs([
    "🏠 Home",
    "📈 Market Overview",
    "🎮 Genre Analysis",
    "👥 Player Behaviour"
])

# ============================================================
# HOME TAB
# ============================================================

with home:

    st.header("🏠 Steam Marketplace Overview")

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # Genre Distribution
    # --------------------------------------------------------

    with col1:

        genre_counts = (
            filtered_df["primary_genre"]
            .value_counts()
            .sort_values()
            .reset_index()
        )

        genre_counts.columns = ["Genre", "Games"]

        fig = px.bar(
            genre_counts,
            x="Games",
            y="Genre",
            orientation="h",
            color="Games",
            color_continuous_scale="Blues",
            title="Games Available by Genre"
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=500,
            coloraxis_showscale=False,
            yaxis_title="",
            xaxis_title="Number of Games"
        )

        st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "displayModeBar": False,
        "responsive": True
    }
)

        st.success(
            "Action and Adventure dominate Steam's catalogue, while Simulation and Racing contain significantly fewer titles."
        )

    # --------------------------------------------------------
    # Top Developers
    # --------------------------------------------------------

    with col2:

        developers = (
            filtered_df["developer"]
            .value_counts()
            .head(10)
            .sort_values()
            .reset_index()
        )

        developers.columns = ["Developer", "Games"]

        fig = px.bar(
            developers,
            x="Games",
            y="Developer",
            orientation="h",
            color="Games",
            color_continuous_scale="Viridis",
            title="Top 10 Developers by Number of Games"
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=500,
            coloraxis_showscale=False,
            yaxis_title="",
            xaxis_title="Games Published"
        )

        st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "displayModeBar": False,
        "responsive": True
    }
)

        st.success(
            "A small number of developers contribute a large proportion of games within the selected filters."
        )

# ============================================================
# MARKET OVERVIEW
# ============================================================

with market:

    st.header("💰 Market Overview")

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # Average Price by Genre
    # --------------------------------------------------------

    with col1:

        genre_price = (
            filtered_df.groupby("primary_genre")["price"]
            .mean()
            .sort_values()
            .reset_index()
        )

        fig = px.bar(
            genre_price,
            x="price",
            y="primary_genre",
            orientation="h",
            color="price",
            color_continuous_scale="Turbo",
            title="Average Price by Genre"
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=500,
            coloraxis_showscale=False,
            xaxis_title="Average Price ($)",
            yaxis_title=""
        )

        st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "displayModeBar": False,
        "responsive": True
    }
)

        st.info(
            "Different genres follow different pricing strategies. Some consistently command higher average prices than others."
        )

    # --------------------------------------------------------
    # Average Review Score by Genre
    # --------------------------------------------------------

    with col2:

        genre_reviews = (
            filtered_df.groupby("primary_genre")["review_score"]
            .mean()
            .sort_values()
            .reset_index()
        )

        fig = px.bar(
            genre_reviews,
            x="review_score",
            y="primary_genre",
            orientation="h",
            color="review_score",
            color_continuous_scale="RdYlGn",
            title="Average Review Score by Genre"
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=500,
            coloraxis_showscale=False,
            xaxis_title="Average Review Score",
            yaxis_title=""
        )

        st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "displayModeBar": False,
        "responsive": True
    }
)

        st.info(
            "Comparing average review scores helps identify which genres consistently receive stronger player feedback."
        )

    st.markdown("---")

    st.subheader("📌 Market Summary")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "💲 Average Price",
        f"${filtered_df['price'].mean():.2f}"
    )

    c2.metric(
        "⭐ Highest Review",
        f"{filtered_df['review_score'].max():.0f}"
    )

    c3.metric(
        "🎮 Developers",
        filtered_df["developer"].nunique()
    )
# ============================================================
# GENRE ANALYSIS
# ============================================================

with genre:

    st.header("🎮 Genre Analysis")

    st.markdown("""
    This section compares Steam genres based on **player satisfaction**, **community engagement**
    and **market presence**.
    """)

    # =======================================================
    # Bubble Chart
    # =======================================================

    genre_stats = (
        filtered_df
        .groupby("primary_genre")
        .agg(
            Avg_Review=("review_score","mean"),
            Avg_Reviews=("review_count","mean"),
            Games=("name","count")
        )
        .reset_index()
    )

    fig = px.scatter(
        genre_stats,
        x="Avg_Reviews",
        y="Avg_Review",
        size="Games",
        color="primary_genre",
        hover_name="primary_genre",
        size_max=70,
        title="Genre Satisfaction vs Community Engagement"
    )

    fig.update_layout(
        template="plotly_dark",
        height=650,
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Average Review Count",
        yaxis_title="Average Review Score"
    )

    st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "displayModeBar": False,
        "responsive": True
    }
)

    st.success("""
Genres positioned in the **upper-right** combine both
high player satisfaction and strong engagement,
making them the most successful categories on Steam.
""")

    st.markdown("---")

    # =======================================================
    # Developer Performance
    # =======================================================

    st.subheader("🏆 Highest Rated Developers (Minimum 10 Games)")

    developer_stats = (
        filtered_df
        .groupby("developer")
        .agg(
            Games=("name","count"),
            Avg_Review=("review_score","mean")
        )
        .reset_index()
    )

    developer_stats = developer_stats[
        developer_stats["Games"] >= 10
    ]

    developer_stats = developer_stats.nlargest(
        15,
        "Avg_Review"
    )

    fig = px.bar(
        developer_stats.sort_values("Avg_Review"),
        x="Avg_Review",
        y="developer",
        orientation="h",
        color="Avg_Review",
        color_continuous_scale="Viridis",
        title="Top Rated Developers"
    )

    fig.update_layout(
        template="plotly_dark",
        height=600,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        xaxis_title="Average Review Score",
        yaxis_title=""
    )

    st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "displayModeBar": False,
        "responsive": True
    }
)

    st.info("""
Developers included have released **at least 10 games**, ensuring the rankings
reflect consistent performance rather than isolated successes.
""")
# ============================================================
# PLAYER BEHAVIOUR
# ============================================================

with players:

    st.header("👥 Player Behaviour")

    st.markdown("""
Analyse how player engagement relates to review scores
and identify the most influential games on Steam.
""")

    col1, col2 = st.columns([1.1,1])

    # =======================================================
    # Top Reviewed Games
    # =======================================================

    with col1:

        top_games = (
            filtered_df
            .nlargest(15,"review_count")
        )

        fig = px.bar(
            top_games.sort_values("review_count"),
            x="review_count",
            y="name",
            orientation="h",
            color="review_score",
            color_continuous_scale="Turbo",
            hover_data=["developer","price"],
            title="Top 15 Most Reviewed Games"
        )

        fig.update_layout(
            template="plotly_dark",
            height=650,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False,
            xaxis_title="Review Count",
            yaxis_title=""
        )

        st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "displayModeBar": False,
        "responsive": True
    }
)

    # =======================================================
    # Density Heatmap
    # =======================================================

    with col2:

        fig = px.density_heatmap(
            filtered_df,
            x="review_count",
            y="review_score",
            nbinsx=35,
            nbinsy=25,
            color_continuous_scale="Viridis",
            title="Review Count vs Review Score"
        )

        fig.update_layout(
            template="plotly_dark",
            height=650,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_colorbar_title=""
        )

        st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "displayModeBar": False,
        "responsive": True
    }
)

    st.success("""
Most Steam games cluster around **moderate review counts** with
**high review scores**, while only a small number achieve extremely
large communities.
""")

    st.markdown("---")

    c1,c2,c3 = st.columns(3)

    c1.metric(
        "Total Reviews",
        f"{filtered_df.review_count.sum():,}"
    )

    c2.metric(
        "Highest Review Score",
        int(filtered_df.review_score.max())
    )

    c3.metric(
        "Average Reviews",
        f"{filtered_df.review_count.mean():,.0f}"
    )

    st.markdown("---")

    csv = filtered_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "📥 Download Filtered Dataset",
        csv,
        "filtered_steam_games.csv",
        "text/csv"
    )
