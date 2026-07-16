# Banco de Dados

O aplicativo utiliza um banco de dados relacional chamado **SQLite**. Ele é ideal para projetos pequenos e médios porque não exige um servidor de banco de dados rodando separadamente (como o MySQL ou PostgreSQL); todos os dados ficam salvos em um único arquivo chamado `baby_routine.db`.

## O ORM (SQLAlchemy)

Para não termos que escrever códigos SQL complexos na mão, o Backend utiliza uma biblioteca famosa do Python chamada **SQLAlchemy**.

O SQLAlchemy atua como um tradutor. Nós escrevemos classes Python, e ele traduz isso para tabelas no banco de dados.

Veja o arquivo `backend/database.py`:

Nós criamos a classe Base, que serve como molde. A partir dela, desenhamos as nossas tabelas.

### Tabela de Fraldas (DiaperChange)
- **id:** Um número único (Chave Primária).
- **date:** A data em que a fralda foi trocada.
- **time:** A hora exata.
- **type:** O tipo de fralda (Ex: "Urina", "Fezes", ou "Ambos").

### Tabela de Banhos (BathRecord)
- **id:** Um número único.
- **date:** Data do banho.
- **time:** Hora do banho.
- **type:** O tipo (Ex: "Ofurô", "Banheira", "Chuveiro").
- **notes:** Notas ou observações opcionais sobre o banho.

## A Sessão (SessionLocal)

Toda vez que o celular (Frontend) pede para o servidor ler ou salvar alguma coisa, o servidor não pode simplesmente invadir o banco de dados. Ele precisa abrir uma "Sessão" (como se fosse abrir a porta de um cofre), fazer o que precisa, e depois fechar a porta.

O `AsyncSessionLocal` faz exatamente isso de forma assíncrona, garantindo que dezenas de conexões possam ser feitas ao mesmo tempo sem travar o aplicativo.
