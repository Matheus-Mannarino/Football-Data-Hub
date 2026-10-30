"use strict";

const dadosJogadores = document.getElementById("dados-jogadores");

if (dadosJogadores) {
    const jogadores = JSON.parse(dadosJogadores.textContent);

    function normalizar(texto) {
        return texto
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .toLowerCase()
            .trim();
    }

    document.querySelectorAll(".seletor-jogador").forEach((grupo) => {
        const busca = grupo.querySelector(".busca-jogador");
        const clube = grupo.querySelector(".filtro-clube");
        const posicao = grupo.querySelector(".filtro-posicao");
        const select = grupo.querySelector(".opcoes-jogador");
        const quantidade = grupo.querySelector(".quantidade-opcoes");

        function atualizarOpcoes() {
            const selecionado =
                select.value || grupo.dataset.selecionado;

            const termo = normalizar(busca.value);

            const filtrados = jogadores.filter((jogador) => {
                const correspondeNome = normalizar(
                    jogador.nome
                ).includes(termo);

                const correspondeClube =
                    !clube.value
                    || jogador.clubes.includes(Number(clube.value));

                const correspondePosicao =
                    !posicao.value
                    || jogador.posicao === posicao.value;

                return (
                    correspondeNome
                    && correspondeClube
                    && correspondePosicao
                );
            });

            const placeholder = new Option(
                filtrados.length
                    ? "Selecione"
                    : "Nenhum jogador encontrado",
                ""
            );

            select.replaceChildren(placeholder);

            filtrados.forEach((jogador) => {
                const opcao = new Option(
                    `${jogador.nome} — ${jogador.posicao}`,
                    String(jogador.id)
                );

                select.add(opcao);
            });

            const manterSelecao = filtrados.some(
                (jogador) => String(jogador.id) === selecionado
            );

            select.value = manterSelecao ? selecionado : "";
            grupo.dataset.selecionado = select.value;

            quantidade.textContent =
                `${filtrados.length} jogadores encontrados.`;
        }

        busca.addEventListener("input", atualizarOpcoes);
        clube.addEventListener("change", atualizarOpcoes);
        posicao.addEventListener("change", atualizarOpcoes);

        select.addEventListener("change", () => {
            grupo.dataset.selecionado = select.value;
        });

        atualizarOpcoes();
    });
}

const containerGrafico = document.getElementById("grafico-comparacao");
const dadosGrafico = document.getElementById("dados-grafico");

if (containerGrafico && dadosGrafico) {
    const indicadores = JSON.parse(dadosGrafico.textContent);

    const formatador = new Intl.NumberFormat("pt-BR", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    });

    containerGrafico.replaceChildren();

    indicadores.forEach((indicador) => {
        const secao = document.createElement("section");
        secao.className = "indicador-grafico";

        const titulo = document.createElement("h3");
        titulo.textContent = indicador.rotulo;

        secao.appendChild(titulo);

        const maiorValor = Math.max(
            0,
            ...indicador.valores.map((item) => item.valor ?? 0)
        );

        indicador.valores.forEach((item, indice) => {
            const linha = document.createElement("div");
            linha.className = "linha-grafico";

            const rotulo = document.createElement("div");
            rotulo.className = "rotulo-barra";

            const nome = document.createElement("span");
            nome.textContent = item.nome;

            const valor = document.createElement("strong");
            valor.textContent = item.valor === null
                ? "Não disponível"
                : formatador.format(item.valor);

            rotulo.append(nome, valor);

            const trilho = document.createElement("div");
            trilho.className = "trilho-barra";
            trilho.setAttribute("aria-hidden", "true");

            const barra = document.createElement("div");
            barra.className =
                `barra-jogador cor-jogador-${indice + 1}`;

            const largura = maiorValor > 0 && item.valor !== null
                ? (item.valor / maiorValor) * 100
                : 0;

            barra.style.width = `${largura}%`;

            trilho.appendChild(barra);
            linha.append(rotulo, trilho);
            secao.appendChild(linha);
        });

        containerGrafico.appendChild(secao);
    });
}