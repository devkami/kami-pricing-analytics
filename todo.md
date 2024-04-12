# TO DO

## Próximas Atualizações

### [] Incluir Scraping dos seguintes Marketplaces

- [ ] Amazon SKU = ASIN
- [ ] Mercado Livre
- [ ] Magazine Luiza
- [ ] Raia Drogasil
- [ ] Via Varejo - Casas Bahia
- [ ] Via Varejo - Ponto Frio
- [ ] Via Varejo - Extra
- [ ] Renner
- [ ] Aliexpress
- [ ] Shein

### [] Usar google shopping

### [] quantidade de produtos, quantidades de marketplaces, quantidade de acessos por dia

### [] utilizar postgres para armazenar todas as request executadas na api

## [] Infraestrutura

### [] armazenar todas ´requests´ em um banco postgresql

### [] utilizar estratégica assíncrona para lidar com as request para a pagina no marketplace e para conexão com o banco de dados

### [] utilizar Celery com Redis para lidar com as requisições em estratégia de fila

## Dificuldades técnicas

- Consumir coluna 'sellers' do tipo JSON para análises
- Criar imagem docker da aplicação com ou sem alembic
- Testes de integração usando base de dados postgresql no github actions
- Adicionar id do vendedor no retorno da api
