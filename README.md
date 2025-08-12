# webcrawler

## Escopo inicial

Obter dados de titulos em oferta nas lojas da playstation store, microsoft store e steam com o webdriver
selenium e beautifulsoup agendados com o airflow

## Dia 1(12/08/2025) o que consegui fazer e o que estou encarando ate o momento

### sucesso ate as 13:46
Consegui fazer a primeira etapa de crawling e scrapping da sony e microsoft para entao implementar
a navegacao entre as paginas e pegar mais itens. Criei classe base de logging para poder
registrar no banco de dados os logs das ferramentas de crawling, foi criado o handler do psql
criei esqueleto da rest api responsavel por enviar e receber os dados assim como os schemas pydantic, criei tambem o docker compose com criacao do banco de dados por shell script e esqueleto da API.

### Desafio ate as 13:46
A pagina de promocoes da steam tem classes dinamicas ou seja estou tendo de procurar algo
estatico para obter os ids dos jogos.

### Proximos passos as 13:46
progarmar as dags do airflow para utilizarem as ferramentas de crawling