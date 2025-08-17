# webcrawler

## Como rodar o projeto e links de cada coisa

Necessario docker e docker compose e rodar o seguinte comando

```
docker compose build crawler-base && docker compose up
```

Caso ocorra algum erro basta desligar servico de postgres que estiver rodando em docker

Apos rodar os links para cada componente sao:

[Airflow ui](localhost:8080/) <br>
[Backends disponiveis](localhost:9000/) <br>
[Streamlit para visualizar os dados](localhost:8501/) <br>

## Escopo inicial

Obter dados de titulos em oferta nas lojas da playstation store, microsoft store e steam com o webdriver com: 

- selenium
- beautifulsoup 
- airflow 
- pydantic 
- fastapi 
- postgres 
- pandas

## Ideia subsequente(Dia 2):

Ver os scores de jogos em alguma base de reviews que foram armazenados no banco de dados e
com o selenium e beautifulsoup4 pegar as reviews

## O que acabei fazendo(Dia 2):

Construi um streamlit para ver os dados para ser mais rapido e dockerizei a aplicacao inteira para ser mais plug-n-play

## Dia 1(12/08/2025) o que consegui fazer e o que estou encarando ate o momento

### sucesso ate as 13:46
Consegui fazer a primeira etapa de crawling e scrapping da sony e microsoft para entao implementar
a navegacao entre as paginas e pegar mais itens. Criei classe base de logging para poder
registrar no banco de dados os logs das ferramentas de crawling, foi criado o handler do psql
criei esqueleto da rest api responsavel por enviar e receber os dados assim como os schemas pydantic, criei tambem o docker compose com criacao do banco de dados por shell script e esqueleto da API.

### Desafio ate as 13:46 -> resolvido 14:04()
A pagina de promocoes da steam tem classes dinamicas ou seja estou tendo de procurar algo
estatico para obter os ids dos jogos.

### Resolvi o desafio acima 14:04
Erros de digitacao e ordenacao de variaveis 

### Proximos passos as 13:46
progarmar as dags do airflow para utilizarem as ferramentas de crawling

## Dia 2 (13/08/2025)

Terminar o steam_tools para acessar as paginas dos jogos, e agora criar o airflow para orquestrar o agendamento, alem disso
criar a imagem customizada do airflow com as libs e psql rodando o script de inicializacao se sobrar tempo criar um streamlit

### Desafios dia 2 (13/08/2025)

Terminei o steam_tools mas as tags sao dinamicas e acabou quebrando, dockerizei tudo e ajustei alteracoes da imagem alem disso fiz um streamlit basico para ver o banco de dados. 

### Proximo passo

Documentar as ferramentas