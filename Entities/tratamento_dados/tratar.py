import pandas as pd
import openpyxl
import os
import numpy as nb
from datetime import datetime
from typing import Literal, List, Dict, Union
import locale
import multiprocessing
from Entities import exceptions
import traceback

multiprocessing.freeze_support()
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

valid_sheets:List[str] = ['Base de Dados', 'Despesas']
count:int = 0
def __conversor(row:pd.Series, df_medidas:pd.DataFrame, finalidade:str):
    fina = ""
    if finalidade == 'FINALIDADE 2':
        fina = ".1"
    texto = row['Texto do pedido']
    result = df_medidas[df_medidas['TxtBreveMaterial'] == texto]
    coluna_pep = [x for x in row.keys() if "pep" in str(x).lower()][0]
    centro = str(row[coluna_pep]).split('.')[0]
    
    if not result.empty:
        new_row = pd.Series()
        
        new_row['MÊS'] = row['Data de lançamento'].strftime('%B').title()
        new_row['ANO'] = row['Data de lançamento'].year
        new_row['CENTRO'] = centro
        new_row['TEXTO'] = texto
        new_row['PARÂMETRO'] = result['PARÂMETRO'].values[0]
        if (result[finalidade].values[0] != '-'):
            if (fator:=result['FATOR DE CONVERSÃO'+fina].values[0]) and (isinstance(result['FATOR DE CONVERSÃO'+fina].values[0], (int, float)) and (str(result['FATOR DE CONVERSÃO'+fina].values[0]) != "nan")):                new_row['QNTD. TOTAL'] = (row['Qtd.total entrada'] * fator)
            else:
                new_row['QNTD. TOTAL'] = "?"
            
            new_row['UM'] = result['UM'+fina].values[0]   
            
            new_row['FINALIDADE'] = result[finalidade].values[0]        

            return new_row    
    return pd.Series()

def __create_climas(q:multiprocessing.Queue, df:pd.DataFrame, df_convert:pd.DataFrame):
    try:
        climas = df.apply(__conversor, axis=1, args=(df_convert,'FINALIDADE 1')).dropna(subset=['MÊS']).astype({'MÊS':str,'ANO':int})
        climas = climas.groupby(['MÊS', 'ANO', 'CENTRO', 'TEXTO', 'PARÂMETRO', 'UM', 'FINALIDADE'], as_index=False).sum()
        return q.put(climas)
    except Exception as e:
        return q.put(e)

def __create_relatorios(q:multiprocessing.Queue, df:pd.DataFrame, df_convert:pd.DataFrame):
    try:
        relatorios = df.apply(__conversor, axis=1, args=(df_convert,'FINALIDADE 2')).dropna(subset=['MÊS']).astype({'MÊS':str,'ANO':int})
        relatorios = relatorios.groupby(['MÊS', 'ANO', 'CENTRO', 'TEXTO', 'PARÂMETRO', 'UM', 'FINALIDADE'], as_index=False).sum()
        return q.put(relatorios)
    except Exception as e:
        return q.put(e)

def __exec(base_file, file):
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
    df = df[
        (df['estornado'] != 'X') &
        (df['Documento de estorno'] != 'X')
    ]
    
    q_climas = multiprocessing.Queue()
    q_relatorios = multiprocessing.Queue()
    multiprocessing.Process(target=__create_climas, args=(q_climas, df, df_convert)).start()
    multiprocessing.Process(target=__create_relatorios, args=(q_relatorios, df, df_convert)).start()
    
    result:Dict[str, Union[dict,pd.DataFrame]] = {
        "erros" : {},
    }
    
    df_final = pd.DataFrame()
    if isinstance(climas:=q_climas.get(), pd.DataFrame):
        df_final = pd.concat([df_final, climas])
    else:
        result['error']['climas'] = climas
        
    if isinstance(relatorios:=q_relatorios.get(), pd.DataFrame):
        df_final = pd.concat([df_final, relatorios])
    else:
        result['error']['relatorios'] = relatorios
    
    df_final['QNTD. TOTAL'] = df_final['QNTD. TOTAL'].replace(r'\?+', '?', regex=True)
    
    result["df"] = df_final
    
    return result

def tratar(queue:multiprocessing.Queue, base_file, file):
    return queue.put(__exec(base_file, file))
