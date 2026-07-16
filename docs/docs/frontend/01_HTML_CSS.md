# Estrutura Visual (HTML e CSS)

A aparência do App Joãozinho é definida na pasta `frontend/`. Diferente do Backend que usa Python, aqui nós usamos as linguagens nativas da Web: **HTML** e **CSS**.

## 1. O Esqueleto (`index.html`)

O HTML (`index.html`) não tem inteligência, ele é apenas o esqueleto do aplicativo.

Ele é dividido usando *tags* semânticas:
- `<header>`: Onde fica o título e talvez o botão de alternar tema no futuro.
- `<main>`: O conteúdo principal.
- `<section>`: Nós dividimos as áreas do app em "seções" (Seção de Mamadas, Seção de Sono, Seção de Relatórios).

### IDs para Manipulação
Para que o JavaScript consiga encontrar e modificar partes da tela (como esconder uma área ou mudar a cor de um botão), as tags HTML recebem um atributo especial chamado `id`. Exemplo:
```html
<section id="sleep-section">
```
Isso permite que o arquivo `app.js` encontre facilmente essa seção.

## 2. A Maquiagem (`style.css`)

O arquivo `style.css` é responsável pelas cores, espaçamentos, bordas arredondadas e, principalmente, por fazer o aplicativo se adaptar a telas pequenas de celular (**Responsividade**).

### Variáveis CSS (Custom Properties)
No topo do arquivo CSS nós temos o `:root`. Isso é uma técnica avançada que permite definirmos variáveis de cor:
```css
:root {
  --primary-color: #3498db;
  --bg-color: #f5f6fa;
}
```
Isso significa que, se quisermos criar um "Tema Escuro" (Dark Mode) amanhã, nós só precisamos trocar os valores do `:root`, sem precisar reescrever o arquivo inteiro.

### Flexbox
A maior parte do alinhamento (botões lado a lado, caixas centralizadas) é feita usando o **CSS Flexbox** (`display: flex`). Isso permite que os elementos estiquem ou encolham dependendo do tamanho da tela do celular.
