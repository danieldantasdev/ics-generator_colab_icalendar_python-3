# --- 1. INSTALAÇÃO DAS BIBLIOTECAS ---
# Instala as bibliotecas necessárias no ambiente do Colab.
!pip install icalendar python-dateutil

# --- 2. IMPORTAÇÕES ---
# Note que removemos vRecur pois não usaremos RRULE, e sim eventos explícitos.
from icalendar import Calendar, Event 
from datetime import datetime, date, timedelta
from dateutil.rrule import MO, TU, WE, TH, FR
import pytz
import os

# --- 3. CONFIGURAÇÃO MODULAR (COMPLETA) ---

# [LOCALIZAÇÃO]
LOCAL_ACADEMIA = 'Smart Fit - R. Professor José de Souza, 1216 - Jardim Vinte e Cinco de Agosto, Duque de Caxias, RJ - 25071-202'
FUZO_HORARIO = pytz.timezone('America/Sao_Paulo') 
NOME_ARQUIVO = 'treino_academia_abc_ROTATIVO.ics' # Mudamos o nome para diferenciar

# [HORÁRIO]
HORA_INICIO = 18 # Hora de início do treino (18:00)
DURACAO_MINUTOS = 90 # Duração de 1 hora e 30 minutos

# [INTERVALO DE GERAÇÃO] 
# DATA_INICIO_GERACAO será usada para encontrar a próxima Segunda-feira.
DATA_INICIO_GERACAO = datetime.now().date() 
# Data de término para a geração explícita.
DATA_FIM_RECORRENCIA = date(2026, 12, 31) 

# [CICLO DE TREINO] - Apenas a sequência e os SUMMARIES
# Define a sequência dos 3 treinos, que se repetirá continuamente (A, B, C, A, B, C...)
WORKOUT_SEQUENCE = [
    {"summary": "Treino A: Peito & Tríceps", "uid_tag": "A"}, 
    {"summary": "Treino B: Costas & Bíceps", "uid_tag": "B"},
    {"summary": "Treino C: Ombro & Perna", "uid_tag": "C"},
]

# Dias da semana a serem considerados (Segunda a Sexta)
DIAS_UTEIS = [0, 1, 2, 3, 4] # 0=Segunda, 4=Sexta

# --- 4. FUNÇÕES ---

def encontrar_proxima_segunda(data_atual):
    """Encontra a data da próxima segunda-feira."""
    dias_para_segunda = (7 - data_atual.weekday() + 0) % 7
    # Se hoje é segunda, queremos começar hoje mesmo. Se não, próxima segunda.
    if data_atual.weekday() == 0:
        dias_para_segunda = 0
    elif data_atual.weekday() >= 5: # Se for Sábado ou Domingo, pula para a próxima Segunda
        dias_para_segunda = (7 - data_atual.weekday() + 0) % 7
        
    return data_atual + timedelta(days=dias_para_segunda)

