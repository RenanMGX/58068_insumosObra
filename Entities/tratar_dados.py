from typing import List
import locale
import multiprocessing
from Entities.tratamento_dados.tratar import tratar, pd

multiprocessing.freeze_support()
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')



class TratarDados:
    @staticmethod
    def preprar(*, lista:list, tabela_base:str) -> List[pd.DataFrame]:
        threads:List[multiprocessing.Queue] = []
        
        for file in lista:
            q = multiprocessing.Queue()
            p = multiprocessing.Process(target=tratar, args=(q, tabela_base, file))
            p.start()
            threads.append(q)
        
        result = [] 
        for thread in threads:
            results:dict = thread.get()
            if (errors:=results.get('erros')):
                if errors:
                    print(errors)
            result.append(results.get('df'))
            
        return result

if __name__ == "__main__":
    TratarDados.preprar(lista=["file1", "file2"], tabela_base="base_file")
    