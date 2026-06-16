import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Examen Clase B", layout="centered")

def init_db():
    conn = sqlite3.connect('test_clase_b.db')
    df = pd.read_csv('preguntas.csv')
    df.to_sql('preguntas', conn, if_exists='replace', index=False)
    conn.close()

def get_test_unico():
    conn = sqlite3.connect('test_clase_b.db')
    df_full = pd.read_sql('SELECT * FROM preguntas', conn)
    conn.close()
    return df_full.sample(n=min(35, len(df_full)), replace=False).reset_index(drop=True)

st.title("🎓 Simulador Examen Clase B")

if 'iniciado' not in st.session_state:
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
            # Mapeo: la columna 'correcta' contiene el número 1, 2 o 3
            idx_correcta = int(row['correcta']) - 1 
            opciones = [row['opcion_1'], row['opcion_2'], row['opcion_3']]
            respuesta_correcta_texto = opciones[idx_correcta]
            
            if st.session_state.respuestas[i] == respuesta_correcta_texto:
                correctas += 1
            else:
                errores.append({
                    'p': row['pregunta'], 
                    'r': st.session_state.respuestas[i], 
                    'c': respuesta_correcta_texto, 
                    'e': row['explicacion']
                })

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