def gerar_arquivo_ics_rotativo(workouts, hora_inicio, duracao_minutos, fuso_horario, nome_arquivo, local_academia, data_inicio_geracao, data_fim_recorrencia):
    """
    Cria um arquivo .ics gerando um evento explícito para cada dia útil 
    entre o início e o fim, seguindo um ciclo rotativo (A, B, C, A, B, C...).
    """
    
    # 1. Obter a data de início real para o loop (Próxima Segunda-feira)
    # A contagem do ciclo começa sempre na primeira Segunda-feira disponível.
    data_inicio_loop = encontrar_proxima_segunda(data_inicio_geracao)
    
    cal = Calendar()
    cal.add('prodid', '-//Academia Treino ABC Rotativo//SmartFit//')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', 'Meu Treino ABC Rotativo')
    cal.add('x-wr-timezone', fuso_horario.zone)
    
    # Índice para navegar na sequência de treinos (0=A, 1=B, 2=C)
    workout_index = 0
    
    data_atual = data_inicio_loop
    eventos_gerados_count = 0
    
    print(f"Iniciando a geração de eventos explícitos. Isso pode levar alguns segundos...")
    
    # 2. Loop dia a dia até a data final (31/12/2030)
    while data_atual <= data_fim_recorrencia:
        
        # 3. Verifica se é um dia útil (Segunda a Sexta)
        if data_atual.weekday() in DIAS_UTEIS:
            
            # Pega o treino atual da sequência (A, B ou C)
            current_workout = workouts[workout_index]
            summary = current_workout["summary"]
            uid_tag = current_workout["uid_tag"]
            
            # Define o DTSTART e DTEND para esta data específica
            dtstart = fuso_horario.localize(
                datetime(data_atual.year, data_atual.month, data_atual.day, hora_inicio, 0, 0)
            )
            dtend = dtstart + timedelta(minutes=duracao_minutos)

            # Cria o Evento
            event = Event()
            event.add('summary', summary)
            event.add('dtstart', dtstart)
            event.add('dtend', dtend)
            event.add('description', f"Dia de treino (Ciclo Rotativo): {summary}")
            event.add('location', local_academia)
            
            # UID único para o evento: usa o ID do treino + a data específica
            event.add('uid', f'treino-{uid_tag}-{data_atual.strftime("%Y%m%d")}-rotativo')
            
            cal.add_component(event)
            eventos_gerados_count += 1

            # Avança para o próximo treino na sequência (A, B, C, A, B, C...)
            workout_index = (workout_index + 1) % len(workouts)
        
        # Avança para o próximo dia
        data_atual += timedelta(days=1)


    # 5. Salva o arquivo .ics
    with open(nome_arquivo, 'wb') as f:
        f.write(cal.to_ical())

    print("\n" + "="*50)
    print(f"🎉 SUCESSO! ARQUIVO ICS COM CICLO ROTATIVO GERADO!")
    print(f"Nome do arquivo: {nome_arquivo}")
    print(f"Total de eventos gerados: {eventos_gerados_count} (até {data_fim_recorrencia.strftime('%d/%m/%Y')})")
    print(f"O ciclo começa na Segunda-feira: {data_inicio_loop.strftime('%d/%m/%Y')}")
    print("Este arquivo contém milhares de eventos explícitos, garantindo a rotação A, B, C...")
    print("Agora, hospede-o no GitHub (link Raw) e assine-o no seu iPhone.")
    print("="*50)
    
    # Exibe a primeira ocorrência de cada treino para confirmação
    print("\nConfirmação da Rotação (Próxima Semana):")
    
    # Usamos o data_inicio_loop (Segunda-feira, 17/11/2025)
    data_proxima = data_inicio_loop
    mapa_portugues = {
        0: 'Segunda-feira', 1: 'Terça-feira', 2: 'Quarta-feira',
        3: 'Quinta-feira', 4: 'Sexta-feira'
    }
    
    # Simula a primeira semana de rotação
    temp_index = 0
    for i in range(5): 
        summary = WORKOUT_SEQUENCE[temp_index]["summary"]
        dia_nome_pt = mapa_portugues[i]
        data_treino = data_proxima + timedelta(days=i)
        print(f"-> {dia_nome_pt} ({data_treino.strftime('%d/%m')}) às {HORA_INICIO:02d}:00: {summary}")
        temp_index += 1
    
    # Simula o início da segunda semana (Treino C deve ser o 3º item da sequência [0, 1, 2], que é o Treino C)
    print("\nInício da SEGUNDA Semana (Rotação continua do Treino C):")
    data_proxima_segunda = data_proxima + timedelta(days=7)
    
    # O workout_index atual é 5, mas (5 % 3) é 2, que é o Treino C.
    summary_segunda_w2 = WORKOUT_SEQUENCE[2]["summary"] 
    print(f"-> Segunda-feira ({data_proxima_segunda.strftime('%d/%m')}) às {HORA_INICIO:02d}:00: {summary_segunda_w2} (Treino C)")
    print("-" * 30)


# --- 6. EXECUÇÃO ---
try:
    gerar_arquivo_ics_rotativo(
        WORKOUT_SEQUENCE, 
        HORA_INICIO, 
        DURACAO_MINUTOS, 
        FUZO_HORARIO, 
        NOME_ARQUIVO, 
        LOCAL_ACADEMIA, 
        DATA_INICIO_GERACAO, 
        DATA_FIM_RECORRENCIA
    )
except Exception as e:
    print(f"\n❌ Ocorreu um erro durante a geração do arquivo: {e}")