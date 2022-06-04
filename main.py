import base64
import re
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


def main():
    title = "はてなアンテナの登録ドメイン数の推移"
    st.set_page_config(page_title=title, layout="wide")
    src_df = pd.read_csv("data.csv")
    df = create_dataframe(src_df)
    st.header(title)
    st.markdown(
        """
        [はてなアンテナは20周年を迎えました](https://labo.hatenastaff.com/entry/antenna-20th)
        に掲載されていた、年ごとの登録ドメイン数の推移をグラフにしてみました。
        """
    )
    st.write("")
    st.altair_chart(create_chart(df))
    set_style()


@st.cache
def create_dataframe(src_df: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame(columns=["domain", "year", "rank"])
    for year in src_df:
        domains = src_df[year].dropna()
        images = domains.map(read_image)
        year_df = pd.DataFrame(
            {
                "domain": domains,
                "rank": pd.RangeIndex(start=1, stop=domains.size + 1),
                "year": pd.to_datetime(year),
                "image": images,
            }
        )
        # year_df = year_df.query("rank <= 20")
        df = pd.concat([df, year_df])
    df = df.sort_values(["year", "rank"]).reset_index(drop=True)
    return df


@st.cache
def read_image(domain):
    domain = remove_wildcard(domain)
    png_dir = Path("./favicon/png")
    png_file = png_dir.joinpath(f"{domain}.png")
    if not png_file.exists():
        return None
    png = png_file.open("rb").read()
    base64_png = "data:image/png;base64," + base64.b64encode(png).decode()
    return base64_png


@st.cache
def remove_wildcard(domain: str) -> str:
    match = re.search(r"\*\.(.+)$", domain)
    if match:
        return match[1]
    return domain


def create_chart(df):
    highlight = alt.selection_single(
        fields=["domain"],
        on="mouseover",
        nearest=False,
        empty="none",
    )
    line_chart = (
        alt.Chart(df)
        .mark_line(
            point=True,
            interpolate="monotone",
            strokeWidth=8,
        )
        .encode(
            x=alt.X(
                "year(year):T",
                title="",
                scale=alt.Scale(padding=40),
                axis=alt.Axis(
                    orient="top",
                    labelFontSize=14,
                    labelFontWeight="bold",
                    labelColor="#333",
                    gridColor="#E6E6E6",
                ),
            ),
            y=alt.Y(
                "rank:O",
                title="",
                impute=alt.ImputeParams(
                    value=None,
                ),
                scale=alt.Scale(
                    domain=df["rank"].unique().tolist(), padding=10
                ),
                axis=alt.Axis(
                    labelFontSize=18,
                    labelColor="#999",
                ),
            ),
            order="year",
            color=alt.Color("domain:N", legend=None),
            tooltip="domain",
            strokeOpacity=alt.condition(
                highlight, alt.value(1), alt.value(0.3)
            ),
        )
        .add_selection(highlight)
    )
    icon_df = df.query("not image.isnull()")
    icon_chart = (
        alt.Chart(icon_df)
        .mark_image(width=20, height=20)
        .encode(
            x=alt.X("year:T"),
            y=alt.Y("rank:O"),
            tooltip="domain",
            url="image",
        )
    )
    return (
        alt.layer(
            line_chart,
            icon_chart,
        )
        .properties(width=1000, height=1000)
        .configure()
        .configure_point(size=140)
        .configure_axis(
            ticks=False,
            domain=False,
        )
        .configure_view(strokeWidth=0)
    )


def set_style():
    css = """
    <style>
      button[title="View fullscreen"] {
        display: none;
      }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


main()
