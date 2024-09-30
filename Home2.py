import streamlit as st
from pmax_back import Pmax
from conexao import conexaoBD
from time import sleep
from datetime import datetime

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

@st.cache_data(ttl=100, show_spinner=False)
def get_itinerarios():
    dados_itinerarios = ponto_max.get_itenerarios()

    opc_itinerarios = ponto_max.set_iterarios(dados_itinerarios)

    return opc_itinerarios


@st.cache_data(ttl=100, show_spinner=False)
def get_typeregistros():    
    dados_typeregistros = ponto_max.get_typeregistros()

    # Criando duas listas: uma com os nomes e outra com os ids
    opc_nomes_typeregistros = [registro[1] for registro in dados_typeregistros]  # Apenas o name_registro
    opc_ids_typeregistros = [registro[0] for registro in dados_typeregistros]    # Apenas o id_registro

    return opc_nomes_typeregistros, opc_ids_typeregistros


@st.cache_data(ttl=100, show_spinner=False)
def get_jornadas_disponiveis(fgkey_motorist):
    # Consulta as jornadas do motorista
    jornadas_motorista = ponto_max.get_jornadas_motorista(fgkey_motorist)

    # Consulta os registros de pontos
    registros_pontos = ponto_max.get_registros_pontos()

    # Prepara as opções para o selectbox (jornadas sem número 7)
    opc_jornadas = ponto_max.set_jornadas_opc(jornadas_motorista, registros_pontos)

    return opc_jornadas


def limpa_insert(insert_str):
    return str(insert_str).replace('"', "'")


@st.cache_data(ttl=100, show_spinner=False)
def consulta_jornada():
    jornadas_aux = ponto_max.get_jornadas(255)

    jornadas = ponto_max.set_jornadas(jornadas_aux)

    return jornadas


@st.cache_data(ttl=100, show_spinner=False)
def get_jornadas_disponiveis(fgkey_motorist):
    ponto_max = Pmax()

    # Consulta as jornadas do motorista
    jornadas_motorista = ponto_max.get_jornadas_motorista(fgkey_motorist)

    # Consulta os registros de pontos
    registros_pontos = ponto_max.get_registros_pontos()

    # Prepara as opções para o selectbox (jornadas sem número 7)
    opc_jornadas = ponto_max.set_jornadas_opc(jornadas_motorista, registros_pontos)

    return opc_jornadas, registros_pontos


def definir_opcoes_parada(paradas_registradas):
    if not paradas_registradas:
        return ["Entrada em Serviço"], [1]  # ID 1 para "Entrada em Serviço"
    
    # Se "Início da Viagem" estiver registrado
    if 1 in paradas_registradas:
        # Se "Término da Viagem" ainda não foi registrado, ofereça as opções
        if 2 in paradas_registradas and 6 not in paradas_registradas:
            return ["Intervalo", "Tempo de espera", "Repouso no Veículo", "Término da Viagem"], [3, 4, 5, 6]
        
        # Se "Término da Viagem" foi selecionado, ofereça apenas "Saída de Serviço"
        if 6 in paradas_registradas:
            return ["Saída de Serviço"], [7]

    # Se "Entrada em Serviço" está registrado e "Início da Viagem" ainda não
    if 1 in paradas_registradas and 2 not in paradas_registradas:
        return ["Início da Viagem"], [2]  # ID 2 para "Início da Viagem"

    # Se "Término da Viagem" foi registrado, a próxima opção será "Saída de Serviço"
    if 6 in paradas_registradas:
        return ["Saída de Serviço"], [7]

    return [], []  # Caso padrão, nenhuma opção disponível



################## APRESENTAÇÃO FRONT ##################
st.title("Gestão de Ponto")

with st.expander("Criar Jornada"):
    col1, col2 = st.columns([2, 1])
    with col1:
        itinerario = st.text_input("Itinerário")
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
            with st.spinner("Criando Jornada"):
                if 0 not in check_campos:            
                    try:
                        # Estabelece a conexão com o banco
                        conexao = conexaoBD()
                        cursor = conexao.cursor()


                        ############# CRIANDO INSERT COM PARÂMETROS #############
                        cmd = """INSERT INTO pmax_getregistro(fgkey_servicolin, fgkey_motorist, matricula_motorist, itinerario, num_veiculo, num_mapa, kms)
                                VALUES (%s, %s, %s, %s, %s, %s, %s);"""
                        
                        parametros = (
                            1,
                            679,
                            limpa_insert(255),
                            limpa_insert(itinerario),
                            numVeiculo,
                            numMapa,
                            limpa_insert(Kms)
                        )
                        
                        cursor.execute(cmd, parametros)
                        conexao.commit()

                        st.toast('Jornada criada com sucesso!', icon='✅')
                        sleep(1)
                        st.rerun()
                    except Exception as e:
                        conexao.rollback()
                        st.toast(f'Ocorreu um erro ao salvar a jornada: {str(e)}', icon='❌')
                    finally:
                        cursor.close()
                        conexao.close()
                else:
                    st.toast('Por favor, preencha todos os campos corretamente!', icon='❌')



alldados_jornada = consulta_jornada()
    
#SEPARANDO OS DADOS DA JORNADA QUE ESTÃO EM ABERTO DOS QUE ESTÃO FECHADOS
jornadas_open = []
jornadas_close = []
for dd_iti in alldados_jornada:
    if 'Saída de Serviço' not in [x['nome_parada'] for x in dd_iti['paradas']]:
        jornadas_open.append(dd_iti)
    else:
        jornadas_close.append(dd_iti)


