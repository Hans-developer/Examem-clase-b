import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Examen Clase B", layout="centered")

# Función para inicializar la BD desde el CSV
def init_db():
    conn = sqlite3.connect('test_clase_b.db')
    # Leer el CSV grande
    df = pd.read_csv('preguntas.csv')
    df.to_sql('preguntas', conn, if_exists='replace', index=False)
    conn.close()

# Obtener 35 preguntas únicas de la BD
def get_test_unico():
    conn = sqlite3.connect('test_clase_b.db')
    # SELECT * FROM preguntas ORDER BY RANDOM() LIMIT 35 es más eficiente que cargar todo el CSV
    query = "SELECT * FROM preguntas ORDER BY RANDOM() LIMIT 35"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

st.title("🎓 Simulador Examen Clase B")

if 'iniciado' not in st.session_state:
    st.write(f"Banco de preguntas cargado. Presiona para generar tu examen aleatorio.")
    if st.button("Iniciar Nuevo Examen"):
        init_db()
        st.session_state.iniciado = True
        st.session_state.preguntas = get_test_unico()
        st.session_state.respuestas = {}
        st.rerun()
else:
    for i, row in st.session_state.preguntas.iterrows():
        st.markdown(f"**{i+1}. {row['pregunta']}**")
        opciones = [row['opcion_1'], row['opcion_2'], row['opcion_3']]
        resp = st.radio("Selecciona:", opciones, key=f"q_{i}", index=None, label_visibility="collapsed")
        st.session_state.respuestas[i] = resp
        st.write("---")

    if st.button("Finalizar Examen"):
        correctas = 0
        errores = []
        
        for i, row in st.session_state.preguntas.iterrows():
            idx_correcta = int(row['correcta']) - 1 
            opciones = [row['opcion_1'], row['opcion_2'], row['opcion_3']]
            correcta_texto = opciones[idx_correcta]
            
            if st.session_state.respuestas[i] == correcta_texto:
                correctas += 1
            else:
                errores.append({'p': row['pregunta'], 'r': st.session_state.respuestas[i], 'c': correcta_texto, 'e': row['explicacion']})

        st.divider()
        if correctas >= 33:
            st.success(f"### ¡APROBADO! 🎉 Puntaje: {correctas}/35")
        else:
            st.error(f"### REPROBADO ❌ Puntaje: {correctas}/35")

        if errores:
            st.subheader("💡 Feedback de errores")
            for e in errores:
                st.warning(f"**Pregunta:** {e['p']}\n\n❌ Marcaste: {e['r']}\n✅ Correcta: {e['c']}\n📖 *{e['e']}*")
        
        if st.button("Volver a intentar"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
