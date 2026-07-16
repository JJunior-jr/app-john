# Lógica Visual (app.js)

Enquanto o `api.js` é o mensageiro, o arquivo `app.js` é o grande orquestrador da tela. Ele é o responsável por:
1. Escutar quando você clica em um botão.
2. Ler o que está escrito nos campos de texto.
3. Chamar o `api.js` pedindo para salvar.
4. Mostrar ou esconder partes da tela.
5. Desenhar os Gráficos.

## Manipulação do DOM
DOM significa "Document Object Model". Basicamente, é como o JavaScript enxerga a página HTML. 

No arquivo `app.js`, usamos muito a função:
```javascript
document.getElementById('feeding-section').style.display = 'block';
```
Isso faz o JavaScript procurar no HTML uma tag que tenha o `id="feeding-section"` e injetar uma regra CSS `display: block` para torná-la visível. É assim que o aplicativo alterna entre as telas de Mamada, Sono e Relatório sem precisar recarregar a página!

## Desenhando Gráficos (Chart.js)
Na área de relatórios, nós utilizamos uma biblioteca externa famosa chamada **Chart.js**.

O `app.js` pega os dados puros recebidos pelo `api.js` (como por exemplo: O bebê dormiu 5 horas na segunda-feira e 6 horas na terça) e converte em Arrays (listas de dados).
Em seguida, ele manda o Chart.js desenhar um gráfico de barras no elemento `<canvas id="sleepChart"></canvas>` que deixamos preparado no HTML.

## Tratamento de Dados Vazios
Uma das lógicas mais importantes criadas recentemente no `app.js` foi o tratamento de telas vazias.

Se o banco de dados retornar uma lista de mamadas vazia (`[]`), o `app.js` detecta isso e, em vez de mostrar uma tabela horrível sem dados, ele oculta a tabela inteira e exibe a mensagem amigável: *"Nenhuma mamada registrada para a data atual"*.
