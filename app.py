
import streamlit as st
import pandas as pd
import plotly.express as px

# =====================================
# PAGE CONFIGURATION
# =====================================

st.set_page_config(
    page_title="IPL Performance Analytics",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================
# LOAD DATA
# =====================================

@st.cache_data
def load_data():
    data = pd.read_csv("ipl_2008_2026_cleaned.csv")

    data["season"] = pd.to_numeric(
        data["season"], errors="coerce"
    )

    for col in ["team1_runs", "team2_runs"]:
        data[col] = pd.to_numeric(
            data[col], errors="coerce"
        )

    data["total_runs"] = (
        data["team1_runs"].fillna(0) +
        data["team2_runs"].fillna(0)
    )

    return data

df = load_data()

# =====================================
# CUSTOM DESIGN
# =====================================


st.markdown("""
<style>

/* Main background */
.stApp {
    background-color: #0B1220;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #111C2E;
}

/* KPI Cards */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #172554, #1e293b);
    border: 1px solid #334155;
    padding: 20px;
    border-radius: 14px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.20);
    transition: transform 0.2s ease, border-color 0.2s ease;
}

/* KPI hover effect */
[data-testid="stMetric"]:hover {
    transform: translateY(-4px);
    border-color: #38bdf8;
}

/* KPI labels */
[data-testid="stMetricLabel"] {
    color: #AFC2D8 !important;
    font-size: 14px !important;
    font-weight: 600 !important;
}

/* KPI values */
[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
    font-size: 30px !important;
    font-weight: 700 !important;
}

/* Headings */
h1, h2, h3 {
    color: #F8FAFC;
}

</style>
""", unsafe_allow_html=True)

# ---------------- GLOBAL CHART THEME ----------------

def apply_chart_theme(fig, height=420):

    fig.update_layout(
        template="plotly_dark",
        height=height,
        paper_bgcolor="#0B1220",
        plot_bgcolor="#111C2E",
        font=dict(
            family="Arial",
            size=12,
            color="#E2E8F0"
        ),
        title=dict(
            font=dict(size=18, color="#F8FAFC"),
            x=0.02
        ),
        margin=dict(l=35, r=25, t=65, b=40),
        hoverlabel=dict(
            bgcolor="#1E293B",
            font_size=13,
            font_color="#FFFFFF"
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#CBD5E1")
        )
    )

    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor="#334155",
        tickfont=dict(color="#CBD5E1")
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#26364A",
        zeroline=False,
        linecolor="#334155",
        tickfont=dict(color="#CBD5E1")
    )

    return fig


# =====================================
# SIDEBAR NAVIGATION
# =====================================

st.sidebar.markdown("# 🏏 IPL ANALYTICS")
st.sidebar.caption("CRICKET PERFORMANCE PLATFORM")

st.sidebar.divider()

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "🔎 Match Explorer",
        "🏠 Overview",
        "🏆 Team Performance",
        "🏏 Batting Analysis",
        "🎯 Bowling Analysis",
        "🏟️ Venue Analysis",
        "📊 Match Insights"
    ],
    key="nav_page"
)

st.sidebar.divider()

# =====================================
# SIDEBAR FILTERS
# =====================================

st.sidebar.markdown("### 🔎 Dashboard Filters")

min_season = int(df["season"].min())
max_season = int(df["season"].max())

# Season range
selected_range = st.sidebar.slider(
    "Select Season Range",
    min_value=min_season,
    max_value=max_season,
    value=(min_season, max_season),
    key="season_range"
)

st.sidebar.caption(
    f"Showing {selected_range[0]}–{selected_range[1]}"
)

# Team selection
available_teams = sorted(
    set(df["team1"].dropna()) |
    set(df["team2"].dropna())
)

selected_teams = st.sidebar.multiselect(
    "Select Teams",
    available_teams,
    default=[],
    key="team_filter",
    placeholder="All teams"
)

st.sidebar.caption("Leave empty to include all teams.")

# Reset filters
def reset_filters():
    st.session_state["season_range"] = (
        min_season, max_season
    )
    st.session_state["team_filter"] = []

st.sidebar.button(
    "🔄 Reset Filters",
    use_container_width=True,
    on_click=reset_filters
)

st.sidebar.divider()
st.sidebar.caption("IPL Analytics | 2008–2026")

# =====================================
# FILTER DATA
# =====================================

filtered_df = df[
    df["season"].between(
        selected_range[0],
        selected_range[1]
    )
].copy()

if selected_teams:
    filtered_df = filtered_df[
        filtered_df["team1"].isin(selected_teams) |
        filtered_df["team2"].isin(selected_teams)
    ].copy()

# ---------------- DOWNLOAD FILTERED DATA ----------------

st.sidebar.divider()
st.sidebar.subheader("📥 Export Data")

csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.sidebar.download_button(
    label="Download Filtered CSV",
    data=csv_data,
    file_name="IPL_Filtered_Analysis.csv",
    mime="text/csv",
    use_container_width=True
)


# =====================================
# MAIN HEADER
# =====================================

st.title("🏏 The IPL Experience")

