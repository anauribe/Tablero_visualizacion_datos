"""
Tablero interactivo — Desarrollo mundial (dataset Gapminder)
Unidad 3 · Actividad de tablero con Streamlit

Lógica de la app (reactividad):
1. Se cargan los datos UNA sola vez (con cache) al iniciar.
2. El usuario modifica los INPUTS en la barra lateral (continente y año).
3. Streamlit vuelve a ejecutar el script de arriba a abajo cada vez que
   cambia un input, así que el DataFrame filtrado ('df_filtrado') se
   recalcula automáticamente.
4. Todos los OUTPUTS (texto, gráfico, tabla) se generan a partir de ese
   mismo DataFrame filtrado, por lo que quedan sincronizados entre sí.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------------------------------------------------
# 0. CONFIGURACIÓN GENERAL DE LA PÁGINA
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Desarrollo mundial · Gapminder",
    page_icon="🌍",
    layout="wide",
)

# Paleta de color consistente para los 5 continentes (criterio de diseño:
# mismo color = misma categoría en todo el tablero)
PALETA_CONTINENTES = {
    "Africa": "#B85042",
    "Americas": "#8FA98B",
    "Asia": "#3A6B8A",
    "Europe": "#D9A441",
    "Oceania": "#7A5C61",
}


# ----------------------------------------------------------------------
# 1. CARGA DE DATOS (dataset real, incluido en Plotly Express)
# ----------------------------------------------------------------------
@st.cache_data
def cargar_datos() -> pd.DataFrame:
    """Carga el dataset Gapminder (datos reales del Banco Mundial / ONU:
    esperanza de vida, PIB per cápita y población por país, 1952-2007)."""
    df = px.data.gapminder()
    return df


df = cargar_datos()

anios_disponibles = sorted(df["year"].unique().tolist())
continentes_disponibles = sorted(df["continent"].unique().tolist())


# ----------------------------------------------------------------------
# 2. ENCABEZADO
# ----------------------------------------------------------------------
st.title("🌍 Desarrollo mundial: esperanza de vida, PIB e población")
st.caption(
    "Fuente: Gapminder (Banco Mundial / Naciones Unidas), integrado en "
    "Plotly Express · Datos reales, 1952–2007"
)
st.markdown(
    "Explora cómo se relacionan la **riqueza (PIB per cápita)** y la "
    "**esperanza de vida** entre países y continentes. Usa los controles "
    "de la izquierda para filtrar el tablero."
)
st.divider()


# ----------------------------------------------------------------------
# 3. INPUTS (barra lateral) — el usuario modifica estas condiciones
# ----------------------------------------------------------------------
st.sidebar.header("🎛️ Filtros")

continentes_sel = st.sidebar.multiselect(
    "Continente(s)",
    options=continentes_disponibles,
    default=continentes_disponibles,
    help="Selecciona uno o varios continentes para comparar.",
)

anio_sel = st.sidebar.select_slider(
    "Año",
    options=anios_disponibles,
    value=anios_disponibles[-1],  # 2007 por defecto
    help="El dataset solo tiene registros cada 5 años.",
)

pob_min_millones = st.sidebar.slider(
    "Población mínima del país (millones)",
    min_value=0,
    max_value=50,
    value=0,
    step=1,
    help="Filtra países pequeños si quieres enfocarte en los más poblados.",
)

st.sidebar.divider()
st.sidebar.caption(
    "Tablero desarrollado con Streamlit + Plotly Express · "
    "Actividad Unidad 3"
)


# ----------------------------------------------------------------------
# 4. FILTRADO REACTIVO — se recalcula cada vez que cambia un input
# ----------------------------------------------------------------------
if not continentes_sel:
    st.warning("Selecciona al menos un continente en la barra lateral.")
    st.stop()

df_filtrado = df[
    (df["continent"].isin(continentes_sel))
    & (df["year"] == anio_sel)
    & (df["pop"] >= pob_min_millones * 1_000_000)
].copy()

if df_filtrado.empty:
    st.warning("No hay países que cumplan con estos filtros. Ajusta los controles.")
    st.stop()


# ----------------------------------------------------------------------
# 5. OUTPUT DE TEXTO — resumen estadístico calculado sobre la selección
# ----------------------------------------------------------------------
st.subheader(f"📊 Resumen para {anio_sel}")

col1, col2, col3, col4 = st.columns(4)

esperanza_prom = df_filtrado["lifeExp"].mean()
pib_prom = df_filtrado["gdpPercap"].mean()
pob_total = df_filtrado["pop"].sum()
n_paises = df_filtrado["country"].nunique()

col1.metric("Países incluidos", f"{n_paises}")
col2.metric("Esperanza de vida promedio", f"{esperanza_prom:,.1f} años")
col3.metric("PIB per cápita promedio", f"${pib_prom:,.0f}")
col4.metric("Población total", f"{pob_total / 1_000_000_000:,.2f} mil M")

pais_mayor_esperanza = df_filtrado.loc[df_filtrado["lifeExp"].idxmax()]
pais_menor_esperanza = df_filtrado.loc[df_filtrado["lifeExp"].idxmin()]

st.markdown(
    f"En **{anio_sel}**, con los filtros actuales, **{pais_mayor_esperanza['country']}** "
    f"tiene la mayor esperanza de vida (**{pais_mayor_esperanza['lifeExp']:.1f} años**), "
    f"mientras que **{pais_menor_esperanza['country']}** tiene la menor "
    f"(**{pais_menor_esperanza['lifeExp']:.1f} años**)."
)

st.divider()


# ----------------------------------------------------------------------
# 6. GRÁFICO — Plotly Express, coherente con la selección de inputs
# ----------------------------------------------------------------------
st.subheader("📈 Relación entre riqueza y esperanza de vida")

fig = px.scatter(
    df_filtrado,
    x="gdpPercap",
    y="lifeExp",
    size="pop",
    color="continent",
    color_discrete_map=PALETA_CONTINENTES,
    hover_name="country",
    log_x=True,
    size_max=55,
    labels={
        "gdpPercap": "PIB per cápita (USD, escala log)",
        "lifeExp": "Esperanza de vida (años)",
        "continent": "Continente",
        "pop": "Población",
    },
    title=f"PIB per cápita vs. esperanza de vida — {anio_sel}",
)
fig.update_layout(
    plot_bgcolor="white",
    legend_title_text="Continente",
    title_font_size=18,
    margin=dict(l=10, r=10, t=50, b=10),
)
fig.update_xaxes(gridcolor="#EDEDED")
fig.update_yaxes(gridcolor="#EDEDED")

st.plotly_chart(fig, use_container_width=True)

st.divider()


# ----------------------------------------------------------------------
# 7. TABLA — subconjunto filtrado de los datos
# ----------------------------------------------------------------------
st.subheader("🔎 Datos filtrados")

columnas_a_mostrar = ["country", "continent", "year", "lifeExp", "pop", "gdpPercap"]
df_tabla = (
    df_filtrado[columnas_a_mostrar]
    .sort_values("lifeExp", ascending=False)
    .rename(
        columns={
            "country": "País",
            "continent": "Continente",
            "year": "Año",
            "lifeExp": "Esperanza de vida",
            "pop": "Población",
            "gdpPercap": "PIB per cápita",
        }
    )
    .reset_index(drop=True)
)

st.dataframe(
    df_tabla,
    use_container_width=True,
    column_config={
        "Esperanza de vida": st.column_config.NumberColumn(format="%.1f años"),
        "Población": st.column_config.NumberColumn(format="%d"),
        "PIB per cápita": st.column_config.NumberColumn(format="$%.0f"),
    },
)

st.caption(f"Mostrando {len(df_tabla)} países que cumplen los filtros seleccionados.")