tab1, tab2 = st.tabs(["Jornadas em aberto", "Histórico de Jornadas"])
with tab1:
    opc_jornadas, registros_pontos = get_jornadas_disponiveis(fgkey_motorist=679)  # ID do motorista
    
    if opc_jornadas:
        for jornada in opc_jornadas:

            id_jornada = jornada[0]
            dados_jornada = [x for x in jornadas_open if x['id_itinerario'] == id_jornada]

            # Criando o nome do expander concatenando os valores
            nome_expander = f"{jornada[1]} - {jornada[2]} - {jornada[3].strftime('%d/%m/%Y %H:%M')}"
            with st.expander(nome_expander):
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    fgkey_jornada = jornada[0]  # Assumindo que o índice 0 seja o ID da jornada

                    # Filtra os registros de ponto para essa jornada específica
                    paradas_registradas = [reg[1] for reg in registros_pontos if reg[0] == fgkey_jornada]

                    # Definir as opções do selectbox com base nas paradas já registradas
                    opc_nomes_typeregistros, opc_ids_typeregistros = definir_opcoes_parada(paradas_registradas)

                    # Mostrar o selectbox com as opções filtradas
                    tpParada = st.selectbox(
                        "Tipo de Ponto", 
                        opc_nomes_typeregistros, 
                        index=None, 
                        placeholder="Selecione o tipo de parada", 
                        key=f"Tipo de Ponto - {fgkey_jornada}"
                    )
        
                    
                if tpParada:
                    
                    # Retorna o id correspondente ao nome selecionado
                    idParada = opc_ids_typeregistros[opc_nomes_typeregistros.index(tpParada)]
                    
                    with col2:
                        dtInicio = st.date_input("Data de Início", key=f"Data de Início - {nome_expander}")
                    with col3:
                        hrInicio = st.time_input("Hora de Início", key=f"Hora de Início - {nome_expander}")
                    datetime_ini = datetime.strptime('{} {}'.format(dtInicio, hrInicio), "%Y-%m-%d %H:%M:%S")
                    
                    cmdvalues_insert = '(%s, %s, %s)'
                    columns_insert = ('fgkey_get_regist', 'fgkey_typ_regist', 'datetime_ini')
                    parametros_insert = (id_jornada, idParada, str(datetime_ini))

                    datetime_fim = 'NULL'
                    if idParada not in [1, 2, 6, 7]:

                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col2:
                            dtFim = st.date_input("Data de Fim", key=f"Data de Fim - {nome_expander}")
                        with col3:
                            hrFim = st.time_input("Hora de Fim", key=f"Hora de Fim - {nome_expander}")
                        
                        datetime_fim = datetime.strptime('{} {}'.format(dtFim, hrFim), "%Y-%m-%d %H:%M:%S")
                        
                        cmdvalues_insert = '(%s, %s, %s, %s)'
                        columns_insert = ('fgkey_get_regist', 'fgkey_typ_regist', 'datetime_ini', 'datetime_fim')
                        parametros_insert = (id_jornada, idParada, str(datetime_ini), str(datetime_fim))
                
                    colAux, col4 = st.columns([4, 1])
                    with col4:
                        st.write(" ")
                        st.write(" ")
                        registrar = st.button("Registrar", use_container_width=True, key=f"Registrar - {nome_expander}")

                    if registrar:
                        
                        try:
                            conexao = conexaoBD()
                            cursor = conexao.cursor()

                            cmd = f"""INSERT INTO pmax_setregistro {str(columns_insert).replace("'", "")}
                                        VALUES {cmdvalues_insert};"""
                            
                            cursor.execute(cmd, parametros_insert)
                            conexao.commit()

                        except Exception as e:
                            conexao.rollback()
                            st.toast(f'Ocorreu um erro ao salvar a jornada: {str(e)}', icon='❌')
                        finally:
                            st.toast(f'Jornada registrada!', icon='✅')
                            st.cache_data.clear()
                            cursor.close()
                            conexao.close()
                            sleep(0.1)
                            st.rerun()

                html = f"""<div class="container-pontos">
                    <div class="container-jornada">
                        <p>Itinerário: {dados_jornada[0]['itinerario']}</p>
                        <p>Nº do Veículo: {dados_jornada[0]['numero_veiculo']}</p>
                        <p>Kms: {dados_jornada[0]['kms']}</p>
                        <p>Nº do Mapa: {dados_jornada[0]['numero_mapa']}</p>
                        <p>Id: {dados_jornada[0]['id_itinerario']}</p>
                    </div>"""

                def limpa_parada(return_parada):
                    if return_parada is None:
                        return ' '
                    else:
                        return return_parada


                for index, parada in enumerate(dados_jornada[0]['paradas'], start=1):
                    
                    html += f"""<div class="container-tipoParada">
                        <div class="numRegistro">
                            <p>{index}</p>
                        </div>
                        <div class="nomeParada">
                            <p>{parada['nome_parada'] if parada['nome_parada'] != None else 'Ainda não há informações registradas'}</p>
                        </div>
                        <div class="container-paradas">"""
                    if 'info_parada' in parada:
                        html += f"""<div class="infoParada">
                                <p>{limpa_parada(parada['info_parada'])}</p>
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
    else:
        st.write("Nenhuma jornada disponível.")
        

with tab2:
    dados_jornadas = jornadas_close
    
    for jornada in dados_jornadas:
        with st.expander(f"Registros de Ponto: {jornada['itinerario']} - {jornada['hora_insert'].strftime('%d/%m/%Y %H:%M')}"):
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

