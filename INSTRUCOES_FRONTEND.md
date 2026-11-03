# Football Data Hub — base e navegação

Este pacote contém somente os 13 arquivos novos ou alterados desta etapa, mantendo os caminhos do repositório.

## Aplicação

1. Faça um commit do estado atual do seu projeto para poder voltar a ele.
2. Extraia o ZIP e copie a pasta `backend` para a raiz do Football-Data-Hub, aceitando substituir os nove templates. Mescle as pastas; não apague o backend existente.
3. No terminal, na pasta `backend`, execute `python manage.py check` e `python manage.py runserver` no ambiente virtual habitual.
4. Abra as páginas e recarregue com Ctrl+F5 para atualizar os arquivos estáticos.

Não são necessárias alterações no PostgreSQL, migrations, views, URLs ou settings.

## Estrutura

- `backend/core/templates/core/base.html`: estrutura compartilhada, menu, rodapé e blocos `title`, `content`, `extra_css` e `extra_js`.
- `backend/core/static/core/css/base.css`: paleta, tipografia, estrutura e estilos comuns.
- `backend/core/static/core/js/base.js`: menu responsivo com estado acessível, Escape e ajuste ao redimensionar a janela. Sem JavaScript, os links permanecem disponíveis.
- `backend/core/static/core/img/logo.png`: logo original. O CSS enquadra o espaço transparente para exibi-la no cabeçalho.
- Nove templates: passam a herdar a base. Os dados, formulários, links e paginação permanecem nos templates de origem. As tabelas têm contêineres com rolagem horizontal.

O menu principal contém Home, Classificação, Partidas, Jogadores, Comparação e Sobre. As páginas de detalhes continuam acessíveis pelos links existentes. Detalhe do clube destaca Classificação; detalhe da partida destaca Partidas; detalhe do jogador destaca Jogadores.

## Verificação

- `manage.py check`: sem problemas.
- Renderização dos nove templates pelo Django com contextos de exemplo: aprovada.
- Uma única região principal e um item ativo por página: verificados.
- Sintaxe do JavaScript: aprovada com `node --check`.
- O banco PostgreSQL do projeto não está disponível neste ambiente. Valide localmente as consultas e os fluxos com dados reais.
- A revisão visual no navegador e a interação mobile precisam ser conferidas localmente.

Nesta etapa, as páginas recebem apenas os estilos comuns. O próximo passo é trabalhar o layout específico da Home e depois as demais páginas.
