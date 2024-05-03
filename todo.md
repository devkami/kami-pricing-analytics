# TO DO

## Próximas Atualizações

### [] Incluir Scraping dos seguintes Marketplaces

- [x] Amazon SKU = ASIN
- [x] Mercado Livre
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

### [x] utilizar postgres para armazenar todas as request executadas na api

### [x] utilizar estratégica assíncrona para lidar com as request para a pagina no marketplace e para conexão com o banco de dados

### [] utilizar Celery com Redis para lidar com as requisições em estratégia de fila

### [] adicionar tratamento de paginação (principalmente no mercado livre)

### [] adicionar método get à API

### [] implementar funções de recuperação da informação através do storage

### [] implementar um algoritmo inteligente para o get retornar dados do banco de dados de acordo com a última pesquisa, ou realizar uma pesquisa caso a validade da última pesquisa tenha expirado, ou não for encontrado nenhum registro para aquele produto no banco