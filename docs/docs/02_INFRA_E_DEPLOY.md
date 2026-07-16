# Infraestrutura e Deploy

O App Joãozinho não roda direto no computador. Ele foi projetado para rodar na nuvem em um ambiente isolado chamado **Container**. 

Nós utilizamos o **Docker** e o **Docker Compose** para orquestrar tudo.

## O Papel do Docker

Pense no Docker como caixas isoladas (containers) onde o seu aplicativo roda. Isso garante que o app vai funcionar exatamente da mesma forma no seu computador local e no servidor em nuvem (VPS).

O nosso projeto é dividido em três "caixas":
1. **app_baby_routine:** Onde roda o servidor Python (FastAPI).
2. **web_baby_routine:** Onde roda um servidor web (Nginx) que serve a interface visual (Frontend).
3. **docs (opcional):** Onde roda o Docusaurus com essa documentação que você está lendo.

## O Docker Compose

Existe um arquivo chamado `docker-compose.yml` na raiz do projeto. Ele é o maestro da orquestra. É ele quem diz:
- Quais imagens usar para cada caixa.
- Quais portas de rede conectar (ex: Porta 80 para a web, porta 8000 para a API).
- Quais **Volumes** salvar.

### Volumes (Persistência de Dados)
Como containers são efêmeros (se desligar, perdem tudo), o `docker-compose.yml` mapeia pastas do seu servidor físico (ex: `./data`) para dentro do container. É por isso que o seu banco de dados `baby_routine.db` não é apagado quando você reinicia o servidor!

## A VPS e o Deploy

Quando enviamos atualizações para o ar, a sequência clássica no servidor Linux (VPS) é:

```bash
# 1. Baixar as novidades do código (geralmente via git ou copiando arquivos)
cd ~/app-john
git pull

# 2. Reconstruir a imagem do Python caso a gente tenha instalado bibliotecas novas
docker compose build

# 3. Derrubar os containers velhos e subir as versões novas (tudo em background)
docker compose up -d
```

### Let's Encrypt e HTTPS
O servidor também contém uma pasta `letsencrypt/` que lida com a emissão do certificado SSL. Isso garante que, quando você acessa o seu aplicativo pelo celular, a comunicação seja criptografada e o botãozinho de "Cadeado" apareça no navegador, permitindo instalar o aplicativo na tela inicial do celular com segurança (PWA).
