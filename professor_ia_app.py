import streamlit as st
import json
import os
from datetime import date

# Configurações da Página
st.set_page_config(page_title="Professor IA 2.0", page_icon="👨‍🏫", layout="wide")

# Estilização
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 20px; font-weight: bold; height: 3em; background-color: #1f4e79; color: white; }
    .chat-bubble-ai { background-color: #f1f8e9; padding: 15px; border-radius: 15px; margin-bottom: 10px; color: #1b5e20; border: 1px solid #c5e1a5; }
    .bonus-card { background-color: #fff9c4; padding: 10px; border-radius: 10px; text-align: center; border: 2px dashed #fbc02d; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE DADOS ---
def carregar_dados():
    if os.path.exists('dados_estudos.json'):
        with open('dados_estudos.json', 'r') as f:
            return json.load(f)
    return {}

def salvar_dados(nome, pontos, total_hoje):
    dados = carregar_dados()
    dados[nome] = {
        "pontos": pontos,
        "total_hoje": total_hoje,
        "ultima_data": str(date.today())
    }
    with open('dados_estudos.json', 'w') as f:
        json.dump(dados, f)

# --- INICIALIZAÇÃO DO ESTADO ---
if 'nome' not in st.session_state: st.session_state.nome = ""
if 'pagina' not in st.session_state: st.session_state.pagina = 'login'
if 'chat_history' not in st.session_state: st.session_state.chat_history = []
if 'materia' not in st.session_state: st.session_state.materia = None

# Dados das Matérias
materias = {
    "Português": {"cor": "#e91e63", "emoji": "📚", "pergunta": "A palavra 'CASA' é um substantivo?", "resp": "Verdadeiro"},
    "Matemática": {"cor": "#2196f3", "emoji": "📐", "pergunta": "20 + 30 é igual a 60?", "resp": "Falso"},
    "Ciências": {"cor": "#4caf50", "emoji": "🌿", "pergunta": "A Lua emite luz própria?", "resp": "Falso"},
    "História": {"cor": "#ff9800", "emoji": "🏰", "pergunta": "Pedro Álvares Cabral chegou ao Brasil em 1500?", "resp": "Verdadeiro"},
    "Geografia": {"cor": "#9c27b0", "emoji": "🌍", "pergunta": "Brasília é a capital do Brasil?", "resp": "Verdadeiro"}
}

# --- TELA DE LOGIN ---
if st.session_state.pagina == 'login':
    st.title("👨‍🏫 Bem-vindo ao Professor IA!")
    nome_input = st.text_input("Qual é o seu nome, pequeno cadete?", placeholder="Digite seu nome aqui...")
    if st.button("ENTRAR NA SALA DE AULA"):
        if nome_input:
            st.session_state.nome = nome_input.strip()
            dados = carregar_dados()
            user_data = dados.get(st.session_state.nome, {"pontos": 0, "total_hoje": 0, "ultima_data": str(date.today())})
            
            # Resetar contador se for um novo dia
            if user_data["ultima_data"] != str(date.today()):
                user_data["total_hoje"] = 0
            
            st.session_state.pontos = user_data["pontos"]
            st.session_state.total_hoje = user_data["total_hoje"]
            st.session_state.pagina = 'home'
            st.rerun()
        else:
            st.warning("Por favor, digite seu nome para começar!")

# --- TELA PRINCIPAL ---
else:
    # Barra Lateral
    with st.sidebar:
        st.header(f"Estudante: {st.session_state.nome}")
        st.metric("Pontos Totais ⭐", st.session_state.pontos)
        st.write(f"Atividades hoje: **{st.session_state.total_hoje}/20**")
        
        if st.session_state.total_hoje >= 20:
            st.markdown("<div class='bonus-card'>🔥 BÔNUS ATIVO: Pontos em Dobro!</div>", unsafe_allow_html=True)
        
        if st.button("🏠 Início"): st.session_state.pagina = 'home'; st.rerun()
        if st.button("🚪 Sair"): st.session_state.pagina = 'login'; st.rerun()

    # Lógica de Pontuação
    def ganhar_pontos(base):
        multiplicador = 2 if st.session_state.total_hoje >= 20 else 1
        st.session_state.pontos += (base * multiplicador)
        st.session_state.total_hoje += 1
        salvar_dados(st.session_state.nome, st.session_state.pontos, st.session_state.total_hoje)

    # Conteúdo
    if st.session_state.pagina == 'home':
        st.title(f"Olá, {st.session_state.nome}! 👋")
        st.subheader("Escolha sua aula de hoje:")
        cols = st.columns(len(materias))
        for i, (nome, info) in enumerate(materias.items()):
            with cols[i]:
                st.markdown(f"<div style='background:{info['cor']};padding:20px;border-radius:15px;text-align:center;color:white;font-size:40px;'>{info['emoji']}</div>", unsafe_allow_html=True)
                if st.button(nome):
                    st.session_state.materia = nome
                    st.session_state.pagina = 'aula'
                    st.rerun()

    elif st.session_state.pagina == 'aula':
        mat = st.session_state.materia
        info = materias[mat]
        st.title(f"{info['emoji']} Aula de {mat}")
        
        t1, t2 = st.tabs(["💬 Chat com o Professor", "🎮 Desafio Valendo Pontos"])
        
        with t1:
            for msg in st.session_state.chat_history:
                st.markdown(f'<div class="chat-bubble-ai"><b>{msg["role"]}:</b> {msg["content"]}</div>', unsafe_allow_html=True)
            
            duvida = st.chat_input("Tire sua dúvida aqui...")
            if duvida:
                st.session_state.chat_history.append({"role": "Você", "content": duvida})
                ganhar_pontos(5)
                st.session_state.chat_history.append({"role": "Professor", "content": f"Excelente pergunta sobre {mat}! Isso mostra que você está se esforçando!"})
                st.rerun()

        with t2:
            st.write(info['pergunta'])
            c1, c2 = st.columns(2)
            if c1.button("Verdadeiro"):
                if info['resp'] == "Verdadeiro":
                    st.balloons()
                    st.success("Acertou!")
                    ganhar_pontos(10)
                else: st.error("Incorreto!")
            if c2.button("Falso"):
                if info['resp'] == "Falso":
                    st.balloons()
                    st.success("Acertou!")
                    ganhar_pontos(10)
                else: st.error("Incorreto!")