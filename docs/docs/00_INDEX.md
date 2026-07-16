# Visão Geral e Mapa da Documentação

Bem-vindo à Wiki do aplicativo **App Joãozinho**!

Este projeto foi construído para registrar a rotina do Joãozinho (mamadas, sono, fraldas e banhos) com uma interface moderna no navegador e um servidor robusto e rápido.

## O que você vai encontrar aqui?

Navegue pelo menu lateral para entender cada pedaço do projeto:

- **[Arquitetura do Projeto](./ARQUITETURA.md):** Como o celular (Frontend) se comunica com a VPS (Backend).
- **[Infraestrutura e Deploy](./INFRA_E_DEPLOY.md):** Como o Docker mantém o aplicativo no ar e protegido na nuvem.

### Backend (O Cérebro)
- **[Banco de Dados (SQLite e SQLAlchemy)](./backend/DATABASE.md):** Onde os dados moram e como as tabelas estão estruturadas.
- **[Validação de Dados (Pydantic)](./backend/SCHEMAS.md):** Como evitamos que informações quebradas entrem no banco.
- **[Regras de Negócio (main.py)](./backend/MAIN.md):** O núcleo da aplicação e as contas matemáticas complexas de tempo e média.

### Frontend (O Rosto)
- **[Estrutura Visual (HTML/CSS)](./frontend/HTML_CSS.md):** O design e como as telas se adaptam ao celular.
- **[Comunicação com API (api.js)](./frontend/API_JS.md):** A ponte mágica que faz o celular enviar pedidos ao servidor.
- **[Lógica da Tela (app.js)](./frontend/APP_JS.md):** Como desenhamos gráficos do Chart.js e escondemos itens sem dados na interface.
