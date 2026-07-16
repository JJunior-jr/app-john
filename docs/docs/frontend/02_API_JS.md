# A Ponte Mágica (api.js)

Para que a nossa interface visual (Frontend) consiga enviar dados ou pedir relatórios ao servidor (Backend), ela precisa de uma ferramenta. Essa ferramenta mora no arquivo `api.js`.

O papel exclusivo deste arquivo é ser o "Mensageiro".

## O que é o `fetch`?
No JavaScript moderno, usamos uma função nativa chamada `fetch()` (buscar/trazer) para fazer requisições HTTP na internet.

Exemplo clássico dentro do nosso arquivo:
```javascript
async function startFeeding() {
    // ...
    const response = await fetch(`${API_BASE_URL}/feedings/start`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ type, start_time: timeStr })
    });
    // ...
}
```

### Destrinchando a Requisição
- **`${API_BASE_URL}`**: Lembra que dissemos que o Backend roda no endereço `https://sua-vps.com`? Essa variável guarda esse endereço.
- **`method: 'POST'`**: Estamos avisando ao servidor: "Tome aqui um dado novo para você salvar!"
- **`'Content-Type': 'application/json'`**: É como se falássemos: "Ei FastAPI, eu estou falando em JSON com você, prepare-se para ler JSON."
- **`JSON.stringify(...)`**: O JavaScript empacota os dados da mamada no formato de texto JSON puro antes de enviar pela rede.

## Async e Await
Repare nas palavras `async` e `await`. O JavaScript no navegador é apressado. Se ele mandasse um pedido para a China, ele não ia esperar a resposta voltar, ele ia continuar executando o resto do código da tela e poderia causar bugs.
Ao usar o `await`, nós forçamos o JavaScript a cruzar os braços e esperar (de forma assíncrona, sem congelar o navegador) até que o servidor FastAPI responda que a Mamada foi salva com sucesso. Só depois disso, ele continua.
