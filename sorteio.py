import pygame
import random
import sys
import os

# --- Configurações Iniciais ---
pygame.init()
pygame.mixer.init()

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
CINZA_CLARO = (240, 240, 240)
CINZA_MEDIO = (200, 200, 200)
VERDE_BOTAO = (34, 139, 34)
VERDE_HOVER = (50, 205, 50)
AMARELO_DEST = (255, 215, 0)
AZUL_ESCURO = (0, 0, 128)
AZUL_BARRA = (0, 100, 255)
VERMELHO_BINGO = (220, 20, 60)

# Variáveis Globais de Layout
LARGURA = 800
ALTURA = 600
DIV_1 = 0 
DIV_2 = 0 

tela = pygame.display.set_mode((LARGURA, ALTURA), pygame.RESIZABLE)
pygame.display.set_caption("Bingo Solares")

# --- CARREGAMENTO DE SONS ---
NOMES_ARQUIVOS_SOM = [
    "trap-drums-loop-sound-effect-311578.mp3",
    "drum-roll-for-victory-366448.mp3",
    "beat-drums-4_4_120bpm-9sek-275095.mp3",
    "065391_drumrollwav-88344.mp3",
    "tribe-drum-loop-103173.mp3",
    "tambor-38928.mp3",
    "typical-trap-loop-140bpm-129880.mp3"
]

sons_carregados = []
som_atual_tocando = None
tempo_parar_som = 0 

print("--- Carregando Sons ---")
for nome in NOMES_ARQUIVOS_SOM:
    try:
        s = pygame.mixer.Sound(nome)
        s.set_volume(0.8) 
        sons_carregados.append(s)
        print(f"Carregado: {nome}")
    except FileNotFoundError:
        print(f"AVISO: Arquivo '{nome}' não encontrado.")
    except Exception as e:
        print(f"Erro ao carregar {nome}: {e}")

# Som de Celebração
NOME_SOM_CELEBRACAO = "soft-treble-win-fade-out-ending-sound-effect-416829.mp3"
som_celebracao = None

try:
    som_celebracao = pygame.mixer.Sound(NOME_SOM_CELEBRACAO)
    som_celebracao.set_volume(1.0)
    print(f"Carregado Som de Celebração: {NOME_SOM_CELEBRACAO}")
except FileNotFoundError:
    print(f"ERRO: Arquivo '{NOME_SOM_CELEBRACAO}' não encontrado.")


fontes = {}

def atualizar_fontes(altura_tela):
    scale = altura_tela / 720 
    scale = max(0.5, scale)
    
    fontes['ui'] = pygame.font.SysFont("Arial", int(22 * scale), bold=True)
    fontes['bola_hist'] = pygame.font.SysFont("Arial", int(18 * scale), bold=True) # Fonte para o histórico BINGO
    fontes['bola_input'] = pygame.font.SysFont("Arial", int(12 * scale), bold=True)
    fontes['gigante'] = pygame.font.SysFont("Arial", int(140 * scale), bold=True)
    fontes['titulo'] = pygame.font.SysFont("Arial", int(28 * scale), bold=True)
    fontes['pequena'] = pygame.font.SysFont("Arial", int(16 * scale), bold=True)
    fontes['bingo_header'] = pygame.font.SysFont("Arial Black", int(30 * scale), bold=True) # Fonte para B I N G O

def recalcular_layout(w, h):
    global LARGURA, ALTURA, DIV_1, DIV_2
    LARGURA = w
    ALTURA = h
    DIV_1 = int(w * 0.45)
    DIV_2 = int(w * 0.70)
    atualizar_fontes(h)

recalcular_layout(LARGURA, ALTURA)

# --- Classes ---

class Confete:
    def __init__(self):
        self.x = random.randint(0, LARGURA)
        self.y = random.randint(-ALTURA, -10) 
        self.cor = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        self.vy = random.uniform(2, 5) 
        self.vx = random.uniform(-2, 2) 
        self.tamanho = random.randint(4, 8)
        
    def mover(self):
        self.y += self.vy
        self.x += self.vx
        
    def desenhar(self, superficie):
        pygame.draw.rect(superficie, self.cor, (self.x, self.y, self.tamanho, self.tamanho))

class Particula:
    def __init__(self, x, y, cor):
        self.x = x
        self.y = y
        self.cor = cor
        self.vx = random.uniform(-8, 8) 
        self.vy = random.uniform(-8, 8)
        self.raio = random.randint(4, 12) 
        self.vida = 1.0 

    def mover(self):
        self.x += self.vx
        self.y += self.vy
        self.vida -= 0.02 
        if self.raio > 0.1:
            self.raio -= 0.1 

    def desenhar(self, superficie):
        if self.vida > 0 and self.raio > 0:
            pygame.draw.circle(superficie, self.cor, (int(self.x), int(self.y)), int(self.raio))

class Bolinha:
    def __init__(self, numero):
        self.numero = numero
        self.raio_base = 18
        self.x = random.randint(50, DIV_1 - 50)
        self.y = random.randint(50, ALTURA - 50)
        vel = 4
        self.vx = random.choice([-vel, vel])
        self.vy = random.choice([-vel, vel])
        random.seed(numero)
        self.cor = (random.randint(50, 220), random.randint(50, 220), random.randint(50, 220))
        random.seed()

    def mover(self):
        self.x += self.vx
        self.y += self.vy
        raio_atual = int(self.raio_base * (ALTURA/720))
        raio_atual = max(10, raio_atual)

        if self.x + raio_atual > DIV_1:
            self.x = DIV_1 - raio_atual
            self.vx *= -1
        elif self.x - raio_atual < 0:
            self.x = raio_atual
            self.vx *= -1
        if self.y + raio_atual > ALTURA:
            self.y = ALTURA - raio_atual
            self.vy *= -1
        elif self.y - raio_atual < 0:
            self.y = raio_atual
            self.vy *= -1

    def desenhar(self, superficie):
        raio_atual = int(self.raio_base * (ALTURA/720))
        raio_atual = max(10, raio_atual)
        pygame.draw.circle(superficie, self.cor, (int(self.x), int(self.y)), raio_atual)
        pygame.draw.circle(superficie, PRETO, (int(self.x), int(self.y)), raio_atual, 2)
        txt = fontes['bola_input'].render(str(self.numero), True, PRETO)
        rect = txt.get_rect(center=(int(self.x), int(self.y)))
        superficie.blit(txt, rect)

class Botao:
    def __init__(self, texto, cor_base, cor_hover, acao):
        self.texto = texto
        self.cor_base = cor_base
        self.cor_hover = cor_hover
        self.acao = acao
        self.clicado = False
        self.rect = pygame.Rect(0,0,0,0)
        self.pressionado_tecla = False
        self.ativo = True

    def atualizar_posicao(self):
        largura_coluna_meio = DIV_2 - DIV_1
        w_botao = min(200, largura_coluna_meio - 20)
        h_botao = 60
        centro_x = DIV_1 + (largura_coluna_meio // 2)
        pos_y = int(ALTURA * 0.15)
        self.rect = pygame.Rect(0, 0, w_botao, h_botao)
        self.rect.center = (centro_x, pos_y)

    def desenhar(self, superficie):
        self.atualizar_posicao()
        mouse_pos = pygame.mouse.get_pos()
        cor_atual = self.cor_base
        if not self.ativo:
            cor_atual = CINZA_MEDIO
        elif self.pressionado_tecla:
            cor_atual = AMARELO_DEST
        elif self.rect.collidepoint(mouse_pos):
            cor_atual = self.cor_hover
        
        if self.ativo and self.rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0] and not self.clicado:
                self.clicado = True
                self.acao()
            if not pygame.mouse.get_pressed()[0]:
                self.clicado = False
        
        pygame.draw.rect(superficie, cor_atual, self.rect, border_radius=12)
        pygame.draw.rect(superficie, PRETO, self.rect, 2, border_radius=12)
        txt_mostrar = self.texto if self.ativo else "Sorteando..."
        txt_surf = fontes['ui'].render(txt_mostrar, True, BRANCO if not self.pressionado_tecla else PRETO)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        superficie.blit(txt_surf, txt_rect)

class BarraTempo:
    def __init__(self, valor_inicial=4850, min_val=1000, max_val=10000):
        self.valor = valor_inicial 
        self.min_val = min_val
        self.max_val = max_val
        self.rect_linha = pygame.Rect(0, 0, 0, 0)
        self.rect_botao = pygame.Rect(0, 0, 0, 0)
        self.arrastando = False

    def atualizar_layout(self):
        largura_coluna = DIV_2 - DIV_1
        w_barra = int(largura_coluna * 0.8)
        x_barra = DIV_1 + (largura_coluna - w_barra) // 2
        
        # MUDANÇA: Mais para baixo
        y_barra = ALTURA - 40 
        
        self.rect_linha = pygame.Rect(x_barra, y_barra, w_barra, 8)
        pct = (self.valor - self.min_val) / (self.max_val - self.min_val)
        x_botao = self.rect_linha.x + (pct * self.rect_linha.width)
        self.rect_botao = pygame.Rect(0, 0, 16, 24)
        self.rect_botao.center = (x_botao, self.rect_linha.centery)

    def lidar_eventos(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:
                if self.rect_botao.collidepoint(evento.pos) or self.rect_linha.collidepoint(evento.pos):
                    self.arrastando = True
                    self.atualizar_valor(evento.pos[0])
        elif evento.type == pygame.MOUSEBUTTONUP:
            if evento.button == 1:
                self.arrastando = False
        elif evento.type == pygame.MOUSEMOTION:
            if self.arrastando:
                self.atualizar_valor(evento.pos[0])

    def atualizar_valor(self, mouse_x):
        if mouse_x < self.rect_linha.x: mouse_x = self.rect_linha.x
        if mouse_x > self.rect_linha.right: mouse_x = self.rect_linha.right
        pct = (mouse_x - self.rect_linha.x) / self.rect_linha.width
        self.valor = int(self.min_val + pct * (self.max_val - self.min_val))
        self.rect_botao.centerx = mouse_x

    def desenhar(self, superficie):
        self.atualizar_layout() 
        lbl = fontes['pequena'].render(f"Tempo: {self.valor/1000:.1f}s", True, PRETO)
        superficie.blit(lbl, (self.rect_linha.centerx - lbl.get_width()//2, self.rect_linha.y - 20))
        pygame.draw.rect(superficie, CINZA_MEDIO, self.rect_linha, border_radius=4)
        rect_preenchido = self.rect_linha.copy()
        rect_preenchido.width = self.rect_botao.centerx - self.rect_linha.x
        pygame.draw.rect(superficie, AZUL_BARRA, rect_preenchido, border_radius=4)
        pygame.draw.rect(superficie, AZUL_ESCURO, self.rect_botao, border_radius=4)
        pygame.draw.rect(superficie, BRANCO, self.rect_botao, 1, border_radius=4)

# --- Variáveis Globais ---
bolinhas_no_globo = []
particulas = [] 
confetes = [] 
historico_sorteados = []
bola_atual_obj = None
estado = "INPUT" 
texto_input = ""

# Variáveis de Animação
animando = False
tempo_inicio_anim = 0
bola_visual_temp = None
timer_troca_numero = 0

DURACAO_FIXA = 4850 

def criar_explosao(x, y, cor, quantidade=100):
    for _ in range(quantidade):
        p = Particula(x, y, cor)
        particulas.append(p)

def soltar_celebracao():
    if som_celebracao:
        som_celebracao.play()

    for _ in range(300):
        confetes.append(Confete())
    
    for _ in range(10):
        fx = random.randint(50, LARGURA - 50)
        fy = random.randint(50, ALTURA - 50)
        fcor = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        criar_explosao(fx, fy, fcor, quantidade=40)

def iniciar_animacao():
    global animando, tempo_inicio_anim, btn_sortear, som_atual_tocando, tempo_parar_som
    
    if len(bolinhas_no_globo) > 0 and not animando:
        animando = True
        tempo_inicio_anim = pygame.time.get_ticks()
        btn_sortear.ativo = False
        tempo_parar_som = 0
        
        if sons_carregados:
            if som_atual_tocando: 
                som_atual_tocando.stop()
            som_atual_tocando = random.choice(sons_carregados)
            som_atual_tocando.play()

def finalizar_sorteio():
    global bola_atual_obj, animando, btn_sortear, som_atual_tocando, tempo_parar_som
    
    tempo_parar_som = pygame.time.get_ticks() + 500

    if len(bolinhas_no_globo) > 0:
        escolhida = random.choice(bolinhas_no_globo)
        criar_explosao(escolhida.x, escolhida.y, escolhida.cor)
        bolinhas_no_globo.remove(escolhida)
        bola_atual_obj = escolhida
        historico_sorteados.append(escolhida)
        # Não precisamos mais ordenar a lista inteira, pois vamos separar visualmente
    
    animando = False
    btn_sortear.ativo = True

btn_sortear = Botao("SORTEAR", VERDE_BOTAO, VERDE_HOVER, iniciar_animacao)

# --- NOVA FUNÇÃO DE DESENHO DO HISTÓRICO (B I N G O) ---
def desenhar_historico_bingo(superficie):
    area_x = DIV_2
    largura_area = LARGURA - DIV_2
    
    # Cabeçalho B I N G O
    letras = ["B", "I", "N", "G", "O"]
    cores_letras = [(0, 0, 255), (255, 0, 0), (0, 0, 0), (0, 128, 0), (255, 165, 0)] # Azul, Vermelho, Preto, Verde, Laranja (padrão bingo)
    
    largura_coluna = largura_area / 5
    
    # Desenhar Letras
    for i, letra in enumerate(letras):
        cx = area_x + (i * largura_coluna) + (largura_coluna // 2)
        txt = fontes['bingo_header'].render(letra, True, cores_letras[i])
        superficie.blit(txt, (cx - txt.get_width()//2, 20))
        
        # Linha separadora vertical
        if i > 0:
            lx = area_x + (i * largura_coluna)
            pygame.draw.line(superficie, CINZA_MEDIO, (lx, 0), (lx, ALTURA), 2)

    # Organizar bolinhas nas colunas
    # B: 1-15, I: 16-30, N: 31-45, G: 46-60, O: 61-75
    
    # Separar os sorteados por coluna
    colunas = [[], [], [], [], []]
    
    for bola in historico_sorteados:
        n = bola.numero
        idx = -1
        if 1 <= n <= 15: idx = 0
        elif 16 <= n <= 30: idx = 1
        elif 31 <= n <= 45: idx = 2
        elif 46 <= n <= 60: idx = 3
        elif 61 <= n <= 75: idx = 4
        
        if idx != -1:
            colunas[idx].append(bola)
            
    # Ordenar cada coluna numericamante (para ficar bonito)
    for col in colunas:
        col.sort(key=lambda b: b.numero)

    # Desenhar as bolinhas
    inicio_y = 80
    raio_bola = int(18 * (ALTURA/720)) # Ajustado para caber na coluna
    distancia_y = (raio_bola * 2) + 5
    
    for i_col, lista_bolas in enumerate(colunas):
        cx = area_x + (i_col * largura_coluna) + (largura_coluna // 2)
        
        for i_linha, bola in enumerate(lista_bolas):
            cy = inicio_y + (i_linha * distancia_y)
            
            # Se passar da tela, não desenha (mas o bingo é 15 numeros por coluna, deve caber)
            if cy + raio_bola > ALTURA: continue

            pygame.draw.circle(superficie, bola.cor, (int(cx), int(cy)), raio_bola)
            pygame.draw.circle(superficie, PRETO, (int(cx), int(cy)), raio_bola, 1)
            
            txt = fontes['bola_hist'].render(str(bola.numero), True, PRETO)
            r_txt = txt.get_rect(center=(int(cx), int(cy)))
            superficie.blit(txt, r_txt)

def main():
    global estado, texto_input, bolinhas_no_globo, historico_sorteados, bola_atual_obj, tela, LARGURA, ALTURA
    global animando, bola_visual_temp, timer_troca_numero, particulas, confetes, som_atual_tocando, tempo_parar_som, DURACAO_FIXA
    
    relogio = pygame.time.Clock()
    barra_tempo = BarraTempo(valor_inicial=DURACAO_FIXA)

    rodando = True
    while rodando:
        tela.fill(BRANCO)
        tempo_atual = pygame.time.get_ticks()
        
        DURACAO_FIXA = barra_tempo.valor

        if tempo_parar_som > 0 and tempo_atual >= tempo_parar_som:
            if som_atual_tocando:
                som_atual_tocando.stop()
            tempo_parar_som = 0

        if animando:
            if tempo_atual - tempo_inicio_anim > DURACAO_FIXA:
                finalizar_sorteio()
            else:
                if tempo_atual - timer_troca_numero > 80:
                    if len(bolinhas_no_globo) > 0:
                        bola_visual_temp = random.choice(bolinhas_no_globo)
                    timer_troca_numero = tempo_atual

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
            elif event.type == pygame.VIDEORESIZE:
                tela = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                recalcular_layout(event.w, event.h)
            
            if estado == "INPUT":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        texto_input = texto_input[:-1]
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        if texto_input.isdigit() and int(texto_input) > 0:
                            qtd = int(texto_input)
                            bolinhas_no_globo = [Bolinha(i+1) for i in range(qtd)]
                            historico_sorteados = []
                            particulas = []
                            confetes = []
                            bola_atual_obj = None
                            estado = "JOGANDO"
                    elif event.unicode.isdigit():
                        texto_input += event.unicode
            
            elif estado == "JOGANDO":
                barra_tempo.lidar_eventos(event)
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        estado = "INPUT"
                        texto_input = ""
                        animando = False
                        bola_atual_obj = None
                        tempo_parar_som = 0
                        if som_atual_tocando: som_atual_tocando.stop()
                    
                    elif (event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER) and not animando:
                        iniciar_animacao()
                        btn_sortear.pressionado_tecla = True
                    
                    elif event.key == pygame.K_SPACE:
                        soltar_celebracao()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        btn_sortear.pressionado_tecla = False

        cx, cy = LARGURA // 2, ALTURA // 2

        if estado == "INPUT":
            box_w = min(400, LARGURA - 40)
            box_h = 200
            pygame.draw.rect(tela, CINZA_CLARO, (cx - box_w//2, cy - box_h//2, box_w, box_h), border_radius=20)
            pygame.draw.rect(tela, PRETO, (cx - box_w//2, cy - box_h//2, box_w, box_h), 2, border_radius=20)
            lbl = fontes['titulo'].render("Qtd Números (Padrão 75):", True, PRETO)
            tela.blit(lbl, (cx - lbl.get_width()//2, cy - 50))
            txt = fontes['titulo'].render(texto_input + "|", True, AZUL_ESCURO)
            tela.blit(txt, (cx - txt.get_width()//2, cy))
            lbl2 = fontes['ui'].render("Enter p/ Iniciar", True, VERDE_BOTAO)
            tela.blit(lbl2, (cx - lbl2.get_width()//2, cy + 50))

        elif estado == "JOGANDO":
            pygame.draw.rect(tela, (245, 245, 255), (0, 0, DIV_1, ALTURA))
            
            for b in bolinhas_no_globo:
                b.mover()
                b.desenhar(tela)
            
            for c in confetes[:]:
                c.mover()
                c.desenhar(tela)
                if c.y > ALTURA:
                    confetes.remove(c)

            for p in particulas[:]: 
                p.mover()
                p.desenhar(tela)
                if p.vida <= 0:
                    particulas.remove(p)
            
            lbl_res = fontes['ui'].render(f"Restam: {len(bolinhas_no_globo)}", True, PRETO)
            tela.blit(lbl_res, (10, ALTURA - 40))

            if bolinhas_no_globo or animando:
                btn_sortear.desenhar(tela)
            else:
                fim = fontes['titulo'].render("FIM", True, PRETO)
                tela.blit(fim, (DIV_1 + (DIV_2-DIV_1)//2 - fim.get_width()//2, ALTURA*0.15))

            centro_x_meio = DIV_1 + (DIV_2 - DIV_1) // 2
            centro_y_meio = ALTURA // 2 + 40
            raio_grande = min((DIV_2 - DIV_1)//2 - 10, 120) 
            raio_grande = max(50, raio_grande)

            bola_para_desenhar = bola_visual_temp if animando else bola_atual_obj

            if bola_para_desenhar:
                pygame.draw.circle(tela, bola_para_desenhar.cor, (centro_x_meio, centro_y_meio), raio_grande)
                pygame.draw.circle(tela, PRETO, (centro_x_meio, centro_y_meio), raio_grande, 5)
                num_surf = fontes['gigante'].render(str(bola_para_desenhar.numero), True, BRANCO)
                if num_surf.get_width() > raio_grande * 1.5:
                     num_surf = pygame.transform.scale(num_surf, (int(raio_grande*1.5), int(num_surf.get_height() * 0.6)))
                r_num = num_surf.get_width()//2
                tela.blit(num_surf, (centro_x_meio - r_num, centro_y_meio - num_surf.get_height()//2))
                
                # Exibe a letra da bola sorteada
                letra_bola = ""
                n = bola_para_desenhar.numero
                if 1 <= n <= 15: letra_bola = "B"
                elif 16 <= n <= 30: letra_bola = "I"
                elif 31 <= n <= 45: letra_bola = "N"
                elif 46 <= n <= 60: letra_bola = "G"
                elif 61 <= n <= 75: letra_bola = "O"
                
                if not animando:
                    lbl_s = fontes['titulo'].render(f"{letra_bola} - {n}", True, PRETO)
                    tela.blit(lbl_s, (centro_x_meio - lbl_s.get_width()//2, centro_y_meio - raio_grande - 40))

            # USANDO O NOVO DESENHO DO HISTÓRICO BINGO
            desenhar_historico_bingo(tela)
            
            barra_tempo.desenhar(tela)
            
            pygame.draw.line(tela, PRETO, (DIV_1, 0), (DIV_1, ALTURA), 3)
            pygame.draw.line(tela, PRETO, (DIV_2, 0), (DIV_2, ALTURA), 3)

        pygame.display.flip()
        relogio.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()