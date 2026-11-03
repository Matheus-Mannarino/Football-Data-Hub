# Football Data Hub — Home

Copie a pasta backend deste pacote para a raiz do seu repositório, mesclando as pastas. Apenas home.html substitui um arquivo existente; os outros três arquivos são novos. O template base e as outras páginas permanecem iguais.

Execute no ambiente virtual habitual, dentro de backend:

    python manage.py check
    python manage.py runserver

Abra a Home e pressione Ctrl+F5. Confira os links dos clubes, das partidas e dos atalhos. Reduza a janela para conferir o layout mobile.

Arquivos:
- templates/core/home.html: estrutura da Home.
- templates/core/partials/home_partida.html: cartão compartilhado pelos resultados e próximos jogos.
- static/core/css/home.css: estilos exclusivos da Home.
- static/core/js/home.js: oculta escudos que não carregarem, mantendo o nome do clube visível.

Não precisa alterar views, models, URLs, settings ou PostgreSQL. A view atual já carrega os clubes relacionados às partidas.

A Home mantém os cinco resultados e cinco próximos jogos fornecidos pela view, as contagens e o aviso de partidas adiadas. Os jogadores aparecem somente na contagem e no atalho, sem fotos.

Verificado: Django check, renderização com partidas, placar zero, escudos presentes e ausentes, listas vazias e temporada ausente; sintaxe JavaScript. O PostgreSQL real e o layout no navegador devem ser conferidos localmente.
