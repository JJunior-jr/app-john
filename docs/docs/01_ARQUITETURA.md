# Arquitetura do Sistema

O App Joãozinho utiliza um padrão moderno de desenvolvimento chamado **Client-Server** (Cliente-Servidor) via API REST.

Isso significa que a sua aplicação é dividida em duas grandes peças que rodam separadamente e conversam entre si usando uma linguagem comum chamada **JSON**.

## A Separação das Responsabilidades

### 1. O Cliente (Frontend)
É a interface que você acessa no seu celular ou computador. Ele é feito apenas de HTML, CSS e JavaScript puros.
- O Frontend **não** acessa o banco de dados.
- O Frontend **não** sabe salvar informações.
- A única coisa que o Frontend sabe fazer é desenhar botões na tela e, quando você clica neles, enviar um "pedido" (uma requisição HTTP) para o Servidor.

### 2. O Servidor (Backend API)
É o cérebro que roda 24h por dia na sua VPS (Virtual Private Server) usando a linguagem Python e o framework **FastAPI**.
- Ele escuta os pedidos do Frontend.
- Valida as regras (ex: "é possível iniciar uma mamada agora?").
- Salva e lê dados do **Banco de Dados SQLite**.
- Retorna uma resposta (geralmente uma confirmação ou os dados de um relatório) de volta para o celular.

## O Fluxo de uma Ação (Ex: Iniciar Mamada)

1. Você clica no botão "Iniciar Mamada" no celular.
2. O arquivo `app.js` pega a data e hora atuais.
3. O `api.js` empacota isso num JSON e faz um `fetch()` para o endereço `https://sua-vps.com/api/feedings/start`.
4. O servidor recebe o pedido no arquivo `routers/feeding.py`.
5. O servidor confere no arquivo `schemas.py` se a formatação dos dados está correta (se enviou um texto ou um horário válido).
6. O servidor pede ao `database.py` para abrir uma conexão com o SQLite.
7. O servidor salva o horário de início na tabela `feedings`.
8. O servidor responde para o celular: `{"message": "Mamada iniciada com sucesso"}`.
9. O celular recebe a resposta e muda a cor do botão na tela.

---

> [!TIP]
> Essa separação é o que torna o seu app escalável! No futuro, se você quiser criar um aplicativo nativo para Android ou iPhone, você só precisa recriar a "cara" do app. O Cérebro (Backend) continuará sendo exatamente o mesmo, atendendo a qualquer dispositivo que fale JSON.