st.caption(
    "Explore IPL history through data, statistics and performance insights."
)

st.divider()

# =====================================
# OVERVIEW PAGE
# =====================================

if page == "🏠 Overview":

    st.subheader("Tournament Overview")

    st.caption(
        "A snapshot of IPL performance based on your selected filters."
    )

    total_matches = len(filtered_df)

    total_teams = len(
        set(filtered_df["team1"].dropna()) |
        set(filtered_df["team2"].dropna())
    )

    total_venues = filtered_df["venue"].nunique()

    total_runs = int(filtered_df["total_runs"].sum())

    # KPI CARDS

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("🏏 Total Matches", f"{total_matches:,}")
    c2.metric("🏆 Teams", total_teams)
    c3.metric("🏟️ Venues", total_venues)
    c4.metric("🔥 Total Runs", f"{total_runs:,}")

    st.divider()

    # SEASON PERFORMANCE

    st.subheader("📈 Season Performance")

    season_data = (
        filtered_df.groupby("season")
        .size()
        .reset_index(name="Matches")
    )

    fig = px.line(
        season_data,
        x="season",
        y="Matches",
        markers=True,
        template="plotly_dark",
        title="Matches Played Across IPL Seasons",
        color_discrete_sequence=["#38BDF8"]
    )

    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=9)
    )

    fig.update_layout(
        height=420,
        paper_bgcolor="#111C2E",
        plot_bgcolor="#111C2E",
        xaxis_title="IPL Season",
        yaxis_title="Matches Played",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ADDITIONAL CHARTS

    left, right = st.columns(2)

    with left:

        st.subheader("🔥 Runs by Season")

        runs_data = (
            filtered_df.groupby("season")["total_runs"]
            .sum()
            .reset_index()
        )

        fig2 = px.bar(
            runs_data,
            x="season",
            y="total_runs",
            template="plotly_dark",
            color="total_runs",
            color_continuous_scale="Viridis"
        )

        fig2.update_layout(
            height=350,
            title="Total Runs per Season",
            paper_bgcolor="#111C2E",
            plot_bgcolor="#111C2E",
            coloraxis_showscale=False
        )

        st.plotly_chart(fig2, use_container_width=True)

    with right:

        st.subheader("📊 Match Results")

        result_data = (
            filtered_df["result_type"]
            .value_counts()
            .reset_index()
        )

        result_data.columns = ["Result", "Matches"]

        fig3 = px.pie(
            result_data,
            names="Result",
            values="Matches",
            hole=0.65,
            template="plotly_dark",
            color_discrete_sequence=[
                "#38BDF8", "#F59E0B", "#EF4444"
            ]
        )

        fig3.update_layout(
            height=350,
            title="Match Result Distribution",
            paper_bgcolor="#111C2E"
        )

        st.plotly_chart(fig3, use_container_width=True)

# =====================================

# =====================================
# TEAM PERFORMANCE PAGE
# =====================================

elif page == "🏆 Team Performance":

    st.subheader("🏆 IPL Team Performance")
    st.caption(
        "Compare franchise performance across IPL seasons."
    )

    # Calculate team statistics
    team_wins = (
        filtered_df[
            filtered_df["result_type"] == "complete"
        ]
        .groupby("winner")
        .size()
        .reset_index(name="Matches Won")
    )

    team_matches = pd.concat([
        filtered_df[["team1"]].rename(
            columns={"team1": "Team"}
        ),
        filtered_df[["team2"]].rename(
            columns={"team2": "Team"}
        )
    ])

    matches_played = (
        team_matches.groupby("Team")
        .size()
        .reset_index(name="Matches Played")
    )

    team_stats = matches_played.merge(
        team_wins,
        left_on="Team",
        right_on="winner",
        how="left"
    )

    team_stats["Matches Won"] = (
        team_stats["Matches Won"].fillna(0)
    )

    team_stats["Win Percentage"] = (
        team_stats["Matches Won"] /
        team_stats["Matches Played"] * 100
    ).round(2)

    team_stats = team_stats.drop(
        columns=["winner"],
        errors="ignore"
    )

    # KPI CARDS
    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Total Franchises",
        len(team_stats)
    )

    c2.metric(
        "Highest Team Wins",
        int(team_stats["Matches Won"].max())
    )

    c3.metric(
        "Best Win Percentage",
        f'{team_stats["Win Percentage"].max():.2f}%'
    )

    st.divider()

    # TOP TEAM WINS
    st.subheader("🥇 Top Teams by Total Wins")

    wins_chart = team_stats.sort_values(
        "Matches Won",
        ascending=True
    )

    fig1 = px.bar(
        wins_chart,
        x="Matches Won",
        y="Team",
        orientation="h",
        text="Matches Won",
        template="plotly_dark",
        color="Matches Won",
        color_continuous_scale="Viridis"
    )

    fig1.update_traces(
        textposition="outside"
    )

    fig1.update_layout(
        height=550,
        title="IPL Team Wins Ranking",
        paper_bgcolor="#111C2E",
        plot_bgcolor="#111C2E",
        coloraxis_showscale=False,
        xaxis_title="Total Matches Won",
        yaxis_title=""
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

    st.divider()

    # WIN PERCENTAGE
    st.subheader("📊 Team Win Percentage")

    win_chart = team_stats.sort_values(
        "Win Percentage",
        ascending=True
    )

    fig2 = px.scatter(
        win_chart,
        x="Win Percentage",
        y="Team",
        size="Matches Won",
        color="Win Percentage",
        text="Win Percentage",
        template="plotly_dark",
        color_continuous_scale="Viridis"
    )

    fig2.update_traces(
        texttemplate="%{x:.2f}%",
        textposition="middle right"
    )

    fig2.update_layout(
        height=550,
        title="Franchise Win Percentage Ranking",
        paper_bgcolor="#111C2E",
        plot_bgcolor="#111C2E",
        xaxis_title="Win Percentage (%)",
        yaxis_title="",
        coloraxis_colorbar_title="Win %"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    st.divider()

    # TEAM STATISTICS TABLE
    st.subheader("📋 Detailed Team Statistics")

    display_stats = team_stats.sort_values(
        "Matches Won",
        ascending=False
    )

    st.dataframe(
        display_stats,
        use_container_width=True,
        hide_index=True
    )

# =====================================

# =====================================
# BATTING ANALYSIS PAGE
# =====================================

elif page == "🏏 Batting Analysis":

    st.subheader("🏏 IPL Batting Performance")
    st.caption(
        "Explore team scoring records and batting trends across IPL seasons."
    )

    # ---------------------------------
    # PREPARE BATTING DATA
    # ---------------------------------

    batting_data = pd.concat([
        filtered_df[["season", "team1", "team1_runs"]]
        .rename(columns={
            "team1": "Team",
            "team1_runs": "Runs"
        }),

        filtered_df[["season", "team2", "team2_runs"]]
        .rename(columns={
            "team2": "Team",
            "team2_runs": "Runs"
        })
    ], ignore_index=True)

    batting_data["Runs"] = pd.to_numeric(
        batting_data["Runs"], errors="coerce"
    )

    batting_data = batting_data.dropna(
        subset=["Team", "Runs"]
    )

    # ---------------------------------
    # TEAM BATTING STATISTICS
    # ---------------------------------

    batting_stats = (
        batting_data.groupby("Team")
        .agg(
            Total_Runs=("Runs", "sum"),
            Innings=("Runs", "count"),
            Highest_Score=("Runs", "max")
        )
        .reset_index()
    )

    batting_stats["Average_Runs"] = (
        batting_stats["Total_Runs"] /
        batting_stats["Innings"]
    ).round(2)

    batting_stats = batting_stats.sort_values(
        "Total_Runs", ascending=False
    )

    # ---------------------------------
    # KPI CARDS
    # ---------------------------------

    total_runs = int(batting_data["Runs"].sum())

    total_innings = len(batting_data)

    highest_score = int(batting_data["Runs"].max())

    top_team = batting_stats.iloc[0]["Team"]

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("🔥 Total Runs", f"{total_runs:,}")
    c2.metric("🏏 Total Innings", f"{total_innings:,}")
    c3.metric("🚀 Highest Score", highest_score)
    c4.metric("🏆 Top Scoring Team", top_team)

    st.divider()

    # ---------------------------------
    # CHART 1: TOP 10 TOTAL RUNS
    # ---------------------------------

    st.subheader("🥇 Top 10 Teams by Total Runs")

    top_runs = batting_stats.nlargest(
        10, "Total_Runs"
    ).sort_values("Total_Runs", ascending=True)

    fig1 = px.bar(
        top_runs,
        x="Total_Runs",
        y="Team",
        orientation="h",
        text="Total_Runs",
        color="Total_Runs",
        color_continuous_scale="Viridis",
        template="plotly_dark"
    )

    fig1.update_traces(
        texttemplate="%{x:,.0f}",
        textposition="outside"
    )

    fig1.update_layout(
        height=500,
        title="IPL Teams Ranked by Total Runs",
        xaxis_title="Total Runs Scored",
        yaxis_title="",
        coloraxis_showscale=False,
        paper_bgcolor="#111C2E",
        plot_bgcolor="#111C2E"
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.divider()

    # ---------------------------------
    # CHART 2: HIGHEST INNINGS SCORES
    # ---------------------------------

    st.subheader("🚀 Highest Team Innings Scores")

    highest_scores = (
        batting_data.nlargest(10, "Runs")
        .sort_values("Runs", ascending=True)
        .copy()
    )

    highest_scores["Rank"] = range(
        10, 0, -1
    )

    highest_scores["Label"] = (
        "#" + highest_scores["Rank"].astype(str)
        + " " + highest_scores["Team"]
    )

    fig2 = px.scatter(
        highest_scores,
        x="Runs",
        y="Label",
        size="Runs",
        color="Runs",
        text="Runs",
        color_continuous_scale="Viridis",
        template="plotly_dark"
    )

    fig2.update_traces(
        textposition="middle right",
        texttemplate="%{x:.0f}"
    )

    fig2.update_layout(
        height=500,
        title="Top 10 Highest Team Innings",
        xaxis_title="Runs Scored",
        yaxis_title="",
        coloraxis_showscale=False,
        showlegend=False,
        paper_bgcolor="#111C2E",
        plot_bgcolor="#111C2E"
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # ---------------------------------
    # CHART 3: SEASON-WISE RUNS
    # ---------------------------------

    st.subheader("📈 IPL Season-wise Scoring Trends")

    season_runs = (
        filtered_df.groupby("season")["total_runs"]
        .sum()
        .reset_index()
    )

    fig3 = px.line(
        season_runs,
        x="season",
        y="total_runs",
        markers=True,
        text="total_runs",
        template="plotly_dark",
        color_discrete_sequence=["#38BDF8"]
    )

    fig3.update_traces(
        line=dict(width=3),
        marker=dict(size=8),
        texttemplate="%{y:,.0f}",
        textposition="top center"
    )

    fig3.update_layout(
        height=450,
        title="Total Runs Scored Across IPL Seasons",
        xaxis_title="IPL Season",
        yaxis_title="Total Runs",
        paper_bgcolor="#111C2E",
        plot_bgcolor="#111C2E",
        hovermode="x unified"
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    # ---------------------------------
    # DETAILED BATTING TABLE
    # ---------------------------------

    st.subheader("📋 Team Batting Statistics")

    display_batting = batting_stats.rename(
        columns={
            "Total_Runs": "Total Runs",
            "Average_Runs": "Average Runs",
            "Highest_Score": "Highest Score"
        }
    )

    st.dataframe(
        display_batting,
        use_container_width=True,
        hide_index=True
    )


# =====================================
# BOWLING ANALYSIS PAGE
# =====================================

elif page == "🎯 Bowling Analysis":

    st.subheader("🎯 IPL Bowling Performance")
    st.caption(
        "Analyse franchise bowling performance and wickets taken across IPL seasons."
    )

    # ---------------------------------
    # PREPARE BOWLING DATA
    # ---------------------------------

    bowling_data = pd.concat([

        filtered_df[
            ["season", "team1", "team2_wickets"]
        ].rename(columns={
            "team1": "Team",
            "team2_wickets": "Wickets"
        }),

        filtered_df[
            ["season", "team2", "team1_wickets"]
        ].rename(columns={
            "team2": "Team",
            "team1_wickets": "Wickets"
        })

    ], ignore_index=True)

    bowling_data["Wickets"] = pd.to_numeric(
        bowling_data["Wickets"],
        errors="coerce"
    )

    # Remove invalid innings records
    bowling_data = bowling_data.dropna(
        subset=["Team", "Wickets"]
    )

    bowling_data = bowling_data[
        bowling_data["Wickets"].between(0, 10)
    ].copy()

    # ---------------------------------
    # TEAM BOWLING STATISTICS
    # ---------------------------------

    bowling_stats = (
        bowling_data.groupby("Team")
        .agg(
            Total_Wickets=("Wickets", "sum"),
            Innings=("Wickets", "count"),
            Highest_Wickets=("Wickets", "max")
        )
        .reset_index()
    )

    bowling_stats["Average_Wickets"] = (
        bowling_stats["Total_Wickets"] /
        bowling_stats["Innings"]
    ).round(2)

    bowling_stats = bowling_stats.sort_values(
        "Total_Wickets",
        ascending=False
    )

    # ---------------------------------
    # KPI CARDS
    # ---------------------------------

    total_wickets = int(
        bowling_data["Wickets"].sum()
    )

    total_innings = len(bowling_data)

    highest_wickets = int(
        bowling_data["Wickets"].max()
    )

    top_bowling_team = bowling_stats.iloc[0]["Team"]

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "🎯 Total Wickets",
        f"{total_wickets:,}"
    )

    c2.metric(
        "🏏 Bowling Innings",
        f"{total_innings:,}"
    )

    c3.metric(
        "🔥 Highest Wickets",
        highest_wickets
    )

    c4.metric(
        "🏆 Leading Team",
        top_bowling_team
    )

    st.divider()

    # ---------------------------------
    # CHART 1: TOTAL WICKETS
    # ---------------------------------

    st.subheader("🥇 Top 10 Teams by Wickets")

    top_wickets = bowling_stats.nlargest(
        10, "Total_Wickets"
    ).sort_values(
        "Total_Wickets",
        ascending=True
    )

    fig1 = px.bar(
        top_wickets,
        x="Total_Wickets",
        y="Team",
        orientation="h",
        text="Total_Wickets",
        color="Total_Wickets",
        color_continuous_scale="Viridis",
        template="plotly_dark"
    )

    fig1.update_traces(
        textposition="outside"
    )

    fig1.update_layout(
        height=500,
        title="IPL Teams by Total Opposition Wickets Lost",
        xaxis_title="Total Wickets",
        yaxis_title="",
        coloraxis_showscale=False,
        paper_bgcolor="#111C2E",
        plot_bgcolor="#111C2E"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

    st.divider()

    # ---------------------------------
    # CHART 2: AVERAGE WICKETS
    # ---------------------------------

    st.subheader("📊 Average Wickets per Innings")

    average_chart = bowling_stats.sort_values(
        "Average_Wickets",
        ascending=True
    )

    fig2 = px.scatter(
        average_chart,
        x="Average_Wickets",
        y="Team",
        size="Total_Wickets",
        color="Average_Wickets",
        text="Average_Wickets",
        color_continuous_scale="Viridis",
        template="plotly_dark"
    )

    fig2.update_traces(
        texttemplate="%{x:.2f}",
        textposition="middle right"
    )

    fig2.update_layout(
        height=550,
        title="Franchise Average Wickets per Innings",
        xaxis_title="Average Wickets",
        yaxis_title="",
        coloraxis_colorbar_title="Average",
        paper_bgcolor="#111C2E",
        plot_bgcolor="#111C2E"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    st.divider()

    # ---------------------------------
    # CHART 3: SEASON-WISE WICKETS
    # ---------------------------------

    st.subheader("📈 Season-wise Wickets Analysis")

    season_wickets = (
        bowling_data.groupby("season")["Wickets"]
        .sum()
        .reset_index()
    )

    fig3 = px.line(
        season_wickets,
        x="season",
        y="Wickets",
        markers=True,
        text="Wickets",
        template="plotly_dark",
        color_discrete_sequence=["#38BDF8"]
    )

    fig3.update_traces(
        line=dict(width=3),
        marker=dict(size=8),
        textposition="top center"
    )

    fig3.update_layout(
        height=450,
        title="Total Opposition Wickets Lost Across Seasons",
        xaxis_title="IPL Season",
        yaxis_title="Total Wickets",
        paper_bgcolor="#111C2E",
        plot_bgcolor="#111C2E",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

    st.divider()

    # ---------------------------------
    # DETAILED BOWLING TABLE
    # ---------------------------------

    st.subheader("📋 Team Bowling Statistics")

    display_bowling = bowling_stats.rename(
        columns={
            "Total_Wickets": "Total Wickets",
            "Average_Wickets": "Average Wickets",
            "Highest_Wickets": "Highest Wickets"
        }
    )

    st.dataframe(
        display_bowling,
        use_container_width=True,
        hide_index=True
    )


# =====================================
# VENUE ANALYSIS PAGE
# =====================================

elif page == "🏟️ Venue Analysis":

    st.subheader("🏟️ IPL Venue Performance")
    st.caption(
        "Explore stadium statistics, match hosting records and scoring patterns."
    )

    # ---------------------------------
    # PREPARE VENUE DATA
    # ---------------------------------

    venue_data = filtered_df.copy()

    venue_data["team1_runs"] = pd.to_numeric(
        venue_data["team1_runs"], errors="coerce"
    )

    venue_data["team2_runs"] = pd.to_numeric(
        venue_data["team2_runs"], errors="coerce"
    )

    venue_data["Match_Runs"] = (
        venue_data["team1_runs"].fillna(0) +
        venue_data["team2_runs"].fillna(0)
    )

    # ---------------------------------
    # VENUE STATISTICS
    # ---------------------------------

    venue_stats = (
        venue_data.groupby("venue")
        .agg(
            Matches_Played=("match_number", "count"),
            Total_Runs=("Match_Runs", "sum"),
            Average_Match_Runs=("Match_Runs", "mean"),
            Highest_Match_Runs=("Match_Runs", "max")
        )
        .reset_index()
    )

    venue_stats["Average_Match_Runs"] = (
        venue_stats["Average_Match_Runs"].round(2)
    )

    venue_stats = venue_stats.sort_values(
        "Matches_Played", ascending=False
    )

    # ---------------------------------
    # KPI CARDS
    # ---------------------------------

    total_venues = venue_stats["venue"].nunique()

    total_matches = venue_stats["Matches_Played"].sum()

    highest_match_score = int(
        venue_stats["Highest_Match_Runs"].max()
    )

    popular_venue = venue_stats.iloc[0]["venue"]

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("🏟️ Venues", total_venues)

    c2.metric("🏏 Matches Hosted", f"{total_matches:,}")

    c3.metric("🔥 Highest Match Runs", highest_match_score)

    c4.metric("📍 Most Hosted Venue", popular_venue)

    st.divider()

    # ---------------------------------
    # CHART 1: MATCHES HOSTED
    # ---------------------------------

    st.subheader("🏆 Top 10 Venues by Matches Hosted")

    top_venues = venue_stats.nlargest(
        10, "Matches_Played"
    ).sort_values(
        "Matches_Played", ascending=True
    )

    fig1 = px.bar(
        top_venues,
        x="Matches_Played",
        y="venue",
        orientation="h",
        text="Matches_Played",
        color="Matches_Played",
        color_continuous_scale="Viridis",
        template="plotly_dark"
    )

    fig1.update_traces(
        textposition="outside"
    )

    fig1.update_layout(
        height=500,
        title="Most Frequently Used IPL Stadiums",
        xaxis_title="Matches Hosted",
        yaxis_title="",
        coloraxis_showscale=False,
        paper_bgcolor="#111C2E",
        plot_bgcolor="#111C2E"
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.divider()

    # ---------------------------------
    # CHART 2: AVERAGE VS HIGHEST RUNS
    # ---------------------------------

    st.subheader("📊 Venue Scoring Comparison")

    scoring_data = venue_stats.nlargest(
        10, "Matches_Played"
    ).sort_values(
        "Average_Match_Runs", ascending=True
    )

    fig2 = px.scatter(
        scoring_data,
        x="Average_Match_Runs",
        y="venue",
        size="Matches_Played",
        color="Highest_Match_Runs",
        text="Average_Match_Runs",
        color_continuous_scale="Viridis",
        template="plotly_dark",
        hover_data=[
            "Matches_Played",
            "Highest_Match_Runs"
        ]
    )

    fig2.update_traces(
        texttemplate="%{x:.1f}",
        textposition="middle right"
    )

    fig2.update_layout(
        height=550,
        title="Average Match Runs at Top 10 Venues",
        xaxis_title="Average Match Runs",
        yaxis_title="",
        paper_bgcolor="#111C2E",
        plot_bgcolor="#111C2E",
        coloraxis_colorbar_title="Highest Runs"
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # ---------------------------------
    # CHART 3: TOTAL RUNS BY VENUE
    # ---------------------------------

    st.subheader("🔥 Total Runs by Venue")

    runs_venues = venue_stats.nlargest(
        10, "Total_Runs"
    ).sort_values(
        "Total_Runs", ascending=True
    )

    fig3 = px.bar(
        runs_venues,
        x="Total_Runs",
        y="venue",
        orientation="h",
        text="Total_Runs",
        color="Total_Runs",
        color_continuous_scale="Plasma",
        template="plotly_dark"
    )

    fig3.update_traces(
        texttemplate="%{x:,.0f}",
        textposition="outside"
    )

    fig3.update_layout(
        height=500,
        title="Top 10 Venues by Total Runs",
        xaxis_title="Total Runs Scored",
        yaxis_title="",
        coloraxis_showscale=False,
        paper_bgcolor="#111C2E",
        plot_bgcolor="#111C2E"
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    # ---------------------------------
    # VENUE STATISTICS TABLE
    # ---------------------------------

    st.subheader("📋 Detailed Venue Statistics")

    display_venue = venue_stats.rename(
        columns={
            "venue": "Venue",
            "Matches_Played": "Matches Played",
            "Total_Runs": "Total Runs",
            "Average_Match_Runs": "Average Match Runs",
            "Highest_Match_Runs": "Highest Match Runs"
        }
    )

    st.dataframe(
        display_venue,
        use_container_width=True,
        hide_index=True
    )

# =====================================
# MATCH INSIGHTS PAGE
# =====================================

elif page == "📊 Match Insights":

    st.subheader("📊 IPL Match Insights")
    st.caption(
        "Explore toss decisions, match outcomes and winning patterns."
    )

    # ---------------------------------
    # PREPARE MATCH DATA
    # ---------------------------------

    match_data = filtered_df.copy()

    # ---------------------------------
    # KPI CALCULATIONS
    # ---------------------------------

    total_matches = len(match_data)

    complete_matches = match_data[
        match_data["result_type"] == "complete"
    ]

    toss_wins = match_data[
        match_data["toss_winner"] == match_data["winner"]
    ]

    toss_win_rate = (
        len(toss_wins) / total_matches * 100
        if total_matches > 0 else 0
    )

    run_wins = match_data[
        match_data["win_by_runs"] > 0
    ]

    wicket_wins = match_data[
        match_data["win_by_wickets"] > 0
    ]

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("🏏 Total Matches", f"{total_matches:,}")
    c2.metric("🏆 Completed Matches", f"{len(complete_matches):,}")
    c3.metric("🪙 Toss Winners Also Won", f"{len(toss_wins):,}")
    c4.metric("📊 Toss-to-Win Rate", f"{toss_win_rate:.2f}%")

    st.divider()

    # ---------------------------------
    # CHART 1: TOSS DECISIONS
    # ---------------------------------

    st.subheader("🪙 Toss Decision Analysis")

    toss_data = (
        match_data["toss_decision"]
        .value_counts()
        .reset_index()
    )

    toss_data.columns = ["Decision", "Matches"]

    fig1 = px.pie(
        toss_data,
        names="Decision",
        values="Matches",
        hole=0.6,
        template="plotly_dark",
        color_discrete_sequence=[
            "#38BDF8", "#F59E0B"
        ]
    )

    fig1.update_layout(
        height=400,
        title="Bat First vs Field First",
        paper_bgcolor="#111C2E"
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.divider()

    # ---------------------------------
    # CHART 2: TOSS WINNER VS MATCH WINNER
    # ---------------------------------

    st.subheader("🏆 Does Winning the Toss Matter?")

    toss_comparison = pd.DataFrame({
        "Category": [
            "Toss Winner Also Won Match",
            "Toss Winner Lost Match"
        ],
        "Matches": [
            len(toss_wins),
            total_matches - len(toss_wins)
        ]
    })

    fig2 = px.bar(
        toss_comparison,
        x="Category",
        y="Matches",
        text="Matches",
        color="Category",
        template="plotly_dark",
        color_discrete_sequence=[
            "#38BDF8", "#F59E0B"
        ]
    )

    fig2.update_traces(
        textposition="outside"
    )

    fig2.update_layout(
        height=400,
        title="Toss Winner Match Outcome",
        showlegend=False,
        paper_bgcolor="#111C2E",
        plot_bgcolor="#111C2E"
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # ---------------------------------
    # CHART 3: WINNING METHOD
    # ---------------------------------

    st.subheader("🎯 Winning Method Analysis")

    margin_data = pd.DataFrame({
        "Winning Method": [
            "Won by Runs",
            "Won by Wickets"
        ],
        "Matches": [
            len(run_wins),
            len(wicket_wins)
        ]
    })

    fig3 = px.bar(
        margin_data,
        x="Winning Method",
        y="Matches",
        text="Matches",
        color="Winning Method",
        template="plotly_dark",
        color_discrete_sequence=[
            "#38BDF8", "#F59E0B"
        ]
    )

    fig3.update_traces(
        textposition="outside"
    )

    fig3.update_layout(
        height=400,
        title="Matches Won by Runs vs Wickets",
        showlegend=False,
        paper_bgcolor="#111C2E",
        plot_bgcolor="#111C2E"
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    # ---------------------------------
    # CHART 4: SEASON-WISE TOSS ADVANTAGE
    # ---------------------------------

    st.subheader("📈 Season-wise Toss Advantage")

    season_toss = match_data.copy()

    season_toss["Toss_Match_Win"] = (
        season_toss["toss_winner"] ==
        season_toss["winner"]
    )

    season_toss = (
        season_toss.groupby("season")
        .agg(
            Total_Matches=("season", "count"),
            Toss_Wins=("Toss_Match_Win", "sum")
        )
        .reset_index()
    )

    season_toss["Toss_Win_Percentage"] = (
        season_toss["Toss_Wins"] /
        season_toss["Total_Matches"] * 100
    ).round(2)

    fig4 = px.line(
        season_toss,
        x="season",
        y="Toss_Win_Percentage",
        markers=True,
        text="Toss_Win_Percentage",
        template="plotly_dark",
        color_discrete_sequence=["#38BDF8"]
    )

    fig4.update_traces(
        line=dict(width=3),
        marker=dict(size=8),
        texttemplate="%{y:.1f}%",
        textposition="top center"
    )

    fig4.update_layout(
        height=450,
        title="Percentage of Matches Won by Toss Winners",
        xaxis_title="IPL Season",
        yaxis_title="Win Percentage (%)",
        paper_bgcolor="#111C2E",
        plot_bgcolor="#111C2E"
    )

    st.plotly_chart(fig4, use_container_width=True)

    st.divider()

    # ---------------------------------
    # MATCH STATISTICS TABLE
    # ---------------------------------

    st.subheader("📋 Match Outcome Summary")

    result_summary = (
        match_data["result_type"]
        .value_counts()
        .reset_index()
    )

    result_summary.columns = [
        "Result Type", "Number of Matches"
    ]

    st.dataframe(
        result_summary,
        use_container_width=True,
        hide_index=True
    )

elif page == "🔎 Match Explorer":

    st.title("🔎 IPL Match Centre")
    st.caption("Search, filter and analyse individual IPL matches.")

    match_explorer = filtered_df.copy()

    # ---------------- FILTERS ----------------

    st.subheader("Match Filters")

    col1, col2, col3 = st.columns(3)

    with col1:
        search_team = st.selectbox(
            "Team",
            ["All Teams"] + sorted(
                set(match_explorer["team1"].dropna()) |
                set(match_explorer["team2"].dropna())
            )
        )

    with col2:
        search_venue = st.selectbox(
            "Venue",
            ["All Venues"] + sorted(
                match_explorer["venue"].dropna().unique()
            )
        )

    with col3:
        result_options = ["All Results"] + sorted(
            match_explorer["result_type"].dropna().unique()
        )

        search_result = st.selectbox(
            "Match Result",
            result_options
        )

    col4, col5 = st.columns(2)

    with col4:
        search_winner = st.selectbox(
            "Winner",
            ["All Teams"] + sorted(
                match_explorer["winner"].dropna().unique()
            )
        )

    with col5:
        search_toss = st.selectbox(
            "Toss Decision",
            ["All Decisions"] + sorted(
                match_explorer["toss_decision"].dropna().unique()
            )
        )

    search_text = st.text_input(
        "Search team name",
        placeholder="Enter a team name..."
    )

    # ---------------- APPLY FILTERS ----------------

    if search_team != "All Teams":
        match_explorer = match_explorer[
            (match_explorer["team1"] == search_team) |
            (match_explorer["team2"] == search_team)
        ]

    if search_venue != "All Venues":
        match_explorer = match_explorer[
            match_explorer["venue"] == search_venue
        ]

    if search_result != "All Results":
        match_explorer = match_explorer[
            match_explorer["result_type"] == search_result
        ]

    if search_winner != "All Teams":
        match_explorer = match_explorer[
            match_explorer["winner"] == search_winner
        ]

    if search_toss != "All Decisions":
        match_explorer = match_explorer[
            match_explorer["toss_decision"] == search_toss
        ]

    if search_text:
        match_explorer = match_explorer[
            match_explorer["team1"].str.contains(
                search_text, case=False, na=False
            ) |
            match_explorer["team2"].str.contains(
                search_text, case=False, na=False
            )
        ]

    # ---------------- MATCH STATISTICS ----------------

    st.divider()
    st.subheader("Match Statistics")

    total_matches = len(match_explorer)

    completed = match_explorer[
        match_explorer["result_type"] == "complete"
    ]

    average_runs = (
        match_explorer["total_runs"].mean()
        if total_matches else 0
    )

    highest_runs = (
        match_explorer["total_runs"].max()
        if total_matches else 0
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Matches Found", total_matches)
    c2.metric("Completed Matches", len(completed))
    c3.metric("Average Match Runs", round(average_runs, 1))
    c4.metric("Highest Match Runs", int(highest_runs))

    # ---------------- MATCH SELECTION ----------------

    st.divider()
    st.subheader("Individual Match Analysis")

    if not match_explorer.empty:

        match_explorer = match_explorer.copy()

        match_explorer["match_label"] = (
            match_explorer["season"].astype(str)
            + " | Match "
            + match_explorer["match_number"].astype(str)
            + " | "
            + match_explorer["team1"].astype(str)
            + " vs "
            + match_explorer["team2"].astype(str)
        )

        match_explorer = match_explorer.reset_index(drop=True)

        selected_match = st.selectbox(
            "Choose a match",
            match_explorer["match_label"].tolist()
        )

        match = match_explorer[
            match_explorer["match_label"] == selected_match
        ].iloc[0]

        # ---------------- SCORECARD ----------------

        st.subheader("🏏 Match Scorecard")

        team1 = match["team1"]
        team2 = match["team2"]

        runs1 = match["team1_runs"]
        runs2 = match["team2_runs"]

        wickets1 = match["team1_wickets"]
        wickets2 = match["team2_wickets"]

        score1 = (
            f"{int(runs1)}/{int(wickets1)}"
            if pd.notna(runs1) and pd.notna(wickets1)
            else "Not Available"
        )

        score2 = (
            f"{int(runs2)}/{int(wickets2)}"
            if pd.notna(runs2) and pd.notna(wickets2)
            else "Not Available"
        )

        score_col1, score_col2 = st.columns(2)

        with score_col1:
            st.markdown(f"### {team1}")
            st.title(score1)

        with score_col2:
            st.markdown(f"### {team2}")
            st.title(score2)

        st.markdown(f"**Winner:** {match['winner'] if pd.notna(match['winner']) else 'No winner recorded'}")

        # ---------------- MATCH DETAILS ----------------

        st.divider()
        st.subheader("Match Details")

        d1, d2, d3 = st.columns(3)

        d1.metric("Season", int(match["season"]))
        d2.metric("Venue", str(match["venue"]))
        d3.metric("Result Type", str(match["result_type"]).title())

        st.write("**Toss Winner:**", match["toss_winner"])
        st.write("**Toss Decision:**", str(match["toss_decision"]).title())

        if pd.notna(match["win_by_runs"]) and match["win_by_runs"] > 0:
            st.success(
                f"{match['winner']} won by {int(match['win_by_runs'])} runs."
            )

        elif pd.notna(match["win_by_wickets"]) and match["win_by_wickets"] > 0:
            st.success(
                f"{match['winner']} won by {int(match['win_by_wickets'])} wickets."
            )

        else:
            st.info("No standard winning margin is recorded for this match.")

        # ---------------- SCORE COMPARISON ----------------

        st.divider()
        st.subheader("Team Score Comparison")

        score_chart_data = pd.DataFrame({
            "Team": [team1, team2],
            "Runs": [
                runs1 if pd.notna(runs1) else 0,
                runs2 if pd.notna(runs2) else 0
            ]
        })

        fig = px.bar(
            score_chart_data,
            x="Team",
            y="Runs",
            color="Team",
            text="Runs",
            title="Runs Scored by Both Teams"
        )

        fig.update_layout(
            template="plotly_dark",
            showlegend=False,
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("No matches found. Try changing the filters.")

    # ---------------- MATCH HISTORY ----------------

    st.divider()
    st.subheader("📋 Match History")

    display_columns = [
        "season", "match_number", "team1", "team2",
        "team1_runs", "team1_wickets",
        "team2_runs", "team2_wickets",
        "winner", "venue"
    ]

    st.dataframe(
        match_explorer[display_columns].sort_values(
            by=["season", "match_number"],
            ascending=[False, True]
        ),
        use_container_width=True,
        hide_index=True
    )

# =====================================
# FOOTER
# =====================================

st.divider()

st.caption(
    "IPL Performance Analytics | Historical Dataset 2008–2026"
)
