import streamlit as st
from pmax_back import Pmax
from conexao import conexaoBD
from time import sleep

st.set_page_config("Gestão de Ponto", layout="wide")

html = """<div class="cabecalho">
        <div class="titulo">
            <img src="https://github.com/RahyanRamos/Imagens.Eucatur/blob/main/logo-pontoMax.png?raw=true" alt="Logo de escrita EscalaMAX">
            <!-- <p>EscalaMAX</p> -->
        </div>
    </div>"""

css = """@import url('https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,300..800;1,300..800&display=swap');

    p{
        font-family: "Open Sans", sans-serif;
    }

    .cabecalho{
        margin: 0;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 60px;
        display: flex;
        justify-content: center;
        align-items: center;
        background-position: center;
        z-index: 999990;
        background-color: #34495e;
        box-shadow: 0 6px 10px rgba(0, 0, 0, 0.3);
    }

    .cabecalho .logo{
        position: absolute;
        left: 0px;
        background-color: #9dacbb;
        padding-right: 40px;
        margin: 0;
        height: 100%;
    }

    .cabecalho .logo img{
        height: 50px;
    }

    .cabecalho .titulo{
        position: relative;
        z-index: 2;
        color: #000;
        text-align: center;
        //background-color: #9dacbb;
        padding: 0 8px;
        border-radius: 4px;
    }

    .cabecalho .titulo img{
        height: 40px;
    }

    .cabecalho .titulo p{
        margin: 3px;
        font-family: "Open Sans", sans-serif;
        font-size: 14px;
        font-weight: bold;
    }

    [data-testid="collapsedControl"]{
        z-index: 999991;
        height: 60px;
        width: 90px;
        left: 45px;
        top: 0;
        padding: 5px;
    }
    
    [data-testid="collapsedControl"] img{
        width: 35px;
        height: 35px;
    }

    [data-testid="stSidebar"][aria-expanded="true"] img{
        width: 120px;
        height: 35px;
    }
    
    [data-testid="collapsedControl"] svg,
    [data-testid="stSidebar"][aria-expanded="true"] svg{
        height: 30px;
        width: 30px;
        margin: 5px 0;
    }"""
st.write(f"<div>{html}</div>", unsafe_allow_html=True)
st.write(f"<style>{css}</style>", unsafe_allow_html=True)



ponto_max = Pmax()

@st.cache_data(ttl=60)
def get_itinerarios():
    dados_itinerarios = ponto_max.get_itinerarios()

    opc_itinerarios = ponto_max.set_itirarios(dados_itinerarios)

    return opc_itinerarios


@st.cache_data(ttl=60)
def get_jornada():
    dados_jornada_aux = ponto_max.get_jornadas(255)

    dados_jornada = ponto_max.set_jornadas(dados_jornada_aux)

    return dados_jornada


def limpa_insert(insert_str):
    return str(insert_str).replace('"', "'")


@st.cache_data(ttl=60)
def get_jornadas_disponiveis(fgkey_motorist):
    ponto_max = Pmax()

    jornadas_motorista = ponto_max.get_jornadas_motorista(fgkey_motorist)

    registros_pontos = ponto_max.get_registros_pontos()

    opc_jornadas = ponto_max.set_jornadas_opc(jornadas_motorista, registros_pontos)

    return opc_jornadas


@st.cache_data(ttl=60)
def get_typeregistros():
    ponto_max = Pmax()
    dados_typeregistros = ponto_max.get_typeregistros()

    # Criando duas listas: uma com os nomes e outra com os ids
    opc_nomes_typeregistros = [registro[1] for registro in dados_typeregistros]  # Apenas o name_registro
    opc_ids_typeregistros = [registro[0] for registro in dados_typeregistros]    # Apenas o id_registro

    return opc_nomes_typeregistros, opc_ids_typeregistros




st.title("Gestão de Ponto")

