import pygame, sys, socket, pickle, threading, time

# Inicializa o pygame
pygame.init()

# Configuração da tela
LARGURA_TELA = 800
ALTURA_TELA  = 600

# Cria a janela do pygame
tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption('Space Invaders Multiplayer')

# Carrega as imagens e configurações
BACKGROUND       = pygame.transform.scale(pygame.image.load('multimidia/background.jpeg'), (LARGURA_TELA, ALTURA_TELA))
VELOCIDADE_FUNDO = 3

player_image = pygame.transform.scale(pygame.image.load('multimidia/nave.png'), (50, 50))
alien_image  = pygame.transform.scale(pygame.image.load('multimidia/alien.png'), (50, 50))

# Configuração do socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('192.168.16.212', 5555)

# Configuração do relógio do pygame
clock = pygame.time.Clock()

# Variáveis globais
tiros          = []
tiro_ativo     = False
recebeu_musica = False
Y_FUNDO        = 0

#Inicializa as variáveis do jogo.
def inicializar_jogo():
    global LARGURA_TELA, ALTURA_TELA
    global tela, player_rect, velocidade_jogador, player_image, tiro_ativo, id_cliente, objetivo, qntd_jogadores
    
    # Configuração do jogador
    player_rect         = player_image.get_rect()  # Obtém um retângulo associado à imagem do jogador
    player_rect.centerx = LARGURA_TELA // 2        # Define a posição inicial horizontal do jogador
    player_rect.bottom  = ALTURA_TELA - 10         # Define a posição inicial vertical do jogador (próximo ao fundo da tela)
    tiro_ativo          = False                    # Inicializa a variável que controla se um tiro está ativo ou não
    id_cliente          = None                     # Inicializa o identificador do cliente como nulo
    objetivo            = None                     # Inicializa a variável de objetivo como nula
    qntd_jogadores      = 0                        # Inicializa o contador de jogadores como zero
    velocidade_jogador  = 3                        # Define a velocidade de movimento do jogador

#Desenha os elementos na tela com base no estado atualizado do servidor.
def desenhar_tela(estado_atualizado):
    global tela, player_rect, player_image, alien_image
    
    # Desenha os jogadores na tela
    for jogador_id, info in estado_atualizado['jogadores'].items():
        nave_rect = pygame.Rect(info['posicao'][0] - 25, info['posicao'][1] - 25, 50, 50)
        tela.blit(player_image, nave_rect)

    # Desenha os tiros na tela
    for tiro_pos in estado_atualizado['tiros']:
        pygame.draw.rect(tela, (255, 255, 0), pygame.Rect(tiro_pos[0], tiro_pos[1], 5, 5))

    # Desenha os aliens na tela
    for alien_pos in estado_atualizado['aliens']:
        tela.blit(alien_image, pygame.Rect(alien_pos[0], alien_pos[1], 50, 50))

    # Atualiza a tela
    pygame.display.flip()

#Verifica se o evento de fechar a janela foi acionado.
def verifica_fim_eventos():
    # Itera sobre todos os eventos presentes na fila de eventos do Pygame
    for event in pygame.event.get():
        # Verifica se o tipo do evento é QUIT, indicando que o usuário tentou fechar a janela do jogo
        if event.type == pygame.QUIT:
            # Cria um dicionário contendo o identificador do cliente e o evento de desconexão
            dados_desconectar = {'id': id_cliente, 'evento': 'desconectar'}
            
            # Envia os dados de desconexão para o servidor usando o socket UDP
            client_socket.sendto(pickle.dumps(dados_desconectar), server_address)
            
            # Encerra o Pygame
            pygame.quit()
            
            # Encerra o programa
            sys.exit()

