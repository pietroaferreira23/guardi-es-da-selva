# guardi-es-da-selva
apenas um jogo
Jungle Defense
Protótipo de Tower Defense em Python com Pygame, ambientado em uma selva e protagonizado por macacos defensores. O jogo desenha seus personagens, inimigos, projéteis, efeitos e cenário diretamente pelo código, portanto não precisa de imagens ou arquivos de áudio externos.
Estado do projeto: esta é uma primeira versão jogável em 2D. Ela implementa uma parte das mecânicas planejadas para o projeto maior; não representa ainda o jogo 3D completo descrito no prompt mestre.

Requisitos
- Python 3.10 ou superior.
- Pygame (ou pygame-ce).
- Windows, macOS ou Linux com ambiente gráfico disponível.
Instalação
1. Baixe jungle_defense.py e este README.md para a mesma pasta.
2. Abra um terminal nessa pasta.
3. (Opcional, recomendado) Crie e ative um ambiente virtual:
   Windows (PowerShell):
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   macOS / Linux:
   python3 -m venv .venv
   source .venv/bin/activate
4. Instale a dependência:
   python -m pip install pygame
   Caso python não aponte para Python 3, use python3 -m pip install pygame (macOS/Linux) ou py -m pip install pygame (Windows).
Como executar
Na pasta onde está o arquivo:
python jungle_defense.py
No Windows, também pode ser necessário usar:
py jungle_defense.py
A janela do jogo abre em 1280 × 760 pixels. No menu inicial, clique em JOGAR.
Controles
Ação	Como fazer
Iniciar a próxima onda	Clique em INICIAR ONDA ou pressione Espaço
Escolher um macaco para construir	Clique no botão do macaco no painel à direita
Posicionar o macaco	Clique em um ponto válido da área da selva
Cancelar o posicionamento	Clique com o botão direito ou pressione Esc
Selecionar uma torre já construída	Clique nela com o botão esquerdo
Comprar uma melhoria	Selecione a torre e clique em um dos três caminhos no painel
Vender uma torre	Selecione-a e clique em Vender; o protótipo devolve 70% do investimento registrado
Mudar a prioridade de alvo	Clique no botão Alvo ou pressione T com uma torre selecionada
Pausar / continuar	Clique no botão correspondente ou pressione Esc
Alternar velocidade	Clique em Velocidade; 1 define 1× e 2 define 2×
Fechar o jogo	Feche a janela


A tecla Esc cancela primeiro o posicionamento de uma torre; quando não há posicionamento ativo, alterna a pausa.
O que já está implementado
Partida e defesa
- Uma arena 2D com trilha fixa, vegetação e elementos decorativos desenhados pelo código.
- Ondas de inimigos que aumentam em quantidade e variedade.
- Sistema de vidas, dinheiro da partida, vitória de onda e fim de jogo.
- Inimigos de diferentes cores e resistências, incluindo camuflados, regeneradores e MOABs.
- Inimigos com imunidades específicas, como resistência a explosões, congelamento ou determinados tipos de ataque.
- Projéteis, perfuração, dano, explosões em área, efeitos de lentidão e congelamento.
Macacos e melhorias
O protótipo possui 14 unidades de torre configuradas: Macaco Arqueiro, Macaco de Tachas, Macaco Bumerangue, Macaco Bombardeiro, Macaco Glacial, Macaco Cola-Cola, Macaco Atirador, Macaco Submarino, Macaco Mago, Macaco Ninja, Macaco Alquimista, Fazenda Tropical, Vila dos Macacos e Macaco Engenheiro.
- Torres agrupadas em classes Primária, Militar, Mágica e Suporte.
- Desbloqueio gradual de torres conforme o nível da conta.
- Três caminhos de melhoria por torre, com regras de cruzamento e níveis até Tier 5.
- Atributos de dano, perfuração e alcance exibidos ao selecionar uma torre.
- Prioridades de alvo: Primeiro, Último, Forte e Próximo.
- Bônus de suporte do Alquimista e detecção de camuflagem associada à Vila.
- Fazenda que gera renda ao final das ondas.
- Alcance global para o Atirador e restrições especiais de posicionamento para o Submarino.
Herói
- Um herói arqueiro chamado Kiko Arqueiro.
- Ataque automático contra inimigos não camuflados.
- Evolução automática até o nível 20 durante a partida.
Progressão e salvamento
- XP de conta e níveis permanentes.
- XP individual por tipo de torre, distribuído conforme o investimento em torres daquele tipo ao final das ondas.
- Desbloqueio de melhorias conforme a XP da torre.
- Registro de partidas, vitórias/recordes de onda e inimigos derrotados.
- Salvamento automático do progresso em arquivo JSON.
Salvamento
O jogo cria o arquivo jungle_defense_save.json na mesma pasta de jungle_defense.py. Ele guarda, entre outros dados, nível e XP da conta, torres desbloqueadas, XP das torres e recorde de onda.

Para reiniciar a progressão do zero:
1. Feche o jogo.
2. Apague jungle_defense_save.json.
3. Execute o jogo novamente.
O arquivo de salvamento é criado novamente quando o jogo salvar o progresso.
Regras e limitações desta versão
Esta entrega é um protótipo 2D e não implementa todos os sistemas do documento de design. Em particular, ainda não há:
- Modelos, câmera ou mapas 3D; o visual é desenhado em 2D com formas do Pygame.
- Animações esqueléticas, modelos externos, dublagem ou trilha sonora.
- Todos os macacos, heróis, inimigos, chefes, mapas e melhorias descritos no projeto completo.
- Paragons, editor de mapas, editor de desafios, modo cooperativo ou multiplayer.
- Loja funcional de heróis, compra de skins ou sistema completo de Dinheiro de Macaco.
- Modos CHIMPS, Deflação, Apopalipse, Metade do Dinheiro ou Freeplay completo.
- Sistema completo de obstáculos removíveis e linha de visão dinâmica; há uma área de bloqueio simplificada no mapa.
- Interface de configurações, remapeamento de teclas ou suporte responsivo a diferentes resoluções.
Os preços, atributos, XP e desbloqueios atuais são valores de balanceamento deste protótipo e podem ser alterados diretamente no início de jungle_defense.py, especialmente nos dicionários TOWER_SPECS e BALLOON_TYPES.
Solução de problemas
Erro No module named pygame

Instale o Pygame no mesmo ambiente Python usado para executar o jogo:
python -m pip install pygame
A janela abre e fecha imediatamente

Execute o jogo pelo terminal para visualizar a mensagem de erro. Confira se a versão do Python é 3.10 ou superior e se o Pygame foi instalado no ambiente correto.

O progresso não está sendo salvo

Verifique se a pasta do jogo permite escrita e se jungle_defense_save.json não está bloqueado por outro programa.

O jogo não abre em um servidor sem tela

O Pygame precisa de um ambiente gráfico para criar a janela. Execute em um computador com desktop ou configure um ambiente gráfico compatível.
Estrutura de arquivos
JungleDefense/
├── jungle_defense.py          # Código-fonte do jogo
├── README.md                  # Este guia
└── jungle_defense_save.json   # Criado automaticamente após salvar o progresso
Desenvolvimento
O projeto está concentrado em um único arquivo Python para facilitar a execução inicial. As configurações das torres e dos inimigos ficam nos dicionários TOWER_SPECS e BALLOON_TYPES; as classes Balloon, Projectile, Tower e Game controlam os elementos principais da partida.

Para ampliar o jogo, recomenda-se separar posteriormente os sistemas em módulos (entidades, combate, mapas, interface, progressão e salvamento) e adicionar testes automatizados para economia, dano, melhorias e desbloqueios.
