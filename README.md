# Documentação do Projeto

Este projeto contém scripts em Python para tratar dados de insumos de obras, incluindo a leitura, conversão e agrupamento de dados de arquivos Excel.

## Estrutura do Projeto

- `Entities/tratamento_dados/tratar.py`: Contém funções para converter e agrupar dados de arquivos Excel.
- `Entities/tratar_dados.py`: Contém a classe `TratarDados` que coordena o processamento dos arquivos.
- `Entities/get_files.py`: Contém a classe `FilesPath` que obtém a lista de arquivos Excel a serem processados.
- `Entities/exceptions.py`: Define exceções personalizadas para o projeto.
- `main.py`: Script principal para executar o processamento dos dados.

## Descrição dos Arquivos

### `Entities/tratamento_dados/tratar.py`

Este arquivo contém funções para converter e agrupar dados de arquivos Excel.

- `__conversor(row: pd.Series, df_medidas: pd.DataFrame, finalidade: str) -> pd.Series`: Converte uma linha do DataFrame de acordo com as medidas e finalidade fornecidas.
- `__create_climas(q: multiprocessing.Queue, df: pd.DataFrame, df_convert: pd.DataFrame)`: Cria o DataFrame de climas aplicando a função de conversão e agrupando os resultados.
- `__create_relatorios(q: multiprocessing.Queue, df: pd.DataFrame, df_convert: pd.DataFrame)`: Cria o DataFrame de relatórios aplicando a função de conversão e agrupando os resultados.
- `__exec(base_file: str, file: str) -> dict`: Executa o processo de leitura, conversão e agrupamento dos dados.
- `tratar(queue: multiprocessing.Queue, base_file: str, file: str)`: Função principal para tratar os dados, colocando o resultado na fila fornecida.

### `Entities/tratar_dados.py`

Este arquivo contém a classe `TratarDados` que coordena o processamento dos arquivos.

- `TratarDados.preprar(lista: list, tabela_base: str) -> List[pd.DataFrame]`: Prepara os dados processando uma lista de arquivos e uma tabela base.

### `Entities/get_files.py`

Este arquivo contém a classe `FilesPath` que obtém a lista de arquivos Excel a serem processados.

- `FilesPath.get() -> list`: Obtém a lista de arquivos Excel (.xlsx, .xls, .xlsm) nos diretórios especificados.

### `Entities/exceptions.py`

Este arquivo define exceções personalizadas para o projeto.

- `SheetNotFoundError`: Exceção levantada quando uma planilha específica não é encontrada.
- `ColumnNotFoundError`: Exceção levantada quando uma coluna específica não é encontrada.

### `main.py`

Este é o script principal para executar o processamento dos dados.

- `Execute.start()`: Função principal que coordena a execução do processamento dos dados.