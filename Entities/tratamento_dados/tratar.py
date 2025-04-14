import pandas as pd
import openpyxl
import os
import numpy as np
from datetime import datetime
from typing import Literal, List, Dict, Union
import locale
import multiprocessing
import exceptions
import traceback

multiprocessing.freeze_support()
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Lista de sheets válidas que podem ser processadas
valid_sheets:List[str] = ['Sheet1']

# Contador auxiliar para possíveis usos futuros
count:int = 0

def __conversor(row:pd.Series, df_medidas:pd.DataFrame, finalidade:str):
    """
    Converte uma linha do DataFrame de acordo com as medidas e finalidade fornecidas.
    
    Args:
        row (pd.Series): Linha do DataFrame original.
        df_medidas (pd.DataFrame): DataFrame contendo as medidas de conversão.
        finalidade (str): Finalidade da conversão ('FINALIDADE 1' ou 'FINALIDADE 2').
    
    Returns:
        pd.Series: Nova linha convertida ou uma série vazia se a conversão não for possível.
    """
    fina = ""
    if finalidade == 'FINALIDADE 2':
        fina = ".1"
    texto = row['TxtBreveMaterial']

    if (texto is np.nan) or (not isinstance(texto, str)):
        print("Texto inválido:", texto, type(texto))
        return pd.Series()
    

    material = int(row['Material'])
    result = df_medidas[
        (df_medidas['TxtBreveMaterial'] == texto) &
        (df_medidas['Material'].astype(str) == str(material))
        ]
    
    #coluna_pep = [x for x in row.keys() if "pep" in str(x).lower()][0]
    #centro = str(row[coluna_pep]).split('.')[0]
    centro = row['Cen.']
    
    if not result.empty:
        new_row = pd.Series()
        
        new_row['MÊS'] = row['Dt.lçto.'].strftime('%B').title()
        new_row['ANO'] = row['Dt.lçto.'].year
        new_row['CENTRO'] = centro
        new_row['MATERIAL'] = material
        new_row['TEXTO'] = texto
        new_row['PARÂMETRO'] = result['PARÂMETRO'].values[0]
        if (result[finalidade].values[0] != '-'):
            if (fator:=result['FATOR DE CONVERSÃO'+fina].values[0]) and (isinstance(result['FATOR DE CONVERSÃO'+fina].values[0], (int, float)) and (str(result['FATOR DE CONVERSÃO'+fina].values[0]) != "nan")): 
                new_row['QNTD. TOTAL'] = (round(row['Quantidade'], 4) * fator)
            else:
                new_row['QNTD. TOTAL'] = "?"
            
            new_row['UM'] = result['UM'+fina].values[0]   
            
            new_row['FINALIDADE'] = result[finalidade].values[0]        

            # if texto == "BRITA 0 GNAISSE A GRANEL":
            #     print(new_row['MÊS'], new_row['ANO'], new_row['CENTRO'], new_row['MATERIAL'], "|||||||",fator, new_row['QNTD. TOTAL'], row['Quantidade'], result['UM'+fina].values[0])
                
            return new_row    
    return pd.Series()

def __create_climas(q:multiprocessing.Queue, df:pd.DataFrame, df_convert:pd.DataFrame):
    """
    Cria o DataFrame de climas aplicando a função de conversão e agrupando os resultados.
    
    Args:
        q (multiprocessing.Queue): Fila para colocar o resultado.
        df (pd.DataFrame): DataFrame original.
        df_convert (pd.DataFrame): DataFrame contendo as medidas de conversão.
    
    Returns:
        None
    """
    try:
        climas = df.apply(__conversor, axis=1, args=(df_convert,'FINALIDADE 1')).dropna(subset=['MÊS']).astype({'MÊS':str,'ANO':int})
        climas = climas.groupby(['MÊS', 'ANO', 'CENTRO','MATERIAL', 'TEXTO', 'PARÂMETRO', 'UM', 'FINALIDADE'], as_index=False).sum()
        
        return q.put(climas)
    except Exception as e:
        return q.put(e)

def __create_relatorios(q:multiprocessing.Queue, df:pd.DataFrame, df_convert:pd.DataFrame):
    """
    Cria o DataFrame de relatórios aplicando a função de conversão e agrupando os resultados.
    
    Args:
        q (multiprocessing.Queue): Fila para colocar o resultado.
        df (pd.DataFrame): DataFrame original.
        df_convert (pd.DataFrame): DataFrame contendo as medidas de conversão.
    
    Returns:
        None
    """
    try:
        relatorios = df.apply(__conversor, axis=1, args=(df_convert,'FINALIDADE 2')).dropna(subset=['MÊS']).astype({'MÊS':str,'ANO':int})
        relatorios = relatorios.groupby(['MÊS', 'ANO', 'CENTRO', 'MATERIAL', 'TEXTO', 'PARÂMETRO', 'UM', 'FINALIDADE'], as_index=False).sum()
        return q.put(relatorios)
    except Exception as e:
        return q.put(e)

def __exec(base_file, file):
    """
    Executa o processo de leitura, conversão e agrupamento dos dados.
    
    Args:
        base_file (str): Caminho para o arquivo base contendo as medidas de conversão.
        file (str): Caminho para o arquivo de dados a ser processado.
    
    Returns:
        dict: Dicionário contendo os DataFrames resultantes ou erros encontrados.
    """
    
    wb = openpyxl.load_workbook(file)
    selected_sheet:str = ""
    for sheet in wb.sheetnames:
        if sheet in valid_sheets:
            selected_sheet = sheet
    if not selected_sheet:
        return exceptions.SheetNotFoundError(f"nenhuma das sheet {valid_sheets=} foi encontrada!")
    
    sheet_convert = "CONVERSÃO MATERIAIS APLIC."
    try:
        df_convert = pd.read_excel(base_file, sheet_name=sheet_convert)
    except:
        return exceptions.SheetNotFoundError(f"a sheet {sheet_convert} não foi encontrada na planilha de conversão!")
    
    df = pd.read_excel(file, sheet_name=selected_sheet)
    # df = df[
    #     (df['estornado'] != 'X') &
    #     (df['Documento de estorno'] != 'X')
    # ]
    
    #df['abs_Quantidade'] = df['Quantidade'].abs()
    #duplicates = df.duplicated(subset=['abs_Quantidade', 'TxtBreveMaterial', 'Nome 1'], keep=False)
    #
    #df = df[~duplicates]
    
    df = df[
        ~df['TxtBreveMaterial'].isna()
    ]
    
    
    q_climas = multiprocessing.Queue()
    q_relatorios = multiprocessing.Queue()
    
    # Inicia processos para criar climas e relatórios
    p_climas = multiprocessing.Process(target=__create_climas, args=(q_climas, df, df_convert))
    p_relatorio = multiprocessing.Process(target=__create_relatorios, args=(q_relatorios, df, df_convert))
    
    p_climas.start()
    p_relatorio.start()
    
    result:Dict[str, Union[dict,pd.DataFrame]] = {
        "error" : {},
    }
    

    df_final = pd.DataFrame()
    
    # Obtém resultados dos processos
    if isinstance(climas:=q_climas.get(), pd.DataFrame):
        df_final = pd.concat([df_final, climas])
    else:
        result['error']['climas'] = climas
        
    if isinstance(relatorios:=q_relatorios.get(), pd.DataFrame):
        df_final = pd.concat([df_final, relatorios])
    else:
        result['error']['relatorios'] = relatorios
    
    try:
        df_final['QNTD. TOTAL'] = df_final['QNTD. TOTAL'].replace(r'\?+', '?', regex=True)
    except Exception as e:
        pass
        #print(type(e), e)
    
    # import pdb; pdb.set_trace()
    result["df"] = df_final
    
    return result

def tratar(queue:multiprocessing.Queue, base_file, file):
    """
    Função principal para tratar os dados, colocando o resultado na fila fornecida.
    
    Args:
        queue (multiprocessing.Queue): Fila para colocar o resultado.
        base_file (str): Caminho para o arquivo base contendo as medidas de conversão.
        file (str): Caminho para o arquivo de dados a ser processado.
    
    Returns:
        None
    """
    return queue.put(__exec(base_file, file))

if __name__ == "__main__":
    pass
    
    print(__exec(
                r'R:\58068 - Insumos de Obra - Qualidade\insumosObras\arquivos\convert\Materiais Aplicados - Conversão.xlsx',
                r'R:\58068 - Insumos de Obra - Qualidade\insumosObras\arquivos\novolar\Novolar_Materiais_faturados_01-01-2023_a_31-01-2025 - B.XLSX'
                 )
          )
