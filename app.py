"""
App de Streamlit: Análisis de Competencias Deportivas Olímpicas (datos sintéticos)
-----------------------------------------------------------------------------------
Genera un dataset sintético de competencias olímpicas y permite explorar:
  1. Análisis cuantitativo (estadísticas descriptivas, correlaciones, agregaciones)
  2. Análisis cualitativo (frecuencias, tablas cruzadas, composición categórica)
  3. Gráficos interactivos (Plotly)

Ejecutar con:
    streamlit run app.py
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from faker import Faker

# ----------------------------------------------------------------------------
# Configuración general
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Analítica de Competencias Olímpicas",
    page_icon="🏅",
    layout="wide",
)

fake = Faker()

DEPORTES = {
    "Atletismo": ["100m", "200m", "400m", "Maratón", "Salto largo", "Lanzamiento de jabalina"],
    "Natación": ["50m libre", "100m libre", "200m mariposa", "400m estilos"],
    "Gimnasia": ["Suelo", "Barra fija", "Anillas", "Salto de potro"],
    "Ciclismo": ["Ruta", "Pista", "BMX", "Montaña"],
    "Halterofilia": ["-61kg", "-73kg", "-89kg", "+109kg"],
    "Judo": ["-60kg", "-73kg", "-90kg", "+100kg"],
    "Tiro con arco": ["Individual", "Por equipos"],
    "Boxeo": ["Peso pluma", "Peso welter", "Peso pesado"],
}

PAISES = [
    "Colombia", "Estados Unidos", "China", "Japón", "Brasil", "Francia",
    "Alemania", "Kenia", "Jamaica", "Australia", "España", "Italia",
    "Reino Unido", "Cuba", "México", "Canadá", "Países Bajos", "Sudáfrica",
]

CONTINENTE = {
    "Colombia": "América", "Estados Unidos": "América", "China": "Asia",
    "Japón": "Asia", "Brasil": "América", "Francia": "Europa",
    "Alemania": "Europa", "Kenia": "África", "Jamaica": "América",
    "Australia": "Oceanía", "España": "Europa", "Italia": "Europa",
    "Reino Unido": "Europa", "Cuba": "América", "México": "América",
    "Canadá": "América", "Países Bajos": "Europa", "Sudáfrica": "África",
}

MEDALLAS = ["Oro", "Plata", "Bronce", "Sin medalla"]
GENERO = ["Masculino", "Femenino"]


@st.cache_data(show_spinner=False)
def generar_datos(n_registros: int, semilla: int) -> pd.DataFrame:
    """Genera un dataset sintético de resultados de competencias olímpicas."""
    rng = np.random.default_rng(semilla)
    Faker.seed(semilla)
    local_fake = Faker()

    registros = []
    for i in range(n_registros):
        deporte = rng.choice(list(DEPORTES.keys()))
        prueba = rng.choice(DEPORTES[deporte])
        pais = rng.choice(PAISES)
        genero = rng.choice(GENERO)
        edad = int(np.clip(rng.normal(24, 4), 15, 45))

        # Probabilidad de medalla (no todos ganan)
        medalla = rng.choice(MEDALLAS, p=[0.08, 0.08, 0.08, 0.76])

        # Puntaje / marca sintética (escala 0-100, con algo de ruido por edad y medalla)
        base = rng.normal(70, 12)
        bonus_medalla = {"Oro": 20, "Plata": 12, "Bronce": 6, "Sin medalla": 0}[medalla]
        puntaje = float(np.clip(base + bonus_medalla - abs(edad - 24) * 0.3, 0, 100))

        horas_entrenamiento = float(np.clip(rng.normal(28, 6), 8, 50))
        altura_cm = float(np.clip(rng.normal(175, 10), 150, 210))
        peso_kg = float(np.clip(rng.normal(70, 12), 45, 130))
        años_experiencia = int(np.clip(rng.normal(8, 4), 0, 25))

        registros.append({
            "atleta": local_fake.name(),
            "pais": pais,
            "continente": CONTINENTE[pais],
            "genero": genero,
            "edad": edad,
            "deporte": deporte,
            "prueba": prueba,
            "medalla": medalla,
            "puntaje_desempeno": round(puntaje, 2),
            "horas_entrenamiento_semana": round(horas_entrenamiento, 1),
            "altura_cm": round(altura_cm, 1),
            "peso_kg": round(peso_kg, 1),
            "anios_experiencia": años_experiencia,
        })

    df = pd.DataFrame(registros)
    df.insert(0, "id", range(1, len(df) + 1))
    return df


# ----------------------------------------------------------------------------
# Barra lateral: parámetros de generación y filtros
# ----------------------------------------------------------------------------
st.sidebar.header("⚙️ Parámetros de generación")
n_registros = st.sidebar.slider("Número de registros", 100, 5000, 1000, step=100)
semilla = st.sidebar.number_input("Semilla aleatoria", value=42, step=1)

df = generar_datos(n_registros, semilla)

st.sidebar.header("🔎 Filtros")
deportes_sel = st.sidebar.multiselect("Deporte", sorted(df["deporte"].unique()))
paises_sel = st.sidebar.multiselect("País", sorted(df["pais"].unique()))
genero_sel = st.sidebar.multiselect("Género", sorted(df["genero"].unique()))
medalla_sel = st.sidebar.multiselect("Medalla", MEDALLAS)

df_filtrado = df.copy()
if deportes_sel:
    df_filtrado = df_filtrado[df_filtrado["deporte"].isin(deportes_sel)]
if paises_sel:
    df_filtrado = df_filtrado[df_filtrado["pais"].isin(paises_sel)]
if genero_sel:
    df_filtrado = df_filtrado[df_filtrado["genero"].isin(genero_sel)]
if medalla_sel:
    df_filtrado = df_filtrado[df_filtrado["medalla"].isin(medalla_sel)]

if st.sidebar.button("🔄 Regenerar datos"):
    generar_datos.clear()
    st.rerun()

# ----------------------------------------------------------------------------
# Encabezado
# ----------------------------------------------------------------------------
st.title("🏅 Analítica de Competencias Deportivas Olímpicas")
st.caption("Dataset 100% sintético generado con Faker + NumPy, solo para fines demostrativos/analíticos.")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Registros filtrados", f"{len(df_filtrado):,}")
col2.metric("Países", df_filtrado["pais"].nunique())
col3.metric("Deportes", df_filtrado["deporte"].nunique())
col4.metric("Medallistas", int((df_filtrado["medalla"] != "Sin medalla").sum()))

st.divider()

if df_filtrado.empty:
    st.warning("No hay datos con los filtros seleccionados. Ajusta los filtros en la barra lateral.")
    st.stop()

tab_datos, tab_cuant, tab_cual, tab_graf = st.tabs(
    ["📄 Datos", "📊 Análisis cuantitativo", "🗂️ Análisis cualitativo", "📈 Gráficos interactivos"]
)

# ----------------------------------------------------------------------------
# Tab: Datos crudos
# ----------------------------------------------------------------------------
with tab_datos:
    st.subheader("Vista de datos")
    st.dataframe(df_filtrado, use_container_width=True, height=400)
    csv = df_filtrado.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Descargar CSV filtrado", csv, "olimpicos_sinteticos.csv", "text/csv")

# ----------------------------------------------------------------------------
# Tab: Análisis cuantitativo
# ----------------------------------------------------------------------------
with tab_cuant:
    st.subheader("Estadísticas descriptivas")
    variables_num = [
        "edad", "puntaje_desempeno", "horas_entrenamiento_semana",
        "altura_cm", "peso_kg", "anios_experiencia",
    ]
    st.dataframe(df_filtrado[variables_num].describe().T, use_container_width=True)

    st.subheader("Agregaciones por grupo")
    col_a, col_b = st.columns(2)
    with col_a:
        agrupar_por = st.selectbox(
            "Agrupar por", ["deporte", "pais", "continente", "genero", "medalla"], index=0
        )
    with col_b:
        variable_metrica = st.selectbox("Variable numérica", variables_num, index=1)

    resumen = (
        df_filtrado.groupby(agrupar_por)[variable_metrica]
        .agg(["mean", "median", "std", "min", "max", "count"])
        .sort_values("mean", ascending=False)
        .rename(columns={
            "mean": "promedio", "median": "mediana", "std": "desv_std",
            "min": "mínimo", "max": "máximo", "count": "n",
        })
    )
    st.dataframe(resumen, use_container_width=True)

    st.subheader("Matriz de correlación")
    corr = df_filtrado[variables_num].corr(numeric_only=True)
    fig_corr = px.imshow(
        corr, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
        title="Correlación entre variables numéricas",
    )
    st.plotly_chart(fig_corr, use_container_width=True)

# ----------------------------------------------------------------------------
# Tab: Análisis cualitativo
# ----------------------------------------------------------------------------
with tab_cual:
    st.subheader("Frecuencias por variable categórica")
    variables_cat = ["deporte", "pais", "continente", "genero", "medalla", "prueba"]
    var_cat = st.selectbox("Variable categórica", variables_cat, index=0)

    frecuencia = df_filtrado[var_cat].value_counts().reset_index()
    frecuencia.columns = [var_cat, "frecuencia"]
    frecuencia["porcentaje"] = (frecuencia["frecuencia"] / frecuencia["frecuencia"].sum() * 100).round(2)
    st.dataframe(frecuencia, use_container_width=True)

    st.subheader("Tabla cruzada (composición cualitativa)")
    col_c, col_d = st.columns(2)
    with col_c:
        var_fila = st.selectbox("Variable fila", variables_cat, index=0, key="fila")
    with col_d:
        var_col = st.selectbox("Variable columna", variables_cat, index=4, key="col")

    if var_fila == var_col:
        st.info("Selecciona dos variables diferentes para la tabla cruzada.")
    else:
        tabla_cruzada = pd.crosstab(df_filtrado[var_fila], df_filtrado[var_col])
        st.dataframe(tabla_cruzada, use_container_width=True)

        tabla_pct = pd.crosstab(df_filtrado[var_fila], df_filtrado[var_col], normalize="index") * 100
        st.caption("Porcentaje por fila (%)")
        st.dataframe(tabla_pct.round(1), use_container_width=True)

# ----------------------------------------------------------------------------
# Tab: Gráficos interactivos
# ----------------------------------------------------------------------------
with tab_graf:
    st.subheader("Explorador visual interactivo")

    tipo_grafico = st.selectbox(
        "Tipo de gráfico",
        ["Barras", "Dispersión (scatter)", "Histograma", "Caja (boxplot)",
         "Violin", "Sunburst jerárquico", "Radar por deporte"],
    )

    if tipo_grafico == "Barras":
        var_cat = st.selectbox("Categoría (eje X)", variables_cat, index=0, key="bar_x")
        var_num = st.selectbox("Valor a agregar (eje Y)", variables_num, index=1, key="bar_y")
        agg_fn = st.radio("Agregación", ["promedio", "suma", "conteo"], horizontal=True)
        if agg_fn == "promedio":
            data_bar = df_filtrado.groupby(var_cat)[var_num].mean().reset_index()
        elif agg_fn == "suma":
            data_bar = df_filtrado.groupby(var_cat)[var_num].sum().reset_index()
        else:
            data_bar = df_filtrado.groupby(var_cat)[var_num].count().reset_index()
        fig = px.bar(
            data_bar.sort_values(var_num, ascending=False), x=var_cat, y=var_num,
            color=var_cat, title=f"{agg_fn.capitalize()} de {var_num} por {var_cat}",
        )
        st.plotly_chart(fig, use_container_width=True)

    elif tipo_grafico == "Dispersión (scatter)":
        col_e, col_f, col_g = st.columns(3)
        with col_e:
            x_var = st.selectbox("Eje X", variables_num, index=0)
        with col_f:
            y_var = st.selectbox("Eje Y", variables_num, index=1)
        with col_g:
            color_var = st.selectbox("Color por", variables_cat, index=0, key="scatter_color")
        fig = px.scatter(
            df_filtrado, x=x_var, y=y_var, color=color_var,
            hover_data=["atleta", "pais", "deporte", "medalla"],
            title=f"{y_var} vs. {x_var}",
        )
        st.plotly_chart(fig, use_container_width=True)

    elif tipo_grafico == "Histograma":
        var_num = st.selectbox("Variable numérica", variables_num, index=1, key="hist_var")
        color_var = st.selectbox("Color por", [None] + variables_cat, index=0, key="hist_color")
        fig = px.histogram(
            df_filtrado, x=var_num, color=color_var, nbins=30, marginal="box",
            title=f"Distribución de {var_num}",
        )
        st.plotly_chart(fig, use_container_width=True)

    elif tipo_grafico == "Caja (boxplot)":
        var_cat = st.selectbox("Categoría (eje X)", variables_cat, index=0, key="box_x")
        var_num = st.selectbox("Variable numérica (eje Y)", variables_num, index=1, key="box_y")
        fig = px.box(
            df_filtrado, x=var_cat, y=var_num, color=var_cat, points="outliers",
            title=f"Distribución de {var_num} por {var_cat}",
        )
        st.plotly_chart(fig, use_container_width=True)

    elif tipo_grafico == "Violin":
        var_cat = st.selectbox("Categoría (eje X)", variables_cat, index=0, key="violin_x")
        var_num = st.selectbox("Variable numérica (eje Y)", variables_num, index=1, key="violin_y")
        fig = px.violin(
            df_filtrado, x=var_cat, y=var_num, color=var_cat, box=True, points="all",
            title=f"Distribución (violin) de {var_num} por {var_cat}",
        )
        st.plotly_chart(fig, use_container_width=True)

    elif tipo_grafico == "Sunburst jerárquico":
        fig = px.sunburst(
            df_filtrado, path=["continente", "pais", "deporte", "medalla"],
            title="Composición jerárquica: continente → país → deporte → medalla",
        )
        st.plotly_chart(fig, use_container_width=True)

    elif tipo_grafico == "Radar por deporte":
        radar_vars = ["edad", "puntaje_desempeno", "horas_entrenamiento_semana", "altura_cm", "anios_experiencia"]
        promedio_por_deporte = df_filtrado.groupby("deporte")[radar_vars].mean()
        norm = (promedio_por_deporte - promedio_por_deporte.min()) / (
            promedio_por_deporte.max() - promedio_por_deporte.min()
        )
        fig = go.Figure()
        for deporte in norm.index:
            fig.add_trace(go.Scatterpolar(
                r=norm.loc[deporte].values, theta=radar_vars, fill="toself", name=deporte,
            ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            title="Perfil normalizado por deporte (0-1)", showlegend=True,
        )
        st.plotly_chart(fig, use_container_width=True)

st.divider()
st.caption("Los datos son generados aleatoriamente y no representan competencias, atletas ni resultados reales.")
