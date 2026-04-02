"""
SkiRent Manager — Gestión de Stock para Rental de Ropa de Nieve
Deploy: Streamlit Community Cloud + Supabase
Ejecutar localmente: streamlit run app.py
"""

import pandas as pd
import streamlit as st
from datetime import datetime
from supabase import create_client

# ─────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SkiRent Manager",
    page_icon="🎿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# ESTILOS CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
  .stApp { background: linear-gradient(135deg, #0d1b2a 0%, #1b2d45 50%, #0d1b2a 100%); }
  [data-testid="stSidebar"] {
      background: linear-gradient(180deg, #0a1628 0%, #142240 100%);
      border-right: 1px solid rgba(100,180,255,0.15);
  }
  [data-testid="stSidebar"] * { color: #cfe4ff !important; }
  .main-title {
      font-family: 'Syne', sans-serif; font-size: 2.6rem; font-weight: 800;
      background: linear-gradient(90deg, #64b8ff, #a8d8ff, #ffffff);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      letter-spacing: -0.5px; margin-bottom: 0.1rem;
  }
  .subtitle { color: #7baed6; font-size: 0.95rem; font-weight: 300; letter-spacing: 0.5px; margin-bottom: 1.5rem; }
  .metric-card {
      background: rgba(255,255,255,0.04); border: 1px solid rgba(100,180,255,0.18);
      border-radius: 14px; padding: 1.2rem 1.4rem; backdrop-filter: blur(10px);
  }
  .metric-label { font-size: 0.78rem; font-weight: 500; letter-spacing: 1.2px; text-transform: uppercase; color: #7baed6; margin-bottom: 0.35rem; }
  .metric-value { font-family: 'Syne', sans-serif; font-size: 2.2rem; font-weight: 700; color: #ffffff; line-height: 1; }
  .metric-delta { font-size: 0.8rem; margin-top: 0.3rem; }
  .delta-green { color: #4ade80; } .delta-amber { color: #fbbf24; } .delta-red { color: #f87171; }
  .section-header {
      font-family: 'Syne', sans-serif; font-size: 1.25rem; font-weight: 700;
      color: #cfe4ff; border-left: 4px solid #64b8ff; padding-left: 0.75rem; margin: 1.2rem 0 0.8rem 0;
  }
  [data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
  hr { border-color: rgba(100,180,255,0.12); }
  .stButton > button {
      background: linear-gradient(135deg, #1e4d8c, #2d6cbf); color: white;
      border: none; border-radius: 9px; font-family: 'DM Sans', sans-serif;
      font-weight: 500; padding: 0.55rem 1.4rem; transition: all 0.2s;
  }
  .stButton > button:hover {
      background: linear-gradient(135deg, #2d6cbf, #3d84e0);
      transform: translateY(-1px); box-shadow: 0 4px 16px rgba(45,108,191,0.4);
  }
  .stSelectbox > div > div, .stTextInput > div > div > input, .stNumberInput > div > div > input {
      background: rgba(255,255,255,0.06) !important;
      border: 1px solid rgba(100,180,255,0.2) !important;
      color: #cfe4ff !important; border-radius: 8px !important;
  }
  .stTabs [data-baseweb="tab-list"] { background: rgba(255,255,255,0.03); border-radius: 10px; padding: 4px; gap: 4px; }
  .stTabs [data-baseweb="tab"] { border-radius: 8px; color: #7baed6; font-family: 'DM Sans', sans-serif; }
  .stTabs [aria-selected="true"] { background: rgba(100,184,255,0.18) !important; color: #cfe4ff !important; }
  .stRadio > div { gap: 0.6rem; }
  .cat-chip {
      display: inline-block; background: rgba(100,184,255,0.12);
      border: 1px solid rgba(100,184,255,0.3); border-radius: 20px;
      padding: 4px 14px; margin: 4px; color: #a8d8ff; font-size: 0.85rem;
  }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# CLIENTE SUPABASE (cacheado)
# ─────────────────────────────────────────────
@st.cache_resource
def get_supabase():
    url = st.secrets["https://baxtffiwfipskxmqhkyc.supabase.co"]
    key = st.secrets["sb_publishable_itppg0w2fgMp1NUdHplPVw_cix4qA5seyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJheHRmZml3Zmlwc2t4bXFoa3ljIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzUxNDc0MDksImV4cCI6MjA5MDcyMzQwOX0.bVdKLQU3cwh4RYV3PMjI0BUayem4HvraBiAITQftSZI"]
    return create_client(url, key)


# ─────────────────────────────────────────────
# CAPA DE DATOS — OFICINAS
# ─────────────────────────────────────────────
def get_oficinas() -> pd.DataFrame:
    sb = get_supabase()
    res = sb.table("oficinas").select("id, nombre, ciudad").order("nombre").execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame(columns=["id", "nombre", "ciudad"])


def agregar_oficina(nombre: str, ciudad: str):
    sb = get_supabase()
    existing = sb.table("oficinas").select("id").eq("nombre", nombre).execute()
    if existing.data:
        return False, "Ya existe una oficina con ese nombre."
    sb.table("oficinas").insert({"nombre": nombre, "ciudad": ciudad}).execute()
    return True, f"Oficina '{nombre}' agregada."


# ─────────────────────────────────────────────
# CAPA DE DATOS — CATEGORÍAS
# ─────────────────────────────────────────────
def get_categorias() -> list[str]:
    sb = get_supabase()
    res = sb.table("categorias").select("nombre").order("nombre").execute()
    return [r["nombre"] for r in res.data] if res.data else []


def agregar_categoria(nombre: str):
    sb = get_supabase()
    nombre = nombre.strip().capitalize()
    existing = sb.table("categorias").select("id").eq("nombre", nombre).execute()
    if existing.data:
        return False, f"La categoría '{nombre}' ya existe."
    sb.table("categorias").insert({"nombre": nombre}).execute()
    return True, f"Categoría '{nombre}' creada y disponible en el stock."


def eliminar_categoria(nombre: str):
    sb = get_supabase()
    # Verificar si hay ítems con esa categoría
    items = sb.table("inventario").select("id").eq("categoria", nombre).execute()
    if items.data:
        return False, f"No se puede eliminar: hay {len(items.data)} ítem(s) con esta categoría."
    sb.table("categorias").delete().eq("nombre", nombre).execute()
    return True, f"Categoría '{nombre}' eliminada."


# ─────────────────────────────────────────────
# CAPA DE DATOS — INVENTARIO
# ─────────────────────────────────────────────
def get_inventario(oficina_id=None, categoria=None, estado=None) -> pd.DataFrame:
    sb = get_supabase()
    q = sb.table("inventario").select(
        "id, categoria, talle, color, oficina_actual, estado, fecha_registro, oficinas(nombre)"
    )
    if oficina_id:
        q = q.eq("oficina_actual", oficina_id)
    if categoria:
        q = q.eq("categoria", categoria)
    if estado:
        q = q.eq("estado", estado)
    res = q.order("categoria").execute()

    if not res.data:
        return pd.DataFrame(columns=["ID", "Categoria", "Talle", "Color", "Oficina", "Estado", "Fecha_Registro"])

    rows = []
    for r in res.data:
        rows.append({
            "ID":             r["id"],
            "Categoria":      r["categoria"],
            "Talle":          r["talle"],
            "Color":          r["color"],
            "Oficina":        r["oficinas"]["nombre"] if r.get("oficinas") else "—",
            "Estado":         r["estado"],
            "Fecha_Registro": r["fecha_registro"],
        })
    return pd.DataFrame(rows)


def agregar_item(categoria: str, talle: str, color: str, oficina_id: int) -> int:
    sb = get_supabase()
    res = sb.table("inventario").insert({
        "categoria":      categoria,
        "talle":          talle.upper(),
        "color":          color.capitalize(),
        "oficina_actual": oficina_id,
        "estado":         "Disponible",
        "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }).execute()
    return res.data[0]["id"] if res.data else None


def actualizar_estado(item_id: int, nuevo_estado: str, notas: str = ""):
    sb = get_supabase()
    item = sb.table("inventario").select("oficina_actual, estado").eq("id", item_id).single().execute()
    if not item.data:
        return False, "Ítem no encontrado."

    oficina_actual = item.data["oficina_actual"]
    sb.table("inventario").update({"estado": nuevo_estado}).eq("id", item_id).execute()

    tipo_map = {"Alquilado": "Alquiler", "Disponible": "Devolución", "Mantenimiento": "Mantenimiento"}
    sb.table("movimientos").insert({
        "item_id":      item_id,
        "tipo":         tipo_map.get(nuevo_estado, nuevo_estado),
        "oficina_orig": oficina_actual,
        "oficina_dest": oficina_actual,
        "fecha":        datetime.now().strftime("%Y-%m-%d %H:%M"),
        "notas":        notas,
    }).execute()
    return True, f"Estado actualizado a '{nuevo_estado}'."


def transferir_item(item_id: int, oficina_dest_id: int, notas: str = ""):
    sb = get_supabase()
    item = sb.table("inventario").select("oficina_actual, estado").eq("id", item_id).single().execute()
    if not item.data:
        return False, "Ítem no encontrado."

    oficina_orig = item.data["oficina_actual"]
    estado = item.data["estado"]

    if oficina_orig == oficina_dest_id:
        return False, "El ítem ya se encuentra en esa oficina."
    if estado == "Alquilado":
        return False, "No se puede transferir un ítem que está alquilado."

    sb.table("inventario").update({"oficina_actual": oficina_dest_id}).eq("id", item_id).execute()
    sb.table("movimientos").insert({
        "item_id":      item_id,
        "tipo":         "Transferencia",
        "oficina_orig": oficina_orig,
        "oficina_dest": oficina_dest_id,
        "fecha":        datetime.now().strftime("%Y-%m-%d %H:%M"),
        "notas":        notas,
    }).execute()
    return True, "Transferencia realizada con éxito."


# ─────────────────────────────────────────────
# CAPA DE DATOS — MÉTRICAS
# ─────────────────────────────────────────────
def get_metricas():
    sb = get_supabase()
    total   = len(sb.table("inventario").select("id").execute().data or [])
    disp    = len(sb.table("inventario").select("id").eq("estado", "Disponible").execute().data or [])
    alq     = len(sb.table("inventario").select("id").eq("estado", "Alquilado").execute().data or [])
    mant    = len(sb.table("inventario").select("id").eq("estado", "Mantenimiento").execute().data or [])
    return total, disp, alq, mant


def get_movimientos(limit: int = 30) -> pd.DataFrame:
    sb = get_supabase()
    res = sb.table("movimientos").select(
        "id, tipo, fecha, notas, item_id, "
        "inventario(categoria, talle, color), "
        "orig:oficinas!movimientos_oficina_orig_fkey(nombre), "
        "dest:oficinas!movimientos_oficina_dest_fkey(nombre)"
    ).order("fecha", desc=True).limit(limit).execute()

    if not res.data:
        return pd.DataFrame()

    rows = []
    for r in res.data:
        inv  = r.get("inventario") or {}
        orig = r.get("orig") or {}
        dest = r.get("dest") or {}
        rows.append({
            "ID":       r["id"],
            "Tipo":     r["tipo"],
            "Prenda":   f"{inv.get('categoria','')} {inv.get('talle','')} {inv.get('color','')}".strip(),
            "Origen":   orig.get("nombre", "—"),
            "Destino":  dest.get("nombre", "—"),
            "Fecha":    r["fecha"],
            "Notas":    r.get("notas", ""),
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# COMPONENTES UI
# ─────────────────────────────────────────────
def render_metric(label, value, delta_text, delta_type):
    color_class = {"green": "delta-green", "amber": "delta-amber", "red": "delta-red"}.get(delta_type, "delta-green")
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-delta {color_class}">{delta_text}</div>
    </div>
    """, unsafe_allow_html=True)


def style_estado(val):
    return {
        "Disponible":    "color: #4ade80; font-weight:600",
        "Alquilado":     "color: #fbbf24; font-weight:600",
        "Mantenimiento": "color: #f87171; font-weight:600",
    }.get(val, "")


def render_tabla(df: pd.DataFrame):
    if df.empty:
        st.info("No hay ítems que coincidan con los filtros.")
        return
    styled = df.style.applymap(style_estado, subset=["Estado"])
    st.dataframe(styled, use_container_width=True, hide_index=True)


def item_label(row) -> str:
    return f"ID {row['ID']} — {row['Categoria']} {row['Talle']} {row['Color']} ({row['Oficina']})"


# ─────────────────────────────────────────────
# PÁGINAS
# ─────────────────────────────────────────────
def page_stock():
    st.markdown('<div class="section-header">📦 Stock Total</div>', unsafe_allow_html=True)

    total, disponibles, alquilados, mant = get_metricas()
    pct_disp = round(disponibles / total * 100) if total else 0
    pct_alq  = round(alquilados  / total * 100) if total else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1: render_metric("Total Prendas",  total,       "inventario completo",      "green")
    with c2: render_metric("Disponibles",    disponibles, f"{pct_disp}% del total",   "green")
    with c3: render_metric("Alquiladas",     alquilados,  f"{pct_alq}% del total",    "amber")
    with c4: render_metric("Mantenimiento",  mant,        "fuera de servicio",        "red")

    st.markdown("---")

    oficinas_df  = get_oficinas()
    categorias   = get_categorias()
    ofi_opts     = {"Todas": None} | dict(zip(oficinas_df["nombre"], oficinas_df["id"]))
    cat_opts     = ["Todas"] + categorias
    est_opts     = ["Todos", "Disponible", "Alquilado", "Mantenimiento"]

    col1, col2, col3 = st.columns(3)
    with col1: ofi_sel = st.selectbox("🏔️ Oficina",    list(ofi_opts.keys()))
    with col2: cat_sel = st.selectbox("🧥 Categoría",  cat_opts)
    with col3: est_sel = st.selectbox("📌 Estado",     est_opts)

    inv = get_inventario(
        oficina_id = ofi_opts[ofi_sel],
        categoria  = None if cat_sel == "Todas" else cat_sel,
        estado     = None if est_sel == "Todos"  else est_sel,
    )

    st.markdown(f'<div class="section-header">🗂️ Inventario ({len(inv)} ítems)</div>', unsafe_allow_html=True)
    render_tabla(inv)

    if not inv.empty:
        st.markdown('<div class="section-header">📊 Resumen por Categoría</div>', unsafe_allow_html=True)
        resumen = inv.groupby(["Categoria", "Estado"]).size().unstack(fill_value=0).reset_index()
        st.dataframe(resumen, use_container_width=True, hide_index=True)

    with st.expander("📋 Últimos 30 movimientos"):
        mov = get_movimientos(30)
        if mov.empty:
            st.info("Sin movimientos registrados aún.")
        else:
            st.dataframe(mov, use_container_width=True, hide_index=True)


def page_alquiler():
    st.markdown('<div class="section-header">🔄 Registrar Alquiler / Devolución</div>', unsafe_allow_html=True)
    tab_alq, tab_dev = st.tabs(["🛷  Registrar Alquiler", "✅  Registrar Devolución"])

    with tab_alq:
        categorias  = ["Todas"] + get_categorias()
        oficinas_df = get_oficinas()
        ofi_opts    = {"Todas": None} | dict(zip(oficinas_df["nombre"], oficinas_df["id"]))

        col1, col2 = st.columns(2)
        with col1: cat_f = st.selectbox("Filtrar categoría", categorias, key="alq_cat")
        with col2: ofi_f = st.selectbox("Filtrar oficina",   list(ofi_opts.keys()), key="alq_ofi")

        disponibles = get_inventario(
            oficina_id = ofi_opts[ofi_f],
            categoria  = None if cat_f == "Todas" else cat_f,
            estado     = "Disponible",
        )

        if disponibles.empty:
            st.warning("No hay ítems disponibles con esos filtros.")
        else:
            render_tabla(disponibles)
            labels = disponibles.apply(item_label, axis=1).tolist()
            sel    = st.selectbox("Seleccionar ítem", labels, key="alq_item")
            sel_id = int(disponibles.iloc[labels.index(sel)]["ID"])
            notas  = st.text_input("Notas (cliente, fecha estimada de devolución…)", key="alq_notas")
            if st.button("🛷 Confirmar Alquiler"):
                ok, msg = actualizar_estado(sel_id, "Alquilado", notas)
                st.success(f"✅ {msg}") if ok else st.error(f"❌ {msg}")
                if ok: st.rerun()

    with tab_dev:
        alquilados = get_inventario(estado="Alquilado")
        if alquilados.empty:
            st.info("No hay ítems alquilados actualmente.")
        else:
            render_tabla(alquilados)
            labels = alquilados.apply(item_label, axis=1).tolist()
            sel    = st.selectbox("Seleccionar ítem a devolver", labels, key="dev_item")
            sel_id = int(alquilados.iloc[labels.index(sel)]["ID"])
            nuevo  = st.radio("Estado tras la devolución:", ["Disponible", "Mantenimiento"], horizontal=True)
            notas  = st.text_input("Notas de devolución", key="dev_notas")
            if st.button("✅ Confirmar Devolución"):
                ok, msg = actualizar_estado(sel_id, nuevo, notas)
                st.success(f"✅ {msg}") if ok else st.error(f"❌ {msg}")
                if ok: st.rerun()


def page_transferir():
    st.markdown('<div class="section-header">🚀 Transferir entre Oficinas</div>', unsafe_allow_html=True)

    oficinas_df = get_oficinas()
    if oficinas_df.shape[0] < 2:
        st.warning("Necesitás al menos 2 oficinas registradas.")
        return

    ofi_map = dict(zip(oficinas_df["nombre"], oficinas_df["id"]))
    col1, col2 = st.columns(2)
    with col1: orig = st.selectbox("🏔️ Origen",  list(ofi_map.keys()), key="t_orig")
    with col2:
        destinos = [o for o in ofi_map if o != orig]
        dest     = st.selectbox("🏔️ Destino", destinos, key="t_dest")

    transferibles = get_inventario(oficina_id=ofi_map[orig])
    transferibles = transferibles[transferibles["Estado"] != "Alquilado"]

    st.markdown(f"**Ítems transferibles en {orig}:** {len(transferibles)}")
    render_tabla(transferibles)

    if not transferibles.empty:
        labels = transferibles.apply(item_label, axis=1).tolist()
        sel    = st.selectbox("Seleccionar ítem", labels, key="t_item")
        sel_id = int(transferibles.iloc[labels.index(sel)]["ID"])
        notas  = st.text_input("Notas", key="t_notas")
        if st.button("🚀 Confirmar Transferencia"):
            ok, msg = transferir_item(sel_id, ofi_map[dest], notas)
            st.success(f"✅ {msg}  {orig} → {dest}") if ok else st.error(f"❌ {msg}")
            if ok: st.rerun()


def page_agregar():
    st.markdown('<div class="section-header">➕ Agregar Ítems, Categorías y Oficinas</div>', unsafe_allow_html=True)
    tab_item, tab_cat, tab_ofi = st.tabs(["🧥  Nuevo Ítem", "🏷️  Gestionar Categorías", "🏔️  Nueva Oficina"])

    # ── TAB NUEVO ÍTEM ──────────────────────────────────────────
    with tab_item:
        categorias  = get_categorias()
        oficinas_df = get_oficinas()

        if not categorias:
            st.warning("⚠️ Primero creá al menos una categoría en la pestaña **Gestionar Categorías**.")
        elif oficinas_df.empty:
            st.warning("⚠️ No hay oficinas registradas.")
        else:
            ofi_map = dict(zip(oficinas_df["nombre"], oficinas_df["id"]))
            c1, c2 = st.columns(2)
            with c1:
                cat   = st.selectbox("Categoría", categorias)
                talle = st.text_input("Talle", placeholder="S / M / L / XL / 40 / 42…")
            with c2:
                color   = st.text_input("Color", placeholder="Azul, Negro, Rojo…")
                ofi_sel = st.selectbox("Oficina", list(ofi_map.keys()))

            if st.button("➕ Agregar Ítem"):
                if not talle.strip() or not color.strip():
                    st.error("Completá el talle y el color.")
                else:
                    item_id = agregar_item(cat, talle.strip(), color.strip(), ofi_map[ofi_sel])
                    st.success(f"✅ Ítem #{item_id} agregado — {cat} {talle.upper()} {color.capitalize()} en {ofi_sel}.")
                    st.rerun()

    # ── TAB CATEGORÍAS ──────────────────────────────────────────
    with tab_cat:
        st.markdown("**Categorías activas:**")
        categorias = get_categorias()

        if categorias:
            chips_html = "".join(f'<span class="cat-chip">🏷️ {c}</span>' for c in categorias)
            st.markdown(chips_html, unsafe_allow_html=True)
        else:
            st.info("Aún no hay categorías. ¡Creá la primera!")

        st.markdown("---")
        col_a, col_b = st.columns([3, 1])
        with col_a:
            nueva_cat = st.text_input("Nombre de la nueva categoría", placeholder="Ej: Guantes, Casco, Gafas…", key="new_cat")
        with col_b:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ Crear Categoría"):
                if not nueva_cat.strip():
                    st.error("Escribí un nombre.")
                else:
                    ok, msg = agregar_categoria(nueva_cat)
                    st.success(f"✅ {msg}") if ok else st.error(f"❌ {msg}")
                    if ok: st.rerun()

        if categorias:
            st.markdown("---")
            st.markdown("**Eliminar categoría** *(solo si no tiene ítems asociados)*")
            cat_del = st.selectbox("Seleccionar categoría a eliminar", categorias, key="del_cat")
            if st.button("🗑️ Eliminar Categoría", key="btn_del_cat"):
                ok, msg = eliminar_categoria(cat_del)
                st.success(f"✅ {msg}") if ok else st.error(f"❌ {msg}")
                if ok: st.rerun()

    # ── TAB OFICINAS ────────────────────────────────────────────
    with tab_ofi:
        col_a, col_b = st.columns(2)
        with col_a: new_nombre = st.text_input("Nombre de la oficina", placeholder="Ej: Rios Andinos Centro")
        with col_b: new_ciudad = st.text_input("Ciudad",               placeholder="Ej: Mendoza")

        if st.button("🏔️ Agregar Oficina"):
            if not new_nombre.strip() or not new_ciudad.strip():
                st.error("Completá nombre y ciudad.")
            else:
                ok, msg = agregar_oficina(new_nombre.strip(), new_ciudad.strip())
                st.success(f"✅ {msg}") if ok else st.error(f"❌ {msg}")
                if ok: st.rerun()

        st.markdown("---")
        st.markdown("**Oficinas registradas:**")
        st.dataframe(get_oficinas().rename(columns={"id": "ID", "nombre": "Nombre", "ciudad": "Ciudad"}),
                     use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────
# SIDEBAR + MAIN
# ─────────────────────────────────────────────
def main():
    st.markdown('<div class="main-title">🎿 SkiRent Manager</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Sistema de Gestión de Stock · Rios Andinos</div>', unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### 🎿 SkiRent Manager")
        st.markdown("##### Rios Andinos")
        st.markdown("---")

        menu_options = {
            "📦 Ver Stock Total":           "stock",
            "🔄 Alquiler / Devolución":     "alquiler",
            "🚀 Transferir entre Oficinas": "transferir",
            "➕ Agregar / Gestionar":       "agregar",
        }
        seleccion = st.radio("Menú principal", list(menu_options.keys()), label_visibility="collapsed")

        st.markdown("---")
        try:
            total, disp, alq, mant = get_metricas()
            st.markdown(f"**Total prendas:** {total}")
            st.markdown(f"🟢 Disponibles: **{disp}**")
            st.markdown(f"🟡 Alquiladas: **{alq}**")
            st.markdown(f"🔴 Mantenimiento: **{mant}**")
        except Exception:
            st.warning("Sin conexión a la base de datos.")
        st.markdown("---")
        st.caption(f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    pagina = menu_options[seleccion]
    if   pagina == "stock":      page_stock()
    elif pagina == "alquiler":   page_alquiler()
    elif pagina == "transferir": page_transferir()
    elif pagina == "agregar":    page_agregar()


if __name__ == "__main__":
    main()