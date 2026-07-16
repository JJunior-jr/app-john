# Schemas (Validação de Dados)

O arquivo `schemas.py` utiliza a biblioteca **Pydantic**. 

Muitas vezes, a palavra "Schema" (Esquema) se confunde com Banco de Dados. Mas no nosso Backend, os Schemas são **Validadores**.

## Por que precisamos de Schemas?
Imagine que a nossa interface Web sofra um "bug" e envie a data do banho como "Amanhã" (texto) em vez de "2026-07-12" (Data), ou envie o tipo de Fralda como um número `5`.

Se tentarmos salvar isso direto no Banco de Dados, o aplicativo inteiro pode quebrar (Erro 500) e parar de funcionar.

Os Schemas criam uma "porta blindada". O Pydantic recebe os dados do celular, valida se estão no formato correto, e se estiver errado, ele mesmo rejeita o pedido avisando o Frontend: "Atenção, formato de data inválido" antes mesmo de chegar no Banco de Dados.

## Exemplo: Fralda
```python
class DiaperCreate(BaseModel):
    type: str
```
Isso garante que ao pedir para criar um registro de fralda, o Frontend DEVE enviar um campo `type` contendo uma String (texto).

## Schemas de Resposta
Além de validar o que "entra", os Schemas padronizam o que "sai" do servidor (as respostas).
Quando respondemos com o schema `DiaperOut`, nós garantimos que o Frontend sempre receberá o `id`, a `date` e o `time` devidamente formatados.