with st.expander("Criar Jornada"):
    col1, col2 = st.columns([2, 1])
    with col1:
        opc_itinerarios = get_itinerarios()
        itinerario = st.selectbox("Itinerário", opc_itinerarios)
    with col2:
        numVeiculo = st.text_input("Número do Veículo")
    

    col1, col2 = st.columns(2)
    with col1:
        Kms = st.text_input("Kms")
    with col2:
        numMapa = st.text_input("Número do Mapa")
    
    colAux, colButton = st.columns([4, 1])
    with colButton:
        salvar = st.button("Criar Jornada", use_container_width=True)

        check_campos = [len(str(x).strip()) for x in [numVeiculo, Kms, numMapa]]
        if salvar:
            if 0 not in check_campos:            
                
                try:
                    conexao = conexaoBD()
                    cursor = conexao.cursor()

                    ############# TRATANDO AS INFORMAÇÕES DO ITINERÁRIO #############
                    split_itiner = itinerario.split('.')
                    trecho = split_itiner[1].split('(')[0]
                    split_trecho_ini = str(trecho.split(' x ')[0]).strip()
                    split_trecho_fim = str(trecho.split(' x ')[1]).strip()
                    ############# FIM DO TRATAMENTO #############

                    ############# CRIANDO INSERT COM PARÂMETROS #############
                    cmd = """INSERT INTO pmax_getregistro(fgkey_servicolin, fgkey_motorist, matricula_motorist, name_city_ini, name_city_fim, num_veiculo, num_mapa, kms)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""
                    
                    parametros = (
                        str(split_itiner[0]).strip(),
                        679,
                        limpa_insert(255),
                        limpa_insert(split_trecho_ini),
                        limpa_insert(split_trecho_fim),
                        numVeiculo,
                        numMapa,
                        limpa_insert(Kms)
                    )
                    
                    cursor.execute(cmd, parametros)
                    conexao.commit()

                    st.toast('Jornada criada com sucesso!', icon='✅')
                    sleep(0.1)
                    st.rerun()
                
                except Exception as e:
                    conexao.rollback()
                    st.toast(f'Ocorreu um erro ao salvar a jornada: {str(e)}', icon='❌')
                
                finally:
                    cursor.close()
                    conexao.close()
                
            else:
                st.toast('Por favor, preencha todos os campos corretamente!', icon='❌')


tab1, tab2 = st.tabs(["Jornadas em aberto", "Jornadas finalizadas"])
with tab1:
    opc_jornadas = get_jornadas_disponiveis(fgkey_motorist=679)  # ID do motorista

    # Selectbox exibindo o campo 'itinerario' e retornando 'id_gregistro'
    if opc_jornadas:
        jornada_selecionada = st.selectbox(
            "Selecione a Jornada",
            options=[(x[1], x[0]) for x in opc_jornadas],
            format_func=lambda x: x[0],  # Exibe o itinerário
            index=0
        )
        id_gregistro_selecionado = jornada_selecionada[1]
    else:
        st.write("Nenhuma jornada disponível.")

    with st.expander("Registros de Ponto"):
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            opc_nomes_typeregistros, opc_ids_typeregistros = get_typeregistros()
            tpParada = st.selectbox("Tipo de Ponto", opc_nomes_typeregistros, index=None, placeholder="Selecione o tipo de parada")

        if tpParada:
            # Retorna o id correspondente ao nome selecionado
            idParada = opc_ids_typeregistros[opc_nomes_typeregistros.index(tpParada)]

            if idParada in [1, 2, 6, 7]:
                with col2:
                    data = st.date_input("Data")
                with col3:
                    hora = st.time_input("Hora")
            else:
                with col2:
                    dtInicio = st.date_input("Data de Início")
                with col3:
                    hrInicio = st.time_input("Hora de Início")

                col1, col2, col3 = st.columns([2, 1, 1])
                with col2:
                    dtFim = st.date_input("Data de Fim")
                with col3:
                    hrFim = st.time_input("Hora de Fim")

            colAux, col4 = st.columns([4, 1])
            with col4:
                st.write(" ")
                st.write(" ")
                registrar = st.button("Registrar", use_container_width=True)

            

            dados_jornada = [
                {
                    "itinerario": "Ji-Paraná X Porto Velho",
                    "numero_veiculo": "6421",
                    "kms": 357,
                    "numero_mapa": "53468",
                    "paradas": [
                        {
                            "nome_parada": "Entrada em Serviço",
                            "info_parada": "25/09/2024 - 11:14"
                        },
                        {
                            "nome_parada": "Início da Viagem",
                            "info_parada": "25/09/2024 - 11:20"
                        },
                        {
                            "nome_parada": "Intervalo",
                            "infos_parada": [
                                {"inicio": "25/09/2024 - 15:00", "fim": "25/09/2024 - 15:15"},
                                {"inicio": "25/09/2024 - 20:40", "fim": "25/09/2024 - 20:50"},
                                {"inicio": "26/09/2024 - 06:22", "fim": "26/09/2024 - 06:40"}
                            ]
                        },
                        {
                            "nome_parada": "Término da Viagem",
                            "info_parada": "26/09/2024 - 18:00"
                        },
                        {
                            "nome_parada": "Saída de Serviço",
                            "info_parada": "26/09/2024 - 18:10"
                        }
                    ]
                }
            ]
            
            html = f"""<div class="container-pontos">
                <div class="container-jornada">
                    <p>Itinerário: {dados_jornada[0]['itinerario']}</p>
                    <p>Nº do Veículo: {dados_jornada[0]['numero_veiculo']}</p>
                    <p>Kms: {dados_jornada[0]['kms']}</p>
                    <p>Nº do Mapa: {dados_jornada[0]['numero_mapa']}</p>
                </div>"""

            for index, parada in enumerate(dados_jornada[0]['paradas'], start=1):
                html += f"""<div class="container-tipoParada">
                    <div class="numRegistro">
                        <p>{index}</p>
                    </div>
                    <div class="nomeParada">
                        <p>{parada['nome_parada']}</p>
                    </div>
                    <div class="container-paradas">"""
                if 'info_parada' in parada:
                    html += f"""<div class="infoParada">
                            <p>{parada['info_parada']}</p>
                        </div>"""
                elif 'infos_parada' in parada:
                    for info in parada['infos_parada']:
                        html += f"""<div class="infoParada">
                            <p>Início: {info['inicio']}</p>
                            <p>Fim: {info['fim']}</p>
                        </div>"""
            
                html += """</div>
                </div>"""

            html += "</div>"


            css = """.container-pontos {
                display: flex;
                flex-direction: column;
                margin: 30px auto;
                background-color: #fff;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            }

            .container-tipoParada {
                display: flex;
                align-items: center;
                margin-bottom: 20px;
                padding: 10px;
                background-color: #e9ecef;
                border-radius: 5px;
                border-left: 5px solid #007bff;
            }

            .numRegistro {
                font-weight: bold;
                color: #007bff;
                width: 20px;
            }

            .numRegistro p{
                font-weight: bold;
                font-size: 18px;
            }

            .nomeParada {
                flex-grow: 1;
                padding-left: 15px;
            }

            .nomeParada p{
                font-weight: bold;
                color: #007bff;
            }

            .infoParada {
                display: flex;
                flex-direction: column;
                width: 100%;
                font-size: 14px;
                color: #333;
                margin: 10px 0;
            }

            .container-tipoParada .infoParada p {
                display: flex;
                margin: 2px 0;
            }

            .container-tipoParada:nth-child(odd) {
                background-color: #f8f9fa;
            }

            .container-tipoParada:nth-child(even) {
                background-color: #e9ecef;
            }
            
            .container-jornada {
                display: flex;
                flex-direction: column;
                margin-bottom: 20px;
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                border-left: 5px solid #007bff;
            }

            .container-jornada p {
                margin: 5px 0;
                font-size: 16px;
                color: #333;
            }

            .container-jornada p:first-child {
                font-weight: bold;
            }"""

            st.write(html, unsafe_allow_html=True)
            st.write(f"<style>{css}</style>", unsafe_allow_html=True)


with tab2:
    dados_jornadas = get_jornada()


    for jornada in dados_jornadas:
        with st.expander(f"Registros de Ponto: {jornada['itinerario']}"):
            html = f"""<div class='container-jornadas'>
                <div class="container-pontos">
                    <div class="container-jornada">
                        <p>Itinerário: {jornada['itinerario']}</p>
                        <p>Nº do Veículo: {jornada['numero_veiculo']}</p>
                        <p>Kms: {jornada['kms']}</p>
                        <p>Nº do Mapa: {jornada['numero_mapa']}</p>
                    </div>"""

            for index, parada in enumerate(jornada['paradas'], start=1):
                html += f"""<div class="container-tipoParada">
                    <div class="numRegistro">
                        <p>{index}</p>
                    </div>
                    <div class="nomeParada">
                        <p>{parada['nome_parada']}</p>
                    </div>
                    <div class="container-paradas">"""
                
                if 'infos_parada' in parada:
                    for info in parada['infos_parada']:

                        html += f"""<div class="infoParada">
                            <p>Início: {info['Inicio']}</p>
                            <p>Fim: {info['Fim']}</p>
                        </div>"""

                elif 'info_parada' in parada:
                    html += f"""<div class="infoParada">
                            <p>{parada['info_parada']}</p>
                        </div>"""
                
                html += """</div>
                </div>"""
            
            html += "</div>"
            html += "</div>"

            css = """.container-pontos {
                display: flex;
                flex-direction: column;
                margin: 30px auto;
                background-color: #fff;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            }

            .container-tipoParada {
                display: flex;
                align-items: center;
                margin-bottom: 20px;
                padding: 10px;
                background-color: #e9ecef;
                border-radius: 5px;
                border-left: 5px solid #007bff;
            }

            .numRegistro {
                font-weight: bold;
                color: #007bff;
                width: 20px;
            }

            .numRegistro p{
                font-weight: bold;
                font-size: 18px;
            }

            .nomeParada {
                flex-grow: 1;
                padding-left: 15px;
            }

            .nomeParada p{
                font-weight: bold;
                color: #007bff;
            }

            .infoParada {
                display: flex;
                flex-direction: column;
                width: 100%;
                font-size: 14px;
                color: #333;
                margin: 10px 0;
            }

            .container-tipoParada .infoParada p {
                display: flex;
                margin: 2px 0;
            }

            .container-tipoParada:nth-child(odd) {
                background-color: #f8f9fa;
            }

            .container-tipoParada:nth-child(even) {
                background-color: #e9ecef;
            }
            
            .container-jornada {
                display: flex;
                flex-direction: column;
                margin-bottom: 20px;
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                border-left: 5px solid #007bff;
            }

            .container-jornada p {
                margin: 5px 0;
                font-size: 16px;
                color: #333;
            }

            .container-jornada p:first-child {
                font-weight: bold;
            }"""

            st.write(html, unsafe_allow_html=True)
            st.write(f"<style>{css}</style>", unsafe_allow_html=True)
