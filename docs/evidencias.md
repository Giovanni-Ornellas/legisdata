# Evidências para Relatório e Apresentação

Use este roteiro para gerar capturas de tela consistentes da Parte 4.

## Telas recomendadas

| Tela | O que destacar | Relação com o trabalho |
|---|---|---|
| Visão Geral | Totais de proposições, deputados, partidos, temas, tramitações e autorias | Demonstra conexão com o banco e visão agregada |
| Qualidade dos Dados | Cobertura temática, autoria e tramitação | Demonstra análise crítica da carga de dados |
| Entenda uma Proposição | Resumo, autores, temas e linha do tempo | Mostra exploração didática de um registro |
| Ranking de Partidos | Gráfico e tabela de partidos | Usa consulta da Parte 3 com múltiplos JOINs e agregação |
| Ranking de Deputados | Deputados com mais proposições assinadas | Usa autoria em `Participa` |
| Proposições e Temas | Proposições sem tema preservadas | Demonstra uso de `LEFT JOIN` |
| Última Tramitação | Situação e órgão da movimentação mais recente | Usa subconsulta para última tramitação |
| Temas Acima da Média | Temas mais recorrentes | Usa agregação, `HAVING` e subconsulta |
| Tramitações Acima da Média | Proposições mais movimentadas | Usa agregação, `HAVING` e subconsulta |
| Órgãos | Ranking de órgãos e proposições associadas | Aproveita `Orgao` e `Tramitacao` |
| Glossário | Termos legislativos explicados | Demonstra foco em usuário leigo |

## Comandos úteis

Validar dados gerais:

```bash
python scripts/validar_banco.py
```

Validar consultas da Parte 3:

```bash
python scripts/validar_consultas_parte3.py
```

Executar a aplicação:

```bash
streamlit run app.py
```

## Dica para apresentação

Antes de capturar as telas, selecione filtros simples, como ano, tipo de proposição ou tema. Isso torna as tabelas menores e facilita explicar o resultado.
