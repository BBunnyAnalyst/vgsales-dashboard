import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Video Game Sales Dashboard", layout="wide")

REGIONS = {"NA_Sales": "North America", "EU_Sales": "Europe",
           "JP_Sales": "Japan", "Other_Sales": "Other"}
COLORS = {"North America": "#2a78d6", "Europe": "#eb6834",
          "Japan": "#1baf7a", "Other": "#eda100"}
BLUE = "#2a78d6"


@st.cache_data
def load_data():
    return pd.read_csv("vgsales_clean.csv")


df = load_data()

# ---------- Title ----------
st.title("Global video game sales, 1980-2016")
st.write("Which genre, platform and region sold the most? "
         "Where should a new game focus? Use the filters on the left.")

# ---------- Filters (interactive element) ----------
st.sidebar.header("Filters")
genres = st.sidebar.multiselect("Genre", sorted(df["Genre"].unique()))
platforms = st.sidebar.multiselect("Platform", sorted(df["Platform"].unique()))
year_min, year_max = int(df["Year"].min()), int(df["Year"].max())
years = st.sidebar.slider("Year range", year_min, year_max, (year_min, year_max))

f = df[df["Year"].between(years[0], years[1])]
if genres:
    f = f[f["Genre"].isin(genres)]
if platforms:
    f = f[f["Platform"].isin(platforms)]

if f.empty:
    st.warning("No data for these filters.")
    st.stop()

# ---------- KPIs ----------
total = f["Global_Sales"].sum()
by_genre = f.groupby("Genre")["Global_Sales"].sum().sort_values(ascending=False)
na_share = f["NA_Sales"].sum() / total * 100

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total sales (million copies)", f"{total:,.0f}")
k2.metric("Number of releases", f"{len(f):,}")
k3.metric("Top genre", by_genre.index[0], f"{by_genre.iloc[0]:,.0f} M copies",
          delta_color="off")
k4.metric("North America share", f"{na_share:.0f}%")

# ---------- Charts ----------
by_year = f.groupby("Year", as_index=False)["Global_Sales"].sum()
fig = px.line(by_year, x="Year", y="Global_Sales",
              labels={"Global_Sales": "Million copies"},
              title="Sales by year (2016 is incomplete)")
fig.update_traces(line_color=BLUE)
st.plotly_chart(fig, width="stretch")

c1, c2 = st.columns(2)

g = by_genre.reset_index().sort_values("Global_Sales")
fig = px.bar(g, x="Global_Sales", y="Genre", orientation="h",
             labels={"Global_Sales": "Million copies"}, title="Sales by genre")
fig.update_traces(marker_color=BLUE)
c1.plotly_chart(fig, width="stretch")

top_plat = f.groupby("Platform")["Global_Sales"].sum().nlargest(10).index
p = (f[f["Platform"].isin(top_plat)]
     .groupby("Platform")[list(REGIONS)].sum().rename(columns=REGIONS)
     .loc[top_plat].reset_index()
     .melt(id_vars="Platform", var_name="Region", value_name="Sales"))
fig = px.bar(p, x="Platform", y="Sales", color="Region",
             color_discrete_map=COLORS,
             labels={"Sales": "Million copies"},
             title="Top 10 platforms by region")
c2.plotly_chart(fig, width="stretch")

c3, c4 = st.columns(2)

pub = f.groupby("Publisher")["Global_Sales"].sum().nlargest(10).reset_index()
pub = pub.sort_values("Global_Sales")
fig = px.bar(pub, x="Global_Sales", y="Publisher", orientation="h",
             labels={"Global_Sales": "Million copies"}, title="Top 10 publishers")
fig.update_traces(marker_color=BLUE)
c3.plotly_chart(fig, width="stretch")

reg = f[list(REGIONS)].sum().rename(index=REGIONS).reset_index()
reg.columns = ["Region", "Sales"]
fig = px.pie(reg, names="Region", values="Sales", hole=0.5,
             color="Region", color_discrete_map=COLORS,
             title="Share by region")
c4.plotly_chart(fig, width="stretch")

# ---------- Insights ----------
peak = by_year.loc[by_year["Global_Sales"].idxmax()]
reg_sorted = reg.sort_values("Sales", ascending=False)
st.subheader("Key insights")
st.markdown(
    f"- Peak year in this selection: **{int(peak['Year'])}** "
    f"({peak['Global_Sales']:,.0f} M copies).\n"
    f"- **{by_genre.index[0]}** leads with "
    f"{by_genre.iloc[0] / total * 100:.0f}% of sales.\n"
    f"- Biggest market: **{reg_sorted.iloc[0]['Region']}** "
    f"({reg_sorted.iloc[0]['Sales'] / total * 100:.0f}%). "
    f"Japan is only {f['JP_Sales'].sum() / total * 100:.0f}%.\n"
    "- A new game should target the leading genre and biggest market, "
    "but competition is strongest there too."
)

# ---------- Methodology ----------
with st.expander("Methodology note"):
    st.write(
        "Source: Kaggle 'Video Game Sales' (scraped from vgchartz.com). "
        "Cleaning: removed 311 rows with a missing Year or Publisher, and "
        "near-empty rows after 2016. 16,287 rows remain. Unit: million copies. "
        "Limitation: single source, and 2016 is incomplete."
    )
