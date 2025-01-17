from typing import List
import locale
import multiprocessing
from Entities.tratamento_dados.tratar import tratar, pd

multiprocessing.freeze_support()
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

class TratarDados:
    @staticmethod
    def preprar(*, lista:list, tabela_base:str) -> List[pd.DataFrame]:
        """
        Prepara os dados processando uma lista de arquivos e uma tabela base.
        
        Args:
            lista (list): Lista de caminhos para os arquivos a serem processados.
            tabela_base (str): Caminho para o arquivo base contendo as medidas de conversão.
        
        Returns:
            List[pd.DataFrame]: Lista de DataFrames resultantes do processamento.
        """
        threads:List[multiprocessing.Queue] = []
        
        # Cria processos para tratar cada arquivo na lista
        for file in lista:
            q = multiprocessing.Queue()
            p = multiprocessing.Process(target=tratar, args=(q, tabela_base, file))
            p.start()
            threads.append(q)
        
        result = [] 
        # Obtém resultados dos processos
        for thread in threads:
            results:dict = thread.get()
            if (errors:=results.get('erros')):
                if errors:
                    print(errors)
            result.append(results.get('df'))
            
        return result

if __name__ == "__main__":
    # Exemplo de uso da classe TratarDados
    TratarDados.preprar(lista=["file1", "file2"], tabela_base="base_file")