#Atualiza o fundo da tela para criar um efeito de movimento.
def atualizar_fundo():
    global VELOCIDADE_FUNDO, ALTURA_TELA, Y_FUNDO

    # Incrementa a posição vertical do fundo pela velocidade definida
    Y_FUNDO += VELOCIDADE_FUNDO

    # Se o fundo ultrapassou a altura da tela, reinicia sua posição para criar um efeito contínuo
    if Y_FUNDO > ALTURA_TELA:
        Y_FUNDO = 0

    # Desenha duas cópias do fundo, uma sobre a outra, para criar o efeito contínuo
    tela.blit(BACKGROUND, (0, Y_FUNDO))
    tela.blit(BACKGROUND, (0, Y_FUNDO - ALTURA_TELA))

#Processa as atualizações recebidas do servidor.
def processar_atualizacoes_do_servidor():
    while True:
        try:
            # Recebe os dados do servidor através do socket UDP
            data, _ = client_socket.recvfrom(4096)

            # Desserializa os dados utilizando o módulo pickle
            estado_atualizado = pickle.loads(data)

            # Retorna o estado atualizado para ser utilizado no restante do programa
            return estado_atualizado
        except OSError as e:
            pass

#Recebe continuamente o estado atualizado do servidor.
def receber_estado_atualizado_continuamente():
    global id_cliente, player_rect, objetivo, recebeu_musica, qntd_jogadores

    tempo_inicio = time.time()
    while True:
        tempo_decorrido = time.time() - tempo_inicio
        
        if tempo_decorrido < 130:
            if objetivo != 0:
                estado_atualizado = processar_atualizacoes_do_servidor()

                # Atualiza as variáveis do cliente com base no estado do servidor
                id_cliente     = estado_atualizado.get('id', None)
                objetivo       = estado_atualizado.get('objetivo', None)
                nome_musica    = estado_atualizado.get('nome_musica', None)
                qntd_jogadores = estado_atualizado.get('qntd_jogadores', None)
        
                if id_cliente is not None:
                    if 'posicao_jogador' in estado_atualizado:
                        x, y = estado_atualizado['posicao_jogador']
                        player_rect.x = x
                        player_rect.y = y

                # Carrega a música quando o segundo jogador se conecta
                if nome_musica and not recebeu_musica and qntd_jogadores == 2:
                    pygame.mixer.init()
                    time.sleep(0.05)
                    pygame.mixer.music.load(nome_musica)
                    pygame.mixer.music.play(-1)  # -1 indica loop infinito
                    recebeu_musica = True

                # Desenha a tela com base no estado atualizado
                desenhar_tela(estado_atualizado)
            else:
                # Exibe mensagem de vitória e encerra o jogo
                mensagem_final = pygame.font.Font(None, 74).render("PARABÉNS", True, (0, 255, 0))
                tela.blit(mensagem_final, (LARGURA_TELA // 2 - 150, ALTURA_TELA // 2 - 30))
                pygame.mixer.music.stop()
                pygame.display.flip()
                time.sleep(3)  # Aguarda 3 segundos para a mensagem ser exibida
                pygame.quit()
                dados_desconectar = {'id': id_cliente, 'evento': 'desconectar'}
                client_socket.sendto(pickle.dumps(dados_desconectar), server_address)
                sys.exit()
        else:
            # Exibe mensagem de derrota e encerra o jogo
            mensagem_final = pygame.font.Font(None, 74).render("GAME-OVER", True, (255, 0, 0))
            tela.blit(mensagem_final, (LARGURA_TELA // 2 - 150, ALTURA_TELA // 2 - 30))
            pygame.mixer.music.stop()
            pygame.display.flip()
            time.sleep(3)  # Aguarda 3 segundos para a mensagem ser exibida
            pygame.quit()
            sys.exit()

#Move o jogador com base nas teclas pressionadas.       
def mover_jogador():
    global LARGURA_TELA, ALTURA_TELA, player_rect, velocidade_jogador
    
    # Obtém o estado das teclas pressionadas
    keys = pygame.key.get_pressed()

    # Move o jogador para a esquerda se a tecla esquerda estiver pressionada e a posição não ultrapassar a borda esquerda
    if keys[pygame.K_LEFT] and player_rect.left > 0:
        player_rect.x -= velocidade_jogador

    # Move o jogador para a direita se a tecla direita estiver pressionada e a posição não ultrapassar a borda direita
    if keys[pygame.K_RIGHT] and player_rect.right < LARGURA_TELA:
        player_rect.x += velocidade_jogador

    # Move o jogador para cima se a tecla para cima estiver pressionada e a posição não ultrapassar a borda superior
    if keys[pygame.K_UP] and player_rect.top > 0:
        player_rect.y -= velocidade_jogador

    # Move o jogador para baixo se a tecla para baixo estiver pressionada e a posição não ultrapassar a borda inferior
    if keys[pygame.K_DOWN] and player_rect.bottom < ALTURA_TELA:
        player_rect.y += velocidade_jogador

#Envia eventos de tiro para o servidor com base nas teclas pressionadas.
def disparar_tiro(keys):
    global client_socket, server_address, id_cliente, player_rect, tiro_ativo

    # Verifica se a tecla de espaço está pressionada
    if keys[pygame.K_SPACE]:
        # Verifica se não há um tiro ativo (para evitar disparos contínuos)
        if not tiro_ativo:
            # Cria um dicionário com informações sobre o tiro e envia ao servidor
            dados_tiro = {'id': id_cliente, 'evento': 'tiro', 'posicao': (player_rect.centerx, player_rect.top)}
            tiro_ativo = True
            client_socket.sendto(pickle.dumps(dados_tiro), server_address)
    else:
        # Define que não há um tiro ativo quando a tecla de espaço é liberada
        tiro_ativo = False

#Atualiza o contador de objetivos e o contador de tempo na tela.
def atualizar_contador(objetivo, tempo_decorrido):
    contador_fonte = pygame.font.Font(None, 36)

    # Desenha o contador de aliens eliminados
    contador_texto = contador_fonte.render(f"Objetivo: {objetivo}", True, (255, 255, 255))
    tela.blit(contador_texto, (10, 10))

    # Desenha o contador do tempo no canto superior direito
    minutos, segundos = divmod(int(tempo_decorrido), 60)
    contador_texto = contador_fonte.render(f"{minutos:02d}:{segundos:02d}", True, (255, 255, 255))
    tela.blit(contador_texto, (LARGURA_TELA - 120, 10))

#Loop principal 
def main_loop():
    global id_cliente, objetivo, qntd_jogadores
     
    # Pequena pausa para garantir que as threads estejam iniciadas
    time.sleep(0.0001)
    
    # Inicia a thread para receber atualizações do servidor
    thread_atualizacoes = threading.Thread(target=receber_estado_atualizado_continuamente)
    thread_atualizacoes.start()

    inicio_jogo = False
    tempo_inicio = time.time()

    while True:
        tempo_decorrido = time.time() - tempo_inicio
            
        # Verifica eventos de encerramento do jogo (por exemplo, fechar a janela)
        verifica_fim_eventos()
        
        keys = pygame.key.get_pressed()

        atualizar_fundo()
        mover_jogador()
        disparar_tiro(keys)

        # Se pelo menos dois jogadores estão conectados ou o jogo já começou
        if qntd_jogadores == 2 or inicio_jogo:
            # Atualiza o contador de aliens eliminados e o tempo decorrido
            atualizar_contador(objetivo, tempo_decorrido)
            inicio_jogo = True

        # Envia a posição do jogador para o servidor
        dados_jogador = {'id': id_cliente, 'evento': 'movimento', 'posicao': (player_rect.x, player_rect.y)}
        client_socket.sendto(pickle.dumps(dados_jogador), server_address)

        # Pequena pausa para controlar a taxa de atualização do loop
        time.sleep(0.0001)
        clock.tick(60)

if __name__ == "__main__":
    inicializar_jogo()
    main_loop()
