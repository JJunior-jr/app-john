# Rotas (Os Carteiros)

Na pasta `routers/`, nós organizamos as rotas (endpoints) do aplicativo. Cada arquivo dessa pasta lida com um assunto específico: fraldas, mamadas, sono e banho.

As rotas são como "Carteiros". Elas recebem os pedidos do Frontend, entregam para o Banco de Dados, pegam a resposta e levam de volta para o Frontend.

## Exemplo: Rotas de Banho (`bath.py`)

Neste arquivo nós temos as três ações fundamentais do Banho:
1. Iniciar o Banho (Registra a hora de início).
2. Finalizar o Banho (Registra a hora do fim).
3. Cancelar o Banho (Exclui o registro se tivermos iniciado sem querer).

### O Decorator `@router`
Para criar uma rota no FastAPI, usamos um "Decorator" (aquele símbolo de `@` em cima da função).

```python
@router.post("/start", response_model=schemas.BathOut)
async def start_bath(bath_in: schemas.BathCreate, db: AsyncSession = Depends(get_db)):
    # ... código aqui ...
```
- **`@router.post`**: Define que esta rota deve ser acessada via método HTTP `POST` (usado para enviar/criar dados).
- **`"/start"`**: É o endereço (a rua do carteiro). Se juntarmos com o domínio, fica algo como `https://sua-vps.com/api/baths/start`.
- **`response_model=schemas.BathOut`**: É a garantia de que a resposta sempre será enviada no formato daquele Schema que criamos.
- **`Depends(get_db)`**: É o conceito de Injeção de Dependência. O FastAPI abre uma conexão com o banco de dados magicamente só para essa função e fecha logo depois.
