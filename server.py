import pygame, sys, socket, pickle, threading, random, time

# Inicialização do Pygame
pygame.init()

# Constantes do jogo
LARGURA_TELA          = 800
ALTURA_TELA           = 600
VELOCIDADE_FUNDO      = 3
VELOCIDADE_JOGADOR    = 3
TAXA_CRIACAO_INIMIGO  = 0.01
TEMP_EXPLOSAO_VISIVEL = 30
Y_FUNDO               = 0
OBJETIVO              = 100
EXPLOSAO_VISIBLE      = False
INICIO_JOGO           = False
FRAMES_EXPLOSAO       = 0
QNTD_JOGADORES        = 0

# Lista de tiros, aliens, endereços dos clientes, informações dos jogadores e eventos dos clientes
TIROS                 = []
ALIENS                = []
CLIENT_ADDRESSES      = [] 
PLAYERS               = {}
CLIENT_INFO           = {} 
EVENTOS_CLIENTES      = []

# Configuração da tela
tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption('Space Invaders Multiplayer')

# Carregamento de imagens
BACKGROUND     = pygame.transform.scale(pygame.image.load('multimidia/background.jpeg'), (LARGURA_TELA, ALTURA_TELA))
PLAYER_IMAGE   = pygame.transform.scale(pygame.image.load('multimidia/nave.png'), (50, 50))
INIMIGO_IMAGE  = pygame.transform.scale(pygame.image.load('multimidia/alien.png'), (50, 50))
EXPLOSAO_IMAGE = pygame.transform.scale(pygame.image.load('multimidia/explosao.png'), (70, 70))

# Posição inicial do jogador
PLAYER_RECT         = PLAYER_IMAGE.get_rect()
PLAYER_RECT.centerx = LARGURA_TELA // 2
PLAYER_RECT.bottom  = ALTURA_TELA - 10

# Controle de threads e lock para evitar condições de corrida
LOCK = threading.Lock()

# Configuração do socket do servidor
SERVER_SOCKET  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SERVER_ADDRESS = ('192.168.16.212', 5555)
SERVER_SOCKET.bind(SERVER_ADDRESS)

# Função para receber dados dos clientes em uma thread separada
def receber_dados():
    global EVENTOS_CLIENTES, CLIENT_ADDRESSES

    while True:
        data, address = SERVER_SOCKET.recvfrom(4096)

        #Adiciona o endereço conectado do client à lista
        if address not in CLIENT_ADDRESSES:
            CLIENT_ADDRESSES.append(address)

        #Tenta obter os dados vindos do cliente e adiciona à lista de eventos
        try:
            dados_cliente = pickle.loads(data)
            with LOCK:
                EVENTOS_CLIENTES.append((dados_cliente, address))
                if 'id' in dados_cliente:
                    CLIENT_INFO[address] = dados_cliente['id']
        except pickle.UnpicklingError:
            pass

# Função para gerar o identificador do jogador com base no endereço
def obter_identificador_do_jogador_pelo_endereco(address):
    global CLIENT_ADDRESSES

    for jogador_id, endereco in enumerate(CLIENT_ADDRESSES, start=1):
        if endereco == address:
            return jogador_id
    return None

# Função para desenhar elementos na tela
def desenhar_elementos():
    global tela, PLAYER_IMAGE, PLAYERS, QNTD_JOGADORES

    for jogador_id, info in PLAYERS.items():
        nave_rect = pygame.Rect(info['posicao'][0] - 25, info['posicao'][1] - 25, 50, 50)
        tela.blit(PLAYER_IMAGE, nave_rect)

# Função para enviar o estado atualizado do jogo para um cliente específico
def enviar_estado_atualizado_para_cliente(estado_atualizado, address):
    # Obtém o identificador do jogador com base no endereço
    jogador_id = obter_identificador_do_jogador_pelo_endereco(address)
    
    # Adiciona a lista de jogadores ao estado atualizado
    estado_atualizado['jogadores'] = PLAYERS
    
    # Se o jogador está registrado, adiciona informações específicas dele ao estado
    if jogador_id is not None:
        estado_atualizado['id']             = jogador_id   
        estado_atualizado['tiros']          = list(TIROS)
        estado_atualizado['aliens']         = ALIENS
        estado_atualizado['objetivo']       = OBJETIVO
        estado_atualizado['nome_musica']    = 'multimidia/sound.mp3'
        estado_atualizado['qntd_jogadores'] = QNTD_JOGADORES

        # Serializa o estado atualizado e envia para o cliente
        serialized_data = pickle.dumps(estado_atualizado, protocol=pickle.HIGHEST_PROTOCOL)
        SERVER_SOCKET.sendto(serialized_data, address)

# Função para processar eventos dos clientes
def processar_eventos_clientes():
    global PLAYERS, EVENTOS_CLIENTES, QNTD_JOGADORES

    # Itera sobre os eventos recebidos dos clientes
    for evento_cliente, address in EVENTOS_CLIENTES:
        jogador_id  = evento_cliente.get('id', None)
        tipo_evento = evento_cliente.get('evento', None)
        
        # Verifica se o evento é relacionado a um jogador
        if jogador_id is not None:
            # Se o jogador ainda não está na lista de jogadores, adiciona-o
            if jogador_id not in PLAYERS:
                PLAYERS[jogador_id] = {'posicao': (LARGURA_TELA // (len(PLAYERS) + 1), ALTURA_TELA - 10)}
                print(f"Conexão estabelecida - ID Jogador: {jogador_id}, Endereço: {address}")
                QNTD_JOGADORES += 1

            # Atualiza a posição do jogador em caso de evento de movimento
            if tipo_evento == 'movimento':
                PLAYERS[jogador_id]['posicao'] = evento_cliente['posicao']

            # Cria uma rajada de tiros caso o evento seja de tiro
            elif tipo_evento == 'tiro':
                criar_rajada_tiros(evento_cliente['posicao'])

            # Realiza a desconexão do jogador caso o evento seja de desconexão
            elif tipo_evento == 'desconectar':
                if jogador_id in PLAYERS:
                    print(f"Desconexão - ID Jogador: {jogador_id}, Endereço: {address}")
                    del PLAYERS[jogador_id]
                    QNTD_JOGADORES -= 1
                    if address in CLIENT_ADDRESSES:
                        CLIENT_ADDRESSES.remove(address)

    # Limpa a lista de eventos, pois todos foram processados
    EVENTOS_CLIENTES = []

# Função para criar uma rajada de tiros
def criar_rajada_tiros(posicao):
    global TIROS

    for i in range(5):
        TIROS.append(pygame.Rect(posicao[0], posicao[1] - i * 10, 5, 5))

# Função para criar um novo alien
def criar_alien():
    # Adiciona um novo alien à lista de aliens, de forma aleatória
    ALIENS.append(pygame.Rect(random.randint(0, LARGURA_TELA - 50), 0, 50, 50))

# Função para mover e desenhar tiros na tela
def mover_desenhar_tiros():
    global TIROS, PLAYERS

    # Itera sobre os jogadores e seus tiros
    for jogador_id, info in PLAYERS.items():
        for tiro in TIROS:
            # Cria um retângulo representando o tiro
            tiro_rect    = pygame.Rect(tiro[0], tiro[1], 5, 5)
            # Move o retângulo para cima (simulando o movimento do tiro)
            tiro_rect.y -= 8
            # Desenha o tiro na tela com uma cor amarela
            pygame.draw.rect(tela, (255, 255, 0), tiro_rect)

# Função para remover tiros fora da tela
def remover_tiros_fora_tela():
    global TIROS

    TIROS = [(tiro[0], tiro[1] - 8) for tiro in TIROS if tiro[1] > 0]

# Função para mover e desenhar aliens na tela
def mover_desenhar_aliens():
    global ALIENS

    # Itera sobre cada alien na lista de aliens
    for alien in ALIENS:
        # Move o alien para baixo, simulando seu movimento na tela
        alien.y += 5
        # Desenha o alien na tela utilizando a imagem carregada
        tela.blit(INIMIGO_IMAGE, alien)

    # Remove aliens que estão fora da tela
    remover_aliens_fora_tela()

# Função para remover aliens fora da tela
def remover_aliens_fora_tela():
    global ALIENS

    ALIENS = [alien for alien in ALIENS if alien.top < ALTURA_TELA]

# Função para verificar colisão entre tiro e alien
def colisao_tiro_alien(tiro_rect, alien):
    # Usa o método colliderect() para verificar se há uma colisão entre o tiro e o alien
    return tiro_rect.colliderect(alien)

# Função para verificar e lidar com colisão entre tiro e alien
def verificar_colisao_tiro_alien():
    global TIROS, ALIENS, EXPLOSAO_VISIBLE, FRAMES_EXPLOSAO, OBJETIVO, INICIO_JOGO

    # Itera sobre todos os tiros em TIROS
    for tiro_rect_tuple in TIROS:
        # Cria um retângulo representando a posição do tiro
        tiro_rect = pygame.Rect(tiro_rect_tuple[0], tiro_rect_tuple[1], 5, 5)
        
        # Itera sobre todos os aliens em ALIENS
        for alien in ALIENS:
            # Verifica se há colisão entre o tiro e o alien
            if colisao_tiro_alien(tiro_rect, alien):
                # Exibe uma explosão na posição do alien atingido
                tela.blit(EXPLOSAO_IMAGE, alien)
                EXPLOSAO_VISIBLE = True
                FRAMES_EXPLOSAO  = 0

                # Reduz o objetivo do jogo, se não for zero
                if OBJETIVO != 0:
                    OBJETIVO  -= 1

                # Remove o tiro e o alien da lista
                TIROS.remove(tiro_rect_tuple)
                ALIENS.remove(alien)

# Função para criar novos aliens com base em uma taxa de criação
def criar_novos_aliens():
    global TAXA_CRIACAO_INIMIGO

    # Gera um número aleatório entre 0 e 1
    if random.random() < TAXA_CRIACAO_INIMIGO:
        # Chama a função criar_alien se o número gerado for menor que a taxa de criação
        criar_alien()

# Função principal do jogo
def main():
    global EXPLOSAO_VISIBLE, FRAMES_EXPLOSAO, EVENTOS_CLIENTES, INICIO_JOGO, OBJETIVO

    # Inicia a thread para receber dados dos clientes
    thread_receber = threading.Thread(target=receber_dados)
    thread_receber.start()

    # Tempo de início do jogo
    tempo_inicio   = time.time()
    clock          = pygame.time.Clock()
    end_game_font  = pygame.font.Font(None, 74)

    print("Iniciando servidor...\nAguardando conexões...")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        with LOCK:
            TIROS = [] 
            processar_eventos_clientes()

            if OBJETIVO == 0:
                OBJETIVO = 100

            # Verifica se há pelo menos dois clientes conectados ou o jogo já começou
            if len(CLIENT_ADDRESSES) >= 2 or INICIO_JOGO:
                if time.time() - tempo_inicio < 10000:  # Tempo máximo de jogo (10 segundos)
                    # Lógica principal do jogo enquanto está ativo
                    mover_desenhar_tiros()
                    remover_tiros_fora_tela()
                    mover_desenhar_aliens()
                    remover_aliens_fora_tela()
                    verificar_colisao_tiro_alien()
                    criar_novos_aliens()
                    INICIO_JOGO = True

                    # Envia o estado atualizado para cada cliente
                    for address in CLIENT_ADDRESSES:
                        enviar_estado_atualizado_para_cliente({
                            'jogadores': PLAYERS,
                            'tiros': TIROS,  # Adiciona a lista de tiros do servidor
                            'aliens': ALIENS, # Adiciona a lista de aliens do servidor
                            'objetivo':OBJETIVO, #Passa o objetivo atual para a tela do cliente
                            'qntd_jogadores': QNTD_JOGADORES 
                        }, address)
                else:
                    # Exibe tela de game over quando o tempo limite é atingido
                    tela.fill((0, 0, 0)) 
                    game_over_text = end_game_font.render("Tempo Esgotado", True, (255, 0, 0))
                    tela.blit(game_over_text, (LARGURA_TELA // 2 - 150, ALTURA_TELA // 2 - 30))
                    pygame.display.flip()

        time.sleep(0.01)
        clock.tick(60)

if __name__ == "__main__":
    main()
