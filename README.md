# 🚀 Space Invaders Multiplayer 👾 
Este projeto foi desenvolvido como requisito avaliativo da disciplina "CET098 - REDE DE COMPUTADORES I" do curso de Ciência da Computação - Universidade Estadual de Santa Cruz.

Nesta versão do famoso arcade game 2D "Space Invaders", dois players se reunem utilizando uma rede local para combater os aliens antes que o tempo acabe. A vitória é alcançada quando os jogadores eliminam 100 inimigos em 2 minutos.     

O jogo está implementado em linguagem Python utilizando o protocolo de comunicação UDP. Para a transmissão de dados entre as partes cliente - servidor são utilizadas, principalmente, três bibliotecas: Socket, Threading e Pickle. 

### 📌Sobre este projeto:
1.  Software
    - [Objetivos e motivações.](#)
    - [Escolhendo o protocolo.](#)
    - [Estrutura do código](#Estrutura-do-código.)
2.  Protocolo usado na camada de aplicação
    - [Estados](#)
    - [Mensagens](#)
    - [Eventos](#)

3. Como jogar
   - [Requisitos](#)
   - [Instruções de instalação](#)
   - [Controles](#)  


![imagem](<Imagem do WhatsApp de 2023-12-04 à(s) 23.09.38_52090821.jpg>)

## Software 🛠
Entendendo um pouco sobre o funcionamento do código e a sua estrutura.
### Objetivos e motivações.
O jogo de shooting "Space Invaders" é bem querido na comunidade gamer, optamos por criar uma versão ainda mais divertida e interativa utilizando uma conexão local para conectar dois jogadores. O principal foco, entretanto, foi o aprendizado dos conceitos abordados durante o estudo da disciplina de Redes. Principalmente o gereciamento da comunicação de dados entre um cliente e um servidor utilizando um protocolo apropriado. Desta maneira, é esperado que o software seja capaz de lidar com o envio e recebimentos de dados atualizando a execução do jogo nas partes envolvidas a cada evento ocorrido. 

### Escolhendo o protocolo.
O protocolo utilizado na implementação foi o UDP (User Datagram Protocol). Durante a escolha buscamos analisar as considerações específicas do projeto. O UDP foi preferido devido à sua simplicidade e eficiência em ambientes nos quais a perda ocasional de pacotes é aceitável. No contexto de um jogo multiplayer, a velocidade de transmissão é crucial para manter a jogabilidade fluida em tempo real, e o UDP, por ser um protocolo não orientado a conexão e de baixa sobrecarga, permite uma comunicação mais rápida do que protocolos mais robustos, como o TCP. Embora o UDP não garanta a entrega de pacotes, percebemos que isso não afeta em grande escala a jogabilidade do jogo.

### Estrutura do código.
O código está dividido em dois arquivos:
- `server.py` lida com a implementação do servidor.
- `client.py` lida com a implementação do cliente. 

O fluxo do programa segue os seguintes passos: 
- Conexão Inicial:
O jogo é inicializado com a execução do código server, que prepara o ambiente e aguarda conexões de clientes. 
Os clientes são jogadores individuais que se conectam com o server através de sockets UDP, estabelecendo a comunicação.

- Cada jogador conectado controla a sua própia nave e pode observar os movimentos realizados pelo outro jogador conectado. 
Os jogadores precisam eliminar uma quantidade determinada de inimigos em um limite de tempo para vencer. 

- A comunicação entre clientes e o servidor é realizada por meio de troca de mensagens usando a biblioteca de serialização Pickle em Python.
Os cliente enviam informações ao servidor sobre seus eventos como: movimentação, tiros ou kills feitas. O servidor então, envia atualizações do estado do jogo. 

- O jogo possui alguns feedbacks visuais e sonoros, como: Um inimigo ao morrer dispara uma animação de explosão. O jogo ao ser iniciado reproduz uma música de fundo. 
 
## Sobre o protocolo usado na camada de aplicação
O protocolo na camada de aplicação se baseia em uma comunicação cliente-servidor utilizando sockets UDP em Python. Cada entidade (cliente e servidor) possui um socket dedicado para a troca de mensagens. As informações são transmitidas na forma de objetos serializados, empregando a biblioteca `Pickle` ou strings conforme o contexto.


### Estados
A lógica de comunicação segue um modelo no qual o cliente envia eventos (movimentos e tiros) para o servidor. Este, por sua vez, processa essas ações e responde com o estado atualizado do jogo. Essa comunicação é realizada por meio de datagramas, garantindo uma troca de dados leve e adequada para jogos em tempo real.

Ao ser iniciado, o servidor espera conexões dos clientes, gerenciando várias instâncias de jogadores por meio de um dicionário identificado pelos respectivos endereços. Para cada jogador é atribuído um identificador único fornecido pelo servidor.

A lógica de atualização no servidor abrange a movimentação dos jogadores, disparo de tiros, criação de aliens, detecção de colisões e a contagem do objetivo a ser alcançado. O estado atualizado do jogo, contendo informações sobre o andar do jogo, é enviado de volta individualmente para cada cliente.

Ambos, cliente e servidor, implementam threads para executar tarefas simultâneas, como a recepção contínua de dados do cliente ou o processamento de atualizações do servidor.

### Eventos 
1.  Registro do Jogador.
    -   **Cliente para Servidor:** Quando um cliente inicia sua participação no jogo, envia uma mensagem solicitando o registro ao servidor. Esta mensagem não contém um 'id' associado, indicando ao servidor que o cliente está se registrando pela primeira vez.
    -   **Servidor para Cliente:** Em resposta, o servidor atribui um 'id' único ao jogador e fornece a posição inicial. Isso estabelece a identidade do jogador e inicia a troca de informações.
2. Movimento do Jogador.
   - **Cliente para Servidor:** Quando o jogador se move, uma mensagem informando a nova posição é enviada ao servidor. A inclusão do 'id' garante que o servidor possa associar corretamente a mensagem à entidade específica.
3. Disparo de Tiro.
   - **Cliente para Servidor:** Quando um jogador dispara, uma mensagem é enviada ao servidor indicando a intenção. A posição inicial do tiro é crucial para determinar a origem e a trajetória do projétil.
4. Atualização do Estado do Jogo.
   - **Servidor para Cliente:** Periodicamente, o servidor envia mensagens de atualização para cada cliente, contendo informações sobre jogadores, tiros, aliens e o objetivo atual. A inclusão do 'id' garante que cada cliente receba as informações pertinentes ao seu contexto.    
5. Alien Eliminado.
   - **Servidor para cliente:** O servidor remove o alien eliminado da lista de aliens ativos, atualiza a pontuação do jogador e o objetivo atual do jogo. Uma mensagem de atualização do estado é enviada a todos os clientes.
 

### Mensagens
O protocolo adota uma estrutura comum para todas as mensagens, baseada em um dicionário Python serializado por meio do módulo pickle. A inclusão de campos como 'id', 'evento' e 'posicao' fornece uma base sólida para identificação, categorização e localização espacial das entidades no jogo.
  #### Mensagens do cliente para o servidor:
- Mover a nave do Jogador:

```py
{
 'id': ID_DO_JOGADOR,
 'evento': 'movimento',
 'posicao': (X, Y)
}
```
- Disparar o Tiro:
```py
 {
 'id': ID_DO_JOGADOR,
 'evento': 'tiro',
 'posicao': (X, Y)
}
```
  #### Mensagens do servidor para o cliente:
- Mensagem de Atualização do Estado: 
```py
{
 'jogadores': {
    ID_JOGADOR_1: {'posicao': (X, Y)},
    ID_JOGADOR_2: {'posicao': (X, Y)},
    ...
 },
    'tiros': [(X1, Y1), (X2, Y2), ...],
    'aliens': [(X1, Y1), (X2, Y2), ...],
    'objetivo': OBJETIVO_ATUAL
}
```
#### Estabelecimento da Conexão:
- Criação de Sockets:
```
Tanto o cliente quanto o servidor criam sockets UDP, usando socket.socket(socket.AF_INET, socket.SOCK_DGRAM).
```
- Definição do Endereço e Porta do Servidor:
```
Ambos especificam o endereço IP e a porta do servidor a qual querem se conectar 
utilizando a variável server_address = ('192.168.0.104', 5555).

```
- Vinculação do Socket à Porta (Apenas Servidor):
```
O servidor vincula o socket criado ao endereço escolhido com SERVER_SOCKET.bin (SERVER_ADDRESS).
```
- Envio de Dados do Cliente para o Servidor:
```
O cliente envia dados serializados para o servidor utilizando client_socket.sendto(pickle.dumps(dados), server_address).
```
- Recebimento de Dados no Servidor:
```
O servidor recebe dados do cliente com: data, address = 
SERVER_SOCKET.recvfrom(4096).
```
- Processamento dos Dados no Cliente e no Servidor:
```
Tanto o cliente quanto o servidor desserializam os dados recebidos utilizando 
pickle.loads(data).
```
- Atualização da Interface Gráfica ou Lógica do Jogo:
```
Ambos atualizam a interface gráfica ou a lógica do jogo com base nos dados recebidos.
```
- Envio de Dados Atualizados para os Clientes:
```
O servidor envia dados atualizados para os clientes com: SERVER_SOCKET.sendto(serialized_data, address).
```
- Thread para Receber Dados no Servidor:
```
O servidor utiliza uma thread separada (thread_receber) para receber continuamente 
dados dos clientes
```
- Tratamento de Eventos e Lógica do Jogo:
```
Ambos, cliente e servidor, realizam o processamento de eventos e a atualização da 
lógica do jogo
```
- Compartilhamento de Dados entre Threads (Apenas Servidor):
```
O servidor utiliza um mecanismo de trava (LOCK) para garantir a consistência ao 
acessar dados compartilhados entre threads.
```
- Serialização e Desserialização:
```
Ambos utilizam o módulo pickle para serializar (transformar em bytes) e 
desserializar (reverter de bytes para objeto) os dados antes do envio e após a recepção.
```

## Como jogar 🎮🎲
Para ter acesso ao jogo é necessário que você faça o download de todos os arquivos presentes neste repositório. Incluindo os arquivos de "Imagens" / client.py / server.py.

### Requisitos 
Certifique-se de que todos os arquivos estão localizados em uma única pasta e que a sua máquina possui o `Python` instalado. 
- [Python](https://www.python.org/downloads/)

### Instruções de Instalação
Ao abrir os arquivos client.py e server.py altere o endereço IP em ambos códigos para o ip da máquina que irá ser o host do jogo (servidor). Não se esqueça que ambas máquinas precisam estar na mesma rede. 

```
SERVER_ADDRESS = ('seu.ip.aqui', porta)
```
Para encontrar o seu ip você pode utilizar esses comandos:

- Ambiente windows  
```
ipconfig
```
![Alt text](image.png)

- Ambiente Linux
```
ifconfig
```
![Alt text](image-1.png)

#### IPs configurados
Agora você pode executar o server.py em sua máquina. E intruir para que seus parceiros de jogo executem o client.py. 
> Caso você esteja sozinho pode executar o client.py em um terminal separado que terá o mesmo resultado! 

### Controles 

Para movimentar a nave basta utilizar as teclas de direção e para atirar utilize a barra de espaço.  



### Feito por:  
>☕ [Gabriella Oliveira](https://github.com/Gabriella0Oliveira)  
>☕ [Diêgo Farias](https://github.com/Gabriella0Oliveira)