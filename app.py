
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, dash_table

DATA_PATH = Path(__file__).parent / "data" / "talabalar.csv"

FANLAR = ["Python", "Suniy_intellekt", "Statistika", "Tarmoqlar", "Data_viz"]
FAN_NOMI = {
    "Python": "Python",
    "Suniy_intellekt": "Sun’iy intellekt",
    "Statistika": "Statistika",
    "Tarmoqlar": "Kompyuter tarmoqlari",
    "Data_viz": "Data vizualizatsiya",
}

df = pd.read_csv(DATA_PATH)

# MUHIM: shu parametr "ID not found in layout" xatoligini yo‘qotadi.
app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "EduVision Analitika"

def filter_data(guruhlar, xavflar, ball_oraliq):
    d = df.copy()
    if guruhlar:
        d = d[d["Guruh"].isin(guruhlar)]
    if xavflar:
        d = d[d["Xavf_darajasi"].isin(xavflar)]
    d = d[d["Ortacha"].between(ball_oraliq[0], ball_oraliq[1])]
    return d

def fig_style(fig, height=400):
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=20, r=20, t=58, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        font=dict(family="Inter, Arial", color="#1e293b"),
        title_font=dict(size=18, color="#0f172a"),
        legend_title_text=""
    )
    return fig

def kpi_card(title, value, note, icon):
    return html.Div(className="metric-card", children=[
        html.Div(icon, className="metric-icon"),
        html.Div(title, className="metric-title"),
        html.Div(value, className="metric-value"),
        html.Div(note, className="metric-note")
    ])

def section_title(title, subtitle):
    return html.Div(className="section-head", children=[
        html.H2(title),
        html.P(subtitle)
    ])

def render_bosh_sahifa(d):
    avg = d["Ortacha"].mean()
    top = d.sort_values("Ortacha", ascending=False).iloc[0]
    eng_fan = d[FANLAR].mean().sort_values(ascending=False).index[0]
    yuqori_xavf = int((d["Xavf_darajasi"] == "Yuqori xavf").sum())

    fan_df = d[FANLAR].mean().sort_values(ascending=False).reset_index()
    fan_df.columns = ["Fan", "Ball"]
    fan_df["Fan"] = fan_df["Fan"].map(FAN_NOMI)

    fig_fan = px.bar(fan_df, x="Fan", y="Ball", text="Ball", title="Fanlar bo‘yicha umumiy ko‘rsatkich")
    fig_fan.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig_fan.update_layout(xaxis_title="", yaxis_title="Ball")

    xavf_df = d["Xavf_darajasi"].value_counts().reset_index()
    xavf_df.columns = ["Xavf darajasi", "Soni"]
    fig_xavf = px.pie(xavf_df, names="Xavf darajasi", values="Soni", hole=.62, title="Xavf darajasi taqsimoti")
    fig_xavf.update_traces(textinfo="percent+label")

    guruh_df = d.groupby("Guruh", as_index=False).agg(Ortacha=("Ortacha", "mean"), Davomat=("Davomat", "mean"), Talabalar=("Ism", "count"))
    fig_guruh = px.scatter(guruh_df, x="Davomat", y="Ortacha", size="Talabalar", color="Guruh",
                           title="Guruhlar: davomat va natija munosabati", hover_data=["Talabalar"])
    fig_guruh.update_layout(xaxis_title="Davomat (%)", yaxis_title="O‘rtacha ball")

    return html.Div([
        html.Div(className="hero-grid", children=[
            html.Div(className="hero-left", children=[
                html.Div("PLOTLY + DASH ANALITIKA PLATFORMASI", className="eyebrow"),
                html.H1("EduVision — talabalar natijasini tahlil qiluvchi zamonaviy platforma"),
                html.P("Ushbu loyiha talabalar baholari, davomat, loyiha balli va xavf darajasini interaktiv grafiklar orqali tahlil qiladi. Platforma odatiy dashboard emas, balki professional web-ilova ko‘rinishida ishlab chiqilgan."),
                html.Div(className="hero-actions", children=[
                    html.Span("Interaktiv grafiklar"),
                    html.Span("Xavf tahlili"),
                    html.Span("Talaba profili"),
                    html.Span("Avtomatik hisobot")
                ])
            ]),
            html.Div(className="hero-right", children=[
                html.Div("Umumiy natija", className="hero-card-label"),
                html.Div(f"{avg:.1f}", className="hero-score"),
                html.Div("o‘rtacha ball", className="hero-card-note"),
                html.Div(className="mini-line"),
                html.Div(f"Eng yuqori talaba: {top['Ism']} • {top['Guruh']}", className="hero-small"),
                html.Div(f"Eng kuchli fan: {FAN_NOMI[eng_fan]}", className="hero-small")
            ])
        ]),

        html.Div(className="metric-grid", children=[
            kpi_card("Talabalar", len(d), "filter bo‘yicha", "👥"),
            kpi_card("O‘rtacha ball", f"{avg:.1f}", "barcha fanlar", "📊"),
            kpi_card("Davomat", f"{d['Davomat'].mean():.1f}%", "o‘rtacha qatnashish", "🕒"),
            kpi_card("Yuqori xavf", yuqori_xavf, "nazorat kerak", "⚠️")
        ]),

        section_title("Platforma bo‘limlari", "Har bir bo‘lim alohida vazifani bajaradi, shuning uchun ma’lumotlar chalkashib ketmaydi."),
        html.Div(className="feature-grid", children=[
            html.Div([html.B("01"), html.H3("Bosh sahifa"), html.P("Umumiy natijalar, KPI va asosiy ko‘rsatkichlar.")], className="feature-card"),
            html.Div([html.B("02"), html.H3("Ma’lumotlar markazi"), html.P("Talabalar jadvali, qidiruv va reyting.")], className="feature-card"),
            html.Div([html.B("03"), html.H3("Tahlil laboratoriyasi"), html.P("Fanlar, guruhlar, heatmap, line va radar grafiklar.")], className="feature-card"),
            html.Div([html.B("04"), html.H3("Talaba profili"), html.P("Bitta talabaning individual akademik ko‘rsatkichi.")], className="feature-card"),
            html.Div([html.B("05"), html.H3("Xavf tahlili"), html.P("Risk ball va yordam kerak talabalar ro‘yxati.")], className="feature-card"),
            html.Div([html.B("06"), html.H3("Hisobot"), html.P("Himoyada gapirishga mos avtomatik xulosa.")], className="feature-card"),
        ]),

        html.Div(className="chart-grid", children=[
            html.Div(dcc.Graph(figure=fig_style(fig_fan, 410)), className="chart-card wide"),
            html.Div(dcc.Graph(figure=fig_style(fig_xavf, 410)), className="chart-card"),
            html.Div(dcc.Graph(figure=fig_style(fig_guruh, 410)), className="chart-card wide")
        ])
    ])

def render_malumotlar(d):
    top = d.sort_values("Ortacha", ascending=False).head(14)
    fig = px.bar(top, y="Ism", x="Ortacha", color="Guruh", orientation="h", text="Ortacha", title="Talabalar reytingi")
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, xaxis_title="O‘rtacha ball", yaxis_title="")
    fig.update_traces(texttemplate="%{text:.1f}")

    table_df = d[["ID", "Ism", "Guruh", "Ortacha", "Daraja", "Xavf_darajasi", "Davomat", "Loyiha_ball", "Faollik"] + FANLAR].copy()
    table_df = table_df.rename(columns={
        "Ortacha": "O‘rtacha",
        "Xavf_darajasi": "Xavf darajasi",
        "Loyiha_ball": "Loyiha ball",
        "Suniy_intellekt": "Sun’iy intellekt",
        "Tarmoqlar": "Kompyuter tarmoqlari",
        "Data_viz": "Data vizualizatsiya"
    })

    return html.Div([
        section_title("Ma’lumotlar markazi", "Bu sahifada talabalar bazasi, reyting va jadval ko‘rinishidagi ma’lumotlar joylashgan."),
        html.Div(className="split-layout", children=[
            html.Div(dcc.Graph(figure=fig_style(fig, 520)), className="chart-card"),
            html.Div(className="table-card", children=[
                html.H3("Talabalar jadvali"),
                html.P("Jadvalda fan ballari, davomat, loyiha balli, daraja va xavf holati berilgan."),
                dash_table.DataTable(
                    data=table_df.to_dict("records"),
                    columns=[{"name": c, "id": c} for c in table_df.columns],
                    page_size=12,
                    sort_action="native",
                    filter_action="native",
                    style_table={"overflowX": "auto"},
                    style_cell={"fontFamily": "Inter", "fontSize": "13px", "padding": "10px", "textAlign": "left", "minWidth": "90px"},
                    style_header={"backgroundColor": "#0f172a", "color": "white", "fontWeight": "800"},
                    style_data_conditional=[
                        {"if": {"filter_query": "{Xavf darajasi} = 'Yuqori xavf'"}, "backgroundColor": "#fff1f2"},
                        {"if": {"filter_query": "{Daraja} = 'A’lo'"}, "backgroundColor": "#ecfdf5"}
                    ],
                )
            ])
        ])
    ])

def render_tahlil(d):
    fan_df = d[FANLAR].mean().sort_values(ascending=False).reset_index()
    fan_df.columns = ["Fan", "Ball"]
    fan_df["Fan"] = fan_df["Fan"].map(FAN_NOMI)

    long = d.melt(id_vars=["Ism", "Guruh"], value_vars=FANLAR, var_name="Fan", value_name="Ball")
    long["Fan"] = long["Fan"].map(FAN_NOMI)

    heat = d.groupby("Guruh")[FANLAR].mean().round(1)
    heat.columns = [FAN_NOMI[c] for c in heat.columns]

    hafta_cols = [f"Hafta_{i}" for i in range(1, 7)]
    hafta = d.melt(id_vars=["Ism", "Guruh"], value_vars=hafta_cols, var_name="Hafta", value_name="Ball")
    hafta["Hafta"] = hafta["Hafta"].str.replace("Hafta_", "Hafta ")
    hafta_mean = hafta.groupby(["Hafta", "Guruh"], as_index=False)["Ball"].mean()

    fig_bar = px.bar(fan_df, x="Fan", y="Ball", text="Ball", title="Fanlar bo‘yicha o‘rtacha natija")
    fig_bar.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig_bar.update_layout(xaxis_title="", yaxis_title="Ball")

    fig_box = px.box(long, x="Fan", y="Ball", color="Fan", title="Fanlar bo‘yicha ball tarqalishi")
    fig_box.update_layout(showlegend=False, xaxis_title="", yaxis_title="Ball")

    fig_heat = px.imshow(heat, text_auto=True, aspect="auto", title="Heatmap: guruhlar va fanlar kesimi")
    fig_heat.update_layout(xaxis_title="Fanlar", yaxis_title="Guruh")

    fig_line = px.line(hafta_mean, x="Hafta", y="Ball", color="Guruh", markers=True, title="Haftalik rivojlanish dinamikasi")
    fig_line.update_layout(xaxis_title="", yaxis_title="Ball")

    radar = d.groupby("Guruh")[FANLAR].mean().round(1).reset_index()
    fig_radar = go.Figure()
    for _, row in radar.iterrows():
        fig_radar.add_trace(go.Scatterpolar(
            r=[row[f] for f in FANLAR],
            theta=[FAN_NOMI[f] for f in FANLAR],
            fill="toself",
            name=row["Guruh"]
        ))
    fig_radar.update_layout(title="Radar profil: guruhlarning fan ko‘rsatkichlari", polar=dict(radialaxis=dict(visible=True, range=[40, 100])), template="plotly_white")

    return html.Div([
        section_title("Tahlil laboratoriyasi", "Fanlar, guruhlar va haftalik o‘zgarishlar interaktiv grafiklar orqali tahlil qilinadi."),
        html.Div(className="chart-grid", children=[
            html.Div(dcc.Graph(figure=fig_style(fig_bar, 405)), className="chart-card"),
            html.Div(dcc.Graph(figure=fig_style(fig_box, 405)), className="chart-card"),
            html.Div(dcc.Graph(figure=fig_style(fig_heat, 440)), className="chart-card wide"),
            html.Div(dcc.Graph(figure=fig_style(fig_line, 420)), className="chart-card"),
            html.Div(dcc.Graph(figure=fig_style(fig_radar, 420)), className="chart-card")
        ])
    ])

def render_talaba(d):
    return html.Div([
        section_title("Talaba profili", "Bitta talabani tanlab, uning individual natijasi va rivojlanishini ko‘rish mumkin."),
        html.Div(className="student-toolbar", children=[
            html.Div("Talabani tanlang:", className="toolbar-label"),
            dcc.Dropdown(
                id="talaba-tanlash",
                options=[{"label": name, "value": name} for name in sorted(d["Ism"].unique())],
                value=sorted(d["Ism"].unique())[0],
                clearable=False,
                className="student-dropdown"
            )
        ]),
        html.Div(id="talaba-profil-natija")
    ])

def render_xavf(d):
    xavf_df = d["Xavf_darajasi"].value_counts().reset_index()
    xavf_df.columns = ["Xavf darajasi", "Soni"]

    fig_bar = px.bar(xavf_df, x="Xavf darajasi", y="Soni", text="Soni", title="Xavf darajalari bo‘yicha taqsimot")
    fig_bar.update_traces(textposition="outside")
    fig_bar.update_layout(xaxis_title="", yaxis_title="Talabalar soni")

    fig_scatter = px.scatter(d, x="Ortacha", y="Risk_ball", color="Xavf_darajasi", size="Davomat",
                             hover_name="Ism", hover_data=["Guruh", "Loyiha_ball"],
                             title="Risk ball va o‘rtacha natija munosabati")
    fig_scatter.update_layout(xaxis_title="O‘rtacha ball", yaxis_title="Risk ball")

    high = d.sort_values("Risk_ball", ascending=False).head(8)
    cards = []
    for _, row in high.iterrows():
        cards.append(html.Div(className="risk-card", children=[
            html.Div(row["Ism"], className="risk-name"),
            html.Div(f"{row['Guruh']} • {row['Xavf_darajasi']}", className="risk-meta"),
            html.Div(className="risk-stats", children=[
                html.Span(f"Ball: {row['Ortacha']}"),
                html.Span(f"Davomat: {row['Davomat']}%"),
                html.Span(f"Risk: {row['Risk_ball']}")
            ])
        ]))

    return html.Div([
        section_title("Xavf tahlili", "Bu bo‘lim o‘rtacha ball, davomat va loyiha balli asosida e’tibor kerak talabalarni aniqlaydi."),
        html.Div(className="insight-row", children=[
            html.Div([html.H3("Risk ball nima?"), html.P("Risk ball past baho, past davomat va past loyiha natijasiga qarab hisoblanadi.")], className="insight-panel"),
            html.Div([html.H3("Amaliy foyda"), html.P("O‘qituvchi kim bilan individual ishlash kerakligini tez ko‘radi.")], className="insight-panel")
        ]),
        html.Div(className="chart-grid", children=[
            html.Div(dcc.Graph(figure=fig_style(fig_bar, 390)), className="chart-card"),
            html.Div(dcc.Graph(figure=fig_style(fig_scatter, 390)), className="chart-card")
        ]),
        html.H3("E’tibor kerak talabalar", className="mini-title"),
        html.Div(cards, className="risk-grid")
    ])

def render_hisobot(d):
    s = d[FANLAR].mean().sort_values(ascending=False)
    group_mean = d.groupby("Guruh")["Ortacha"].mean().sort_values(ascending=False)
    top = d.sort_values("Ortacha", ascending=False).iloc[0]
    weak = d.sort_values("Ortacha").iloc[0]
    yuqori_xavf = int((d["Xavf_darajasi"] == "Yuqori xavf").sum())
    corr = d["Davomat"].corr(d["Ortacha"])

    return html.Div([
        section_title("Hisobot", "Himoyada gapirishga tayyor, qisqa va tushunarli loyiha hisoboti."),
        html.Div(className="report-layout", children=[
            html.Div(className="report-paper", children=[
                html.H2("Loyiha bo‘yicha avtomatik hisobot"),
                html.P(f"Ushbu loyiha “Interaktiv vizualizatsiya dashboardi — Plotly yordamida” mavzusi asosida yaratildi. Dastur jami {len(d)} ta talaba ma’lumotini tahlil qiladi."),
                html.P(f"Umumiy o‘rtacha ball {d['Ortacha'].mean():.1f} ni tashkil etdi. Eng yuqori natija {top['Ism']} ismli talabada kuzatildi. Ko‘proq yordam kerak bo‘lgan talaba esa {weak['Ism']} deb belgilandi."),
                html.P(f"Fanlar tahliliga ko‘ra eng yaxshi fan {FAN_NOMI[s.index[0]]}, nisbatan past fan esa {FAN_NOMI[s.index[-1]]}. Guruhlar ichida eng yuqori o‘rtacha ko‘rsatkich {group_mean.index[0]} guruhida."),
                html.P(f"Xavf tahlilda yuqori xavf guruhidagi talabalar soni {yuqori_xavf} ta. Davomat va o‘zlashtirish orasidagi bog‘liqlik koeffitsiyenti {corr:.2f}."),
                html.P("Xulosa qilib aytganda, platforma o‘qituvchiga talabalar natijasini tez tahlil qilish, past natijali talabalarni aniqlash va ta’lim jarayonini yaxshilash bo‘yicha qaror qabul qilishga yordam beradi.")
            ]),
            html.Div(className="report-side", children=[
                html.Div([html.B("Texnologiyalar"), html.P("Python, Dash, Plotly, Pandas")], className="side-note"),
                html.Div([html.B("Dizayn"), html.P("Professional analitika platformasi")], className="side-note"),
                html.Div([html.B("Asosiy natija"), html.P("Interaktiv grafik + xavf tahlili")], className="side-note")
            ])
        ])
    ])

app.layout = html.Div(className="app-shell", children=[
    dcc.Store(id="filterlangan-malumot"),
    html.Header(className="topbar", children=[
        html.Div(className="brand", children=[
            html.Div("EV", className="brand-logo"),
            html.Div([
                html.Div("EduVision", className="brand-name"),
                html.Div("Analitika platformasi", className="brand-sub")
            ])
        ]),
        dcc.RadioItems(
            id="sahifa-tanlash",
            className="top-nav",
            options=[
                {"label": "Bosh sahifa", "value": "bosh"},
                {"label": "Ma’lumotlar", "value": "malumot"},
                {"label": "Tahlil", "value": "tahlil"},
                {"label": "Talaba profili", "value": "talaba"},
                {"label": "Xavf tahlili", "value": "xavf"},
                {"label": "Hisobot", "value": "hisobot"},
            ],
            value="bosh",
            inline=True
        )
    ]),

    html.Div(className="filter-bar", children=[
        html.Div(className="filter-item", children=[
            html.Label("Guruhlar"),
            dcc.Checklist(
                id="guruh-filter",
                options=[{"label": g, "value": g} for g in sorted(df["Guruh"].unique())],
                value=sorted(df["Guruh"].unique()),
                inline=True,
                className="pill-checklist"
            )
        ]),
        html.Div(className="filter-item", children=[
            html.Label("Xavf darajasi"),
            dcc.Checklist(
                id="xavf-filter",
                options=[{"label": r, "value": r} for r in ["Past xavf", "O‘rta xavf", "Yuqori xavf"]],
                value=["Past xavf", "O‘rta xavf", "Yuqori xavf"],
                inline=True,
                className="pill-checklist"
            )
        ]),
        html.Div(className="filter-item wide-filter", children=[
            html.Label("Ball oralig‘i"),
            dcc.RangeSlider(id="ball-filter", min=0, max=100, step=1, value=[0, 100],
                            marks={0: "0", 50: "50", 100: "100"},
                            tooltip={"placement": "bottom", "always_visible": False})
        ])
    ]),

    html.Main(id="sahifa-content", className="page-content")
])

@app.callback(
    Output("filterlangan-malumot", "data"),
    Input("guruh-filter", "value"),
    Input("xavf-filter", "value"),
    Input("ball-filter", "value")
)
def update_data(guruhlar, xavflar, ball_oraliq):
    d = filter_data(guruhlar, xavflar, ball_oraliq)
    return d.to_dict("records")

@app.callback(
    Output("sahifa-content", "children"),
    Input("sahifa-tanlash", "value"),
    Input("filterlangan-malumot", "data")
)
def update_page(sahifa, records):
    d = pd.DataFrame(records)
    if d.empty:
        return html.Div(className="empty-state", children=[
            html.H2("Ma’lumot topilmadi"),
            html.P("Filterlarni kengaytiring yoki boshqa guruhni tanlang.")
        ])

    if sahifa == "bosh":
        return render_bosh_sahifa(d)
    if sahifa == "malumot":
        return render_malumotlar(d)
    if sahifa == "tahlil":
        return render_tahlil(d)
    if sahifa == "talaba":
        return render_talaba(d)
    if sahifa == "xavf":
        return render_xavf(d)
    return render_hisobot(d)

@app.callback(
    Output("talaba-profil-natija", "children"),
    Input("talaba-tanlash", "value"),
    Input("filterlangan-malumot", "data")
)
def update_talaba_profile(talaba_ismi, records):
    d = pd.DataFrame(records)
    if d.empty or talaba_ismi not in d["Ism"].values:
        return html.Div(className="empty-state", children="Talaba topilmadi.")

    s = d[d["Ism"] == talaba_ismi].iloc[0]

    score_df = pd.DataFrame({"Fan": [FAN_NOMI[x] for x in FANLAR], "Ball": [s[x] for x in FANLAR]})
    hafta_df = pd.DataFrame({"Hafta": [f"Hafta {i}" for i in range(1, 7)], "Ball": [s[f"Hafta_{i}"] for i in range(1, 7)]})

    fig_bar = px.bar(score_df, x="Fan", y="Ball", text="Ball", title=f"{s['Ism']} — fanlar bo‘yicha natija")
    fig_bar.update_traces(textposition="outside")
    fig_bar.update_layout(xaxis_title="", yaxis_title="Ball")

    fig_line = px.line(hafta_df, x="Hafta", y="Ball", markers=True, title="Haftalik rivojlanish")
    fig_line.update_layout(xaxis_title="", yaxis_title="Ball")

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=float(s["Ortacha"]),
        title={"text": "O‘rtacha ball"},
        gauge={"axis": {"range": [0, 100]}}
    ))

    if s["Ortacha"] >= 86:
        tavsiya = "Talaba yuqori natijaga ega. Murakkabroq loyiha va mustaqil tadqiqot berish mumkin."
    elif s["Ortacha"] >= 71:
        tavsiya = "Natija yaxshi. Ayrim fanlar bo‘yicha mustahkamlash ishlari yetarli bo‘ladi."
    elif s["Ortacha"] >= 56:
        tavsiya = "Qo‘shimcha mashg‘ulot, mini-test va muntazam nazorat tavsiya etiladi."
    else:
        tavsiya = "Talaba bilan individual reja asosida ishlash va davomatni nazorat qilish zarur."

    return html.Div(className="student-view", children=[
        html.Div(className="student-card", children=[
            html.Div("Talaba profili", className="eyebrow dark"),
            html.H2(s["Ism"]),
            html.P(f"Guruh: {s['Guruh']}"),
            html.Div(className="student-stats", children=[
                html.Span(f"O‘rtacha: {s['Ortacha']}"),
                html.Span(f"Davomat: {s['Davomat']}%"),
                html.Span(f"Loyiha: {s['Loyiha_ball']}"),
                html.Span(f"Xavf: {s['Xavf_darajasi']}")
            ]),
            html.Div(tavsiya, className="student-advice")
        ]),
        html.Div(dcc.Graph(figure=fig_style(fig_gauge, 310)), className="chart-card"),
        html.Div(dcc.Graph(figure=fig_style(fig_bar, 420)), className="chart-card wide"),
        html.Div(dcc.Graph(figure=fig_style(fig_line, 420)), className="chart-card")
    ])

if __name__ == "__main__":
    app.run(debug=False)
