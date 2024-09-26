import mysql.connector
import streamlit as st

def tratar_direcao(dir):
    aux = {'I': 'IDA',
           'V': 'VOLTA'}
    
    return aux[str(dir).strip().upper()]


class Pmax():
    def __init__(self):
        self.__conexao = mysql.connector.connect(
            passwd='Destak2024',
            port=3306,
            user='admin',
            host='destakveiculos.cjq8g4ggucwy.us-east-1.rds.amazonaws.com',
            database='gestao_escala'
        )


    def __get_cursor(self):
        mycursor = self.__conexao.cursor()
        return mycursor


    def get_jornadas(self, matricula):
        cmd = f'''
            SELECT
                PXR.id_gregistro, 
                (
                    SELECT nome_cidade FROM cidades_pontos WHERE id_cidades = SL.fgkey_ponto_ini
                ) AS TRECHO_INICIO,
                (
                    SELECT nome_cidade FROM cidades_pontos WHERE id_cidades = SL.fgkey_ponto_fim
                ) AS TRECHO_FIM,
                ML.nome_motorista AS NOME_MOTORISTA,
                PXR.matricula_motorist,
                PXR.num_veiculo,
                PXR.num_mapa,
                PXR.kms,
                PXR.name_city_ini,
                PXR.name_city_fim,
                PXR.datetime_insert,
                PSR.id_sregistro,
                PSR.fgkey_get_regist,
                (
                    SELECT name_registro FROM pmax_typeregistro WHERE pmax_typeregistro.id_registro = PSR.fgkey_typ_regist
                ) AS NAME_TYPE,
                PSR.datetime_ini,
                PSR.datetime_fim,
                PXR.datetime_insert
            FROM pmax_getregistro PXR
            JOIN servico_linhas SL ON SL.id_linha = PXR.fgkey_servicolin
            JOIN motoristas_lista ML ON ML.id_mot = PXR.fgkey_motorist
            LEFT JOIN pmax_setregistro PSR ON PSR.fgkey_get_regist = PXR.id_gregistro
            WHERE PXR.matricula_motorist = '{matricula}' 
            GROUP BY PSR.id_sregistro, PXR.id_gregistro;
                '''
        
        cursor = self.__get_cursor()
        cursor.execute(cmd)
        
        jornadas = cursor.fetchall()
        cursor.close()

        return jornadas
    

    def get_registros_pontos(self):
        cursor = self.__get_cursor()

        cmd = """SELECT fgkey_get_regist, fgkey_typ_regist
            FROM pmax_setregistro;"""
        cursor.execute(cmd)
        registros_pontos = cursor.fetchall()

        cursor.close()
        return registros_pontos


    def get_jornadas_motorista(self, fgkey_motorist):
        cursor = self.__get_cursor()

        cmd = """SELECT
                id_gregistro, itinerario, fgkey_motorist
            FROM
                pmax_getregistro
            WHERE
                fgkey_motorist = %s;"""
        cursor.execute(cmd, (fgkey_motorist,))
        jornadas = cursor.fetchall()

        cursor.close()
        return jornadas
    

    @staticmethod
    def set_jornadas(dados_jornada_post):
        
        dados_jornada = []
        for iti in list(set([x[0] for x in dados_jornada_post])):
            dados_by_iti = [x for x in dados_jornada_post if x[0] == iti]

            #DADOS DO ITINERÁRIO
            jornada_aux = {
                'itinerario': '{} x {}'.format(dados_by_iti[0][1], dados_by_iti[0][2]),
                'numero_veiculo': dados_by_iti[0][5],
                'kms': dados_by_iti[0][7],
                'numero_mapa': dados_by_iti[0][6]
            } 

            #DADOS DAS PARADAS DO ITINERÁRIO
            paradas_aux = []
            for parad in list(set([x[13] for x in dados_by_iti])):
                dd_by_parada = [x for x in dados_by_iti if x[13] == parad]
            
                if len(dd_by_parada) > 1:

                    infos_paradas = []
                    for list_parad in dd_by_parada:
                        infos_paradas.append({'Inicio': list_parad[14], 'Fim': list_parad[15]})

                    aux_parads1 = {
                        'nome_parada': parad,
                        'infos_parada': infos_paradas}
                else:
                    aux_parads1 = {
                        'nome_parada': parad,
                        'info_parada':  dd_by_parada[0][14]
                        }
                   
                paradas_aux.append(aux_parads1)

            jornada_aux['paradas'] = paradas_aux
            dados_jornada.append(jornada_aux)
        
        return dados_jornada


    def get_typeregistros(self):
        cmd = """SELECT id_registro, name_registro 
            FROM pmax_typeregistro
            WHERE status_registro = 1;"""
        
        cursor = self.__get_cursor()
        cursor.execute(cmd)
        
        typeregistros = cursor.fetchall()
        cursor.close()

        return typeregistros


    @staticmethod
    def set_jornadas_opc(jornadas_post, registros_pontos):
        jornadas_disponiveis = [
            (x[0], x[1]) for x in jornadas_post
            if not any(y[1] == 7 for y in registros_pontos if y[0] == x[0])
        ]
        return jornadas_disponiveis
    

    def get_itinerarios(self):
        cmd = """        
            SELECT
                id_linha, 
                CP.nome_cidade AS CIDADE_INI,
                CP1.nome_cidade AS CIDADE_FIM,
                NOW() + INTERVAL hora_ini SECOND AS hora_ini,
                cod_linha,
                sentido_linha,
                status_linha
            FROM servico_linhas SL
            JOIN cidades_pontos CP ON CP.id_cidades = SL.fgkey_ponto_ini
            JOIN cidades_pontos CP1 ON CP1.id_cidades = SL.fgkey_ponto_fim;
        """    

        cursor = self.__get_cursor()
        cursor.execute(cmd)
        
        itinerarios = cursor.fetchall()
        cursor.close()

        return itinerarios


    @staticmethod
    def set_itirarios(dados_itinerarios_post):
        dados_itinerarios = [
                            '{}. {} x {} ({}) - {}'.format(
                                            x[0],
                                            x[1],
                                            x[2],
                                            tratar_direcao(x[5]),
                                            x[3].time()        
                                        )
                                for x in dados_itinerarios_post]
        
        return dados_itinerarios
    