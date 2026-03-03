import streamlit as st 
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Simulasi Sistem Pompa Air", layout="wide")

st.sidebar.title("Parameter Sistem")

radius = st.sidebar.slider("Radius Tangki (m)", 0.5, 3.0, 1.5)
h_max = st.sidebar.slider("Tinggi Maksimum (m)", 1.0, 6.0, 4.0)
h_awal = st.sidebar.slider("Tinggi Awal (m)", 0.0, h_max, 2.0)

diameter_outlet = st.sidebar.slider("Diameter Outlet (m)", 0.05, 0.5, 0.15)
debit_pompa = st.sidebar.slider("Debit Pompa (m3/s)", 0.001, 0.05, 0.02)

pump_on_level = st.sidebar.slider("Pompa ON (%)", 0, 100, 40)
pump_off_level = st.sidebar.slider("Pompa OFF (%)", 0, 100, 90)

hari_simulasi = st.sidebar.slider("Hari Simulasi", 1, 7, 2)

jumlah_penghuni = st.sidebar.slider("Jumlah Penghuni", 1, 500, 300)
konsumsi_liter = st.sidebar.slider("Konsumsi (liter/orang/hari)", 50, 300, 150)

A = np.pi * radius**2
volume_max = A * h_max

konsumsi_m3_per_hari = (jumlah_penghuni * konsumsi_liter) / 1000
konsumsi_m3_per_detik = konsumsi_m3_per_hari / (24 * 3600)

# Parameter waktu
dt = 60  # 1 menit
total_detik = hari_simulasi * 24 * 3600
steps = int(total_detik / dt)


tinggi_air = []
status_pompa = []
waktu = []

h = h_awal
pompa_on = False

for step in range(steps):
    t = step * dt / 3600  # dalam jam
    
    level_persen = (h / h_max) * 100
    
    # Logika otomatis pompa
    if level_persen <= pump_on_level:
        pompa_on = True
    if level_persen >= pump_off_level:
        pompa_on = False
    
    debit_masuk = debit_pompa if pompa_on else 0
    debit_keluar = konsumsi_m3_per_detik
    
    dh = (debit_masuk - debit_keluar) / A
    h += dh * dt
    
    # Batas fisik
    if h > h_max:
        h = h_max
    if h < 0:
        h = 0
    
    tinggi_air.append(h)
    status_pompa.append(1 if pompa_on else 0)
    waktu.append(t)


min_tinggi = min(tinggi_air)
max_tinggi = max(tinggi_air)
jam_pompa = sum(status_pompa) * dt / 3600
biaya_listrik = jam_pompa * 1500  # asumsi Rp 1500 per jam

st.title("📊 Dashboard Simulasi Sistem Pompa Air")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Minimum Tinggi (m)", round(min_tinggi, 2))
col2.metric("Maximum Tinggi (m)", round(max_tinggi, 2))
col3.metric("Pompa Aktif (jam)", round(jam_pompa, 2))
col4.metric("Estimasi Biaya (Rp)", f"{int(biaya_listrik):,}")

st.divider()


fig1 = go.Figure()

fig1.add_trace(go.Scatter(
    x=waktu,
    y=tinggi_air,
    mode='lines',
    line=dict(width=4),
    fill='tozeroy',
    name='Tinggi Air'
))

fig1.add_hline(
    y=h_max * pump_on_level / 100,
    line_dash="dash",
    annotation_text="Pompa ON"
)

fig1.add_hline(
    y=h_max * pump_off_level / 100,
    line_dash="dash",
    annotation_text="Pompa OFF"
)

fig1.update_layout(
    title="Grafik Tinggi Air terhadap Waktu",
    xaxis_title="Jam",
    yaxis_title="Tinggi Air (m)",
    template="plotly_dark",
    height=500
)

fig1.update_yaxes(range=[min(tinggi_air)*0.9, max(tinggi_air)*1.1])

st.plotly_chart(fig1, use_container_width=True)


fig2 = go.Figure()

fig2.add_trace(go.Scatter(
    x=waktu,
    y=status_pompa,
    mode='lines',
    line=dict(width=3),
    name="Status Pompa (1=ON)"
))

fig2.update_layout(
    title="Status Pompa",
    xaxis_title="Jam",
    yaxis_title="ON / OFF",
    template="plotly_dark",
    height=300
)

st.plotly_chart(fig2, use_container_width=True)

#ooooooooooo