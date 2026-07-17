# Guia de Desenvolvimento e Implementação de Novas Funcionalidades (App Rotina do João)

Este guia apresenta um passo a passo completo das diretrizes, arquivos impactados e lógicas a serem utilizadas para implementar novas funcionalidades e refatorações no sistema.

## 🔄 Fluxo de Trabalho (Git e Github)
1. **Criar uma nova branch** para cada funcionalidade (para não mexer no código principal):
   ```bash
   git checkout -b feat/nome-da-funcionalidade
   ```
2. Realizar as edições e criar os arquivos detalhados abaixo.
3. Adicionar e commitar as alterações:
   ```bash
   git add .
   git commit -m "feat: adiciona funcionalidade x"
   ```
4. Subir a sua branch para o seu repositório no GitHub:
   ```bash
   git push -u origin feat/nome-da-funcionalidade
   ```
5. Acessar o GitHub e abrir um **Pull Request (PR)** da sua branch apontando para a `main`. Após você ou outra pessoa revisar o código, fazer o **Merge**.

---

## 🚀 Feat 1: Tempo Acordado e Ajuste no Tempo de Sono

Esta funcionalidade engloba as regras de visualização do tempo acordado do João e uma correção na lógica do tempo de sono que passa da meia-noite.

### 1. Tempo Acordado Atual
- Calcular e exibir no painel de resumo o tempo que ele está acordado atualmente.
- A lógica deve pegar o último momento que ele acordou (fim do último registro de sono) e calcular o tempo até o momento atual.
- Exemplo: se ele dormiu das 12:00 até as 13:00, e agora são 16:00, e ele ainda não teve um novo registro de "começou a dormir", o painel deve mostrar que ele está acordado há 3 horas.

### 2. Tempo Total Acordado
- No painel de resumo, mostrar o "Tempo Total Acordado", que soma as horas em que ele esteve acordado ao longo do dia inteiro.

### 3. Ajuste na Regra do "Tempo de Sono" (Divisão de Dias)
- Ajustar a lógica para quando o sono ultrapassa a meia-noite, dividindo o tempo entre os dias adequadamente.

---

## 🚀 Feat 3: Tempo Sem Comer
- Seguir a mesma lógica do "Tempo Acordado Atual".
- Buscar o último registro de amamentação realizado (independentemente de ser ontem ou hoje).
- Calcular quanto tempo faz que ele não come, em relação ao momento atual.
- Se a última amamentação foi dia 09/07 às 22h, e agora são 02:00 do dia 10/07, o painel deve mostrar que ele está sem mamar há 4 horas.

---

## 🚀 Feat 4: Dashboard de Estatísticas e Relatórios Avançados
- **Gráficos Visuais**: Inclusão de gráficos interativos (via Chart.js) exibindo relação Sono vs Acordado e Ofertado vs Consumido dos últimos 7 dias.
- **Detalhamento no Histórico**: Refatoração da tabela de relatórios para incluir "Nº Mamadas", "Máx Jejum", "Tempo Acordado" e "Média Cochilo".
- **Fatiamento de Sono no Histórico**: Assim como no painel diário, o histórico agora fatia e distribui horas de sono adequadamente quando passam da meia-noite.
- **Alertas Visuais**: Destaque em vermelho pálido caso a diferença (Aceitação da Mamadeira) seja menor que 70%.
- Exemplo: Se o sono começou no dia 09/07 às 22:00 e terminou às 02:00 do dia 10/07:
  - 2 horas (das 22:00 às 23:59) devem ser computadas no total do dia 09.
  - 2 horas (das 00:00 às 02:00) devem ser computadas no total do dia 10.

---

## 🛠️ Refatoração 2: Melhorias em Amamentação e Relatórios

O objetivo aqui é incluir percentuais (Diferença) tanto na visualização diária quanto nos relatórios, além de expandir a edição dos registros de amamentação e ampliar a tabela para a tela inteira.

### 1. Percentual nos Registros de Amamentação
- Adicionar o percentual de aceitação diretamente nos registros individuais de "amamentação" que aparecem na tela principal.
- Exibição: mostrar a quantidade ofertada e a aceita e, ao lado, o percentual correspondente.

### 2. Percentual no Painel de Resumo
- No painel de resumo já aparece o Total Ofertado e o Total Consumido daquele dia. 
- Adicionar ao painel:
  - O percentual relativo a estes totais (Total Consumido / Total Ofertado).
  - O percentual da média do dia.

### 3. Edição Completa da Amamentação
- Expandir a funcionalidade de edição dos registros de amamentação (que hoje permite editar a hora) para que seja possível também editar a **quantidade ofertada (ml)** e a **quantidade consumida (ml)**.

### 4. Aumentar a Visualização (Tela Cheia) - Relatórios
- **No arquivo `frontend/css/style.css`**:
  - Atualmente a seção `.card` restringe as telas em caixinhas centrais usando o `max-width`.
  - Crie uma hierarquia específica para que o card do relatório não sofra essa restrição:
    ```css
    #view-reports .card {
        max-width: 95vw; /* Expande o quadro de ponta a ponta na tela */
        height: 85vh; /* Ocupa 85% de toda a altura da tela (ajuda telas de celular) */
        overflow-y: auto; /* Exibe barra de rolagem apenas dentro do quadro de relatórios */
    }
    ```

---

## 🌍 Deploy para Produção na OCI (Oracle Cloud)

Depois que você codificou, testou na sua máquina, criou o PR e a branch principal (`main`) já está com o código pronto lá no GitHub, chegou a hora de atualizar sua VPS:

1. **Acesse sua VPS da Oracle via Terminal (SSH):**
   ```bash
   ssh ubuntu@IP_DA_SUA_VPS
   ```
2. **Navegue até a pasta onde o projeto está hospedado:**
   ```bash
   cd /home/ubuntu/app-john # Ou o diretório que você criou
   ```
3. **Puxe a versão mais atualizada da branch main direto do GitHub:**
   ```bash
   git checkout main
   git pull origin main
   ```
4. **Reconstrua os Containers do Docker:**
   ```bash
   # Como foram modificados arquivos do backend e pacotes, 
   # a tag --build é OBRIGATÓRIA para o container injetar o código novo!
   docker compose up -d --build
   ```

Pronto! Seu App será recarregado já com as novas lógicas de tempo, percentuais e relatórios atualizados em tela cheia na internet. Os registros antigos permanecerão intocáveis, uma vez que o banco de dados `baby_routine.db` está sendo salvo externamente nos volumes do Docker de forma persistente.

---

## 📚 Lições Aprendidas no Deploy e Manutenção (Atualizado em 16/07/2026 às 22:30)

Durante o processo de deploy e testes em produção na VPS, enfrentamos alguns desafios técnicos que geraram aprendizados valiosos para a sustentação do projeto:

1. **Firewall e Redes do Docker (`iptables` e `502 Bad Gateway`):**
   * **O Erro:** Ao rodar `docker compose up --build`, as regras de rede (`iptables`) do Linux se corromperam, fazendo com que o Nginx perdesse a comunicação com a API.
   * **A Lição:** Quando containers perdem conectividade externa "do nada" na VPS após um rebuild, a solução mais eficaz é reiniciar o serviço principal do Docker (`sudo systemctl restart docker`) para forçar o sistema operacional a recriar as pontes de rede e as regras de firewall do zero.

2. **Mapeamento de Volumes do Nginx Proxy Manager:**
   * **O Erro:** Ao mapearmos a pasta do Nginx como `./data/nginx:/data`, o Nginx iniciou com um banco de dados em branco, exibindo a tela de "Congratulations" e perdendo todas as rotas de domínio (Proxy Hosts).
   * **A Lição:** O Nginx Proxy Manager cria sua própria estrutura de pastas (incluindo o `database.sqlite`) na raiz do volume `/data`. O correto é mapear a raiz (`./data:/data`) para preservar o banco de dados interno e manter os certificados HTTPS e rotas salvos.

3. **Permissões do SQLite (Erro: `attempt to write a readonly database`):**
   * **O Erro:** A API travava (retornando erro 500) ao tentar finalizar um sono em andamento ou criar novos registros.
   * **A Lição:** Ao copiar o banco de dados via `scp` ou `docker cp` para a VPS (usando pastas compartilhadas/bind mounts), o arquivo fica pertencendo ao usuário `root` ou `ubuntu`. Como a API roda por segurança com um usuário restrito (`appuser`), ela perdia o direito de escrita. A solução definitiva para esse conflito de Bind Mounts foi garantir permissão global na pasta de dados (`sudo chmod -R 777 ~/app-john/data`).

4. **Tratamento de Exceções no Frontend (Cascata de Falhas):**
   * **O Erro:** Como a API falhava ao salvar devido às permissões do banco, a função `Promise.all` do Javascript no frontend recebia o erro 500 e interrompia toda a execução da página, travando a interface de carregamento (spinner infinito).
   * **A Lição:** Falhas em endpoints específicos não devem quebrar a tela inteira. É fundamental isolar as chamadas (usando `try/catch` individualizados) para que a interface continue operante mesmo se uma rota específica da API cair.

### 🚀 Oportunidade de Melhoria Futura: Backup Automático (Cron Job)
Em vez de depender de downloads manuais do arquivo `baby_routine.db` (o que pode causar corrupção se baixado no exato milissegundo em que uma gravação ocorre), a arquitetura ideal prevê a criação de uma rotina automática na VPS. 

**Como implementar:**
Criar uma tarefa no `crontab` do Linux para rodar todos os dias às 03:00 da manhã um script que faça um *dump* seguro do banco ativo:
```bash
# Exemplo de comando seguro para snapshot do SQLite:
sqlite3 /home/ubuntu/app-john/data/baby_routine.db ".backup '/home/ubuntu/app-john/backups/backup_diario.db'"
```
Desta forma, teremos sempre um arquivo "frio" e seguro (`backup_diario.db`) pronto para ser baixado a qualquer momento, sem risco de corrupção do banco em uso.
