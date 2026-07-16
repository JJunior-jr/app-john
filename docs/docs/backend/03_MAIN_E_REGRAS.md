# Main (Regras de Negócio)

O arquivo `main.py` é o coração do projeto. Ele é o ponto de entrada do servidor FastAPI e onde a maior parte das lógicas complexas acontece.

Nós decidimos dividir a responsabilidade: O `main.py` possui as lógicas centrais e genéricas, enquanto a pasta `routers/` possui os arquivos específicos de cada módulo (como o `bath.py`).

## Estrutura do main.py

### 1. Inicialização e CORS
No topo do arquivo, o aplicativo FastAPI é instanciado.
Um ponto crítico aqui é o **CORS** (Cross-Origin Resource Sharing). Como o nosso site roda na porta `80` (Nginx) e a API na porta `8000`, o navegador bloquearia a comunicação por motivo de segurança. Nós adicionamos o `CORSMiddleware` no `main.py` para permitir que o Frontend e Backend conversem livremente.

### 2. O Motor de Relatórios (`get_reports_history`)
A funcionalidade mais complexa do sistema fica no `main.py`: A geração de relatórios de histórico diário.

O Frontend não precisa calcular nada. Ele simplesmente pede: "Me dê o relatório".
O `main.py` faz o seguinte processo:
1. Pega os últimos 7 dias.
2. Faz consultas ao banco de dados para buscar mamadas, fraldas e tempos de sono.
3. Faz cálculos matemáticos avançados:
   - Qual foi o tempo total de sono em um dia?
   - O bebê acordou de madrugada? Quanto tempo ficou acordado (Wake time)?
   - Se o bebê dormiu às 23:00 e acordou às 08:00, ele "fatia" esse sono: 1 hora conta para o dia anterior, e 8 horas contam para o dia atual.

### 3. Tratamento de Erros e Logs
Sempre que uma regra é violada (ex: tentar fechar um sono que já foi fechado), o `main.py` lança uma `HTTPException`, devolvendo um erro claro em JSON para o aplicativo poder mostrar uma caixinha vermelha amigável na tela do usuário.
