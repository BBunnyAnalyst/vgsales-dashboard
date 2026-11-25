import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Видео тоглоомын борлуулалтын Dashboard", layout="wide")

REGIONS = {"NA_Sales": "Хойд Америк", "EU_Sales": "Европ",
           "JP_Sales": "Япон", "Other_Sales": "Бусад"}
COLORS = {"Хойд Америк": "#2a78d6", "Европ": "#eb6834",
          "Япон": "#1baf7a", "Бусад": "#eda100"}
BLUE = "#2a78d6"
UNIT = "Сая хувь"
INK2 = "#52514e"

# ---------- Загвар (CSS): HTML dashboard-тай ижил харагдац ----------
st.markdown("""
<style>
.stApp{background:#f4f4f2;color:#0b0b0b}
header[data-testid="stHeader"]{background:transparent}
.block-container{max-width:1200px;padding-top:1.5rem;padding-bottom:3rem}
h1{font-size:24px!important;margin:0 0 4px!important;padding:0!important}
.sub{color:#52514e;margin:0 0 16px;max-width:820px}
[class*="st-key-card"],[class*="st-key-filters"]{
  background:#fcfcfb;border:1px solid #e3e2de;border-radius:10px;padding:14px}
[class*="st-key-insight"]{
  background:#eef4fc;border:1px solid #cfe0f6;border-radius:10px;padding:14px}
.kpi{background:#fcfcfb;border:1px solid #e3e2de;border-radius:10px;padding:14px}
.kpi .l{font-size:12px;color:#52514e}
.kpi .v{font-size:30px;font-weight:650;letter-spacing:-.5px;line-height:1.2}
.kpi .u{font-size:12px;color:#52514e;min-height:18px}
.ch{font-size:15px;font-weight:600;margin:0 0 2px}
.cd{font-size:12px;color:#52514e;margin:0 0 4px}
.note{font-size:12px;color:#52514e;margin-top:14px}
.note b{color:#0b0b0b}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    return pd.read_csv("vgsales_clean.csv")


df = load_data()
YEAR_MIN, YEAR_MAX = int(df["Year"].min()), int(df["Year"].max())
ALL = "Бүгд"


def reset_filters():
    st.session_state.fg = ALL
    st.session_state.fp = ALL
    st.session_state.f1 = YEAR_MIN
    st.session_state.f2 = YEAR_MAX


for k, v in {"fg": ALL, "fp": ALL, "f1": YEAR_MIN, "f2": YEAR_MAX}.items():
    st.session_state.setdefault(k, v)


def style(fig, legend=False):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=INK2), margin=dict(l=10, r=10, t=10, b=10), height=300,
        showlegend=legend, legend=dict(orientation="h", y=-0.2, title=None))
    fig.update_xaxes(gridcolor="#ecebe7")
    fig.update_yaxes(gridcolor="#ecebe7")
    return fig


def card_head(title, desc):
    st.markdown(f'<div class="ch">{title}</div><div class="cd">{desc}</div>',
                unsafe_allow_html=True)


# ---------- Гарчиг ----------
st.title("Видео тоглоомын дэлхийн борлуулалт, 1980–2016")
st.markdown('<p class="sub">Аль төрөл, аль платформ, аль бүс нутагт видео тоглоом '
            'хамгийн их борлогдсон бэ? Шинэ тоглоом гаргах бол хаана төвлөрөх нь '
            'ашигтай вэ? Шүүлтүүрүүдээр өөрөө судлаарай.</p>', unsafe_allow_html=True)

# ---------- Шүүлтүүр (интерактив элемент) ----------
with st.container(key="filters"):
    a, b, c, d, e = st.columns([2, 2, 1.2, 1.2, 1.6], vertical_alignment="bottom")
    genre = a.selectbox("Төрөл (Genre)", [ALL] + sorted(df["Genre"].unique()), key="fg")
    plat = b.selectbox("Платформ", [ALL] + sorted(df["Platform"].unique()), key="fp")
    y1 = c.selectbox("Эхлэх он", list(range(YEAR_MIN, YEAR_MAX + 1)), key="f1")
    y2 = d.selectbox("Дуусах он", list(range(YEAR_MIN, YEAR_MAX + 1)), key="f2")
    e.button("Шүүлтүүр арилгах", on_click=reset_filters)

f = df[df["Year"].between(y1, y2)]
if genre != ALL:
    f = f[f["Genre"] == genre]
if plat != ALL:
    f = f[f["Platform"] == plat]

st.write("")
if f.empty:
    st.warning("Энэ шүүлтүүрт өгөгдөл олдсонгүй.")
    st.stop()

# ---------- KPI ----------
total = f["Global_Sales"].sum()
by_genre = f.groupby("Genre")["Global_Sales"].sum().sort_values(ascending=False)
na_share = f["NA_Sales"].sum() / total * 100


def kpi(col, label, value, unit):
    col.markdown(f'<div class="kpi"><div class="l">{label}</div>'
                 f'<div class="v">{value}</div><div class="u">{unit}</div></div>',
                 unsafe_allow_html=True)


k1, k2, k3, k4 = st.columns(4)
kpi(k1, "Нийт борлуулалт", f"{total:,.0f}", "сая хувь")
kpi(k2, "Тоглоомын тоо", f"{len(f):,}", "гаргалт (нэр + платформ)")
kpi(k3, "Тэргүүлэх төрөл", by_genre.index[0], f"{by_genre.iloc[0]:,.0f} сая хувь")
kpi(k4, "Хойд Америкийн хувь", f"{na_share:.0f}%", "нийт борлуулалтын")
st.write("")

# ---------- Графикууд ----------
by_year = f.groupby("Year", as_index=False)["Global_Sales"].sum()
with st.container(key="card_year"):
    card_head("Жилийн борлуулалтын чиг хандлага",
              "Сая хувь. 2016 он дутуу өгөгдөлтэй тул уналт бодит биш.")
    fig = px.line(by_year, x="Year", y="Global_Sales",
                  labels={"Global_Sales": UNIT, "Year": "Он"})
    fig.update_traces(line_color=BLUE)
    st.plotly_chart(style(fig), width="stretch")

c1, c2 = st.columns(2)

with c1.container(key="card_genre"):
    card_head("Төрлөөр", "Сая хувь")
    g = by_genre.reset_index().sort_values("Global_Sales")
    fig = px.bar(g, x="Global_Sales", y="Genre", orientation="h",
                 labels={"Global_Sales": UNIT, "Genre": ""})
    fig.update_traces(marker_color=BLUE)
    st.plotly_chart(style(fig), width="stretch")

with c2.container(key="card_plat"):
    card_head("Платформ ба бүс нутаг (Top 10)", "Сая хувь, бүс нутгаар задалсан")
    top_plat = f.groupby("Platform")["Global_Sales"].sum().nlargest(10).index
    p = (f[f["Platform"].isin(top_plat)]
         .groupby("Platform")[list(REGIONS)].sum().rename(columns=REGIONS)
         .loc[top_plat].reset_index()
         .melt(id_vars="Platform", var_name="Бүс нутаг", value_name="Sales"))
    fig = px.bar(p, x="Platform", y="Sales", color="Бүс нутаг",
                 color_discrete_map=COLORS, labels={"Sales": UNIT, "Platform": ""})
    st.plotly_chart(style(fig, legend=True), width="stretch")

c3, c4 = st.columns(2)

with c3.container(key="card_pub"):
    card_head("Хэвлэн гаргагч (Top 10)", "Сая хувь")
    pub = f.groupby("Publisher")["Global_Sales"].sum().nlargest(10).reset_index()
    pub = pub.sort_values("Global_Sales")
    fig = px.bar(pub, x="Global_Sales", y="Publisher", orientation="h",
                 labels={"Global_Sales": UNIT, "Publisher": ""})
    fig.update_traces(marker_color=BLUE)
    st.plotly_chart(style(fig), width="stretch")

reg = f[list(REGIONS)].sum().rename(index=REGIONS).reset_index()
reg.columns = ["Бүс нутаг", "Sales"]
with c4.container(key="card_reg"):
    card_head("Бүс нутгийн хувь", "Сонгосон шүүлтүүрийн нийт борлуулалтад")
    fig = px.pie(reg, names="Бүс нутаг", values="Sales", hole=0.5,
                 color="Бүс нутаг", color_discrete_map=COLORS)
    st.plotly_chart(style(fig, legend=True), width="stretch")

# ---------- Дүгнэлт ----------
peak = by_year.loc[by_year["Global_Sales"].idxmax()]
reg_sorted = reg.sort_values("Sales", ascending=False)
st.write("")
with st.container(key="insight"):
    st.markdown('<div class="ch">Дүгнэлт (шүүлтүүрээр шинэчлэгдэнэ)</div>',
                unsafe_allow_html=True)
    st.markdown(
        f"- Сонгосон хүрээнд борлуулалт хамгийн өндөр байсан жил нь "
        f"**{int(peak['Year'])}** ({peak['Global_Sales']:,.0f} сая хувь).\n"
        f"- Тэргүүлэх төрөл нь **{by_genre.index[0]}**: нийт борлуулалтын "
        f"{by_genre.iloc[0] / total * 100:.0f}%-ийг эзэлнэ.\n"
        f"- Хамгийн том зах зээл нь **{reg_sorted.iloc[0]['Бүс нутаг']}** "
        f"({reg_sorted.iloc[0]['Sales'] / total * 100:.0f}%). "
        f"Япон зөвхөн {f['JP_Sales'].sum() / total * 100:.0f}% байна.\n"
        f"- Платформоор тэргүүлэгч нь **{top_plat[0]}**.\n"
        "- Шинэ тоглоом гаргах бол тэргүүлэх төрөл, хамгийн том зах зээлд "
        "төвлөрвөл борлуулалтын боломж өндөр. Харин өрсөлдөөн ч тэнд хамгийн "
        "хүчтэй гэдгийг санаарай."
    )

# ---------- Арга зүй ----------
st.markdown(
    '<p class="note"><b>Арга зүйн тэмдэглэл.</b> Эх сурвалж: Kaggle "Video Game Sales" '
    '(vgchartz.com-аас цуглуулсан). Цэвэрлэгээ: оны утга эсвэл хэвлэн гаргагч хоосон '
    '311 мөр хасав; 2016 оноос хойших бараг хоосон мөрүүдийг хасав. Үлдсэн нь '
    '16,287 мөр. Нэгж нь сая хувь. Ганц эх сурвалжтай, 2016 он дутуу гэдгийг '
    'анхаарна уу.</p>', unsafe_allow_html=True)
