from icalendar import Calendar, Event
from datetime import datetime, date, timedelta
from dateutil.rrule import MO, TU, WE, TH, FR
import pytz
import os
from enum import IntEnum

LOCAL_ACADEMIA = 'Smart Fit - R. Professor José de Souza, 1216 - Jardim Vinte e Cinco de Agosto, Duque de Caxias, RJ - 25071-202'
FUZO_HORARIO = pytz.timezone('America/Sao_Paulo')
NOME_ARQUIVO = 'treino_academia_abc_ROTATIVO.ics'

HORA_INICIO = 18
DURACAO_MINUTOS = 90

WORKOUT_SEQUENCE = [
    {"summary": "Treino A: Peito & Tríceps", "uid_tag": "A"},
    {"summary": "Treino B: Costas & Bíceps", "uid_tag": "B"},
    {"summary": "Treino C: Ombro & Perna", "uid_tag": "C"},
]

class WorkoutType(IntEnum):
    A = 0
    B = 1
    C = 2

DATA_INICIO_GERACAO = date(2025, 6, 30)
STARTING_WORKOUT_INDEX = WorkoutType.A.value 
DATA_FIM_RECORRENCIA = date(2030, 12, 31)

DIAS_UTEIS = [0, 1, 2, 3, 4]

def gerar_arquivo_ics_rotativo(workouts, hora_inicio, duracao_minutos, fuso_horario, nome_arquivo, local_academia, data_inicio_loop, data_fim_recorrencia, starting_index):
    """
    Cria um arquivo .ics gerando um evento explícito para cada dia útil
    entre o início e o fim, seguindo um ciclo rotativo (A, B, C, A, B, C...)
    a partir de um índice e data de início específicos.
    """

    cal = Calendar()
    cal.add('prodid', '-//Academia Treino ABC Rotativo//SmartFit//')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', 'Meu Treino ABC Rotativo')
    cal.add('x-wr-timezone', fuso_horario.zone)

    workout_index = starting_index

    data_atual = data_inicio_loop
    eventos_gerados_count = 0

    print(f"Iniciando a geração de eventos explícitos. Base de início: {data_inicio_loop.strftime('%d/%m/%Y')} (Treino {workouts[starting_index]['uid_tag']})...")

    while data_atual <= data_fim_recorrencia:
        if data_atual.weekday() in DIAS_UTEIS:

            current_workout = workouts[workout_index]
            summary = current_workout["summary"]
            uid_tag = current_workout["uid_tag"]

            dtstart = fuso_horario.localize(
                datetime(data_atual.year, data_atual.month, data_atual.day, hora_inicio, 0, 0)
            )
            dtend = dtstart + timedelta(minutes=duracao_minutos)

            event = Event()
            event.add('summary', summary)
            event.add('dtstart', dtstart)
            event.add('dtend', dtend)
            event.add('description', f"Dia de treino (Ciclo Rotativo): {summary}")
            event.add('location', local_academia)

            event.add('uid', f'treino-{uid_tag}-{data_atual.strftime("%Y%m%d")}-rotativo')

            cal.add_component(event)
            eventos_gerados_count += 1

            workout_index = (workout_index + 1) % len(workouts)

        data_atual += timedelta(days=1)


    with open(nome_arquivo, 'wb') as f:
        f.write(cal.to_ical())

    print("\n" + "="*50)
    print(f"🎉 SUCESSO! ARQUIVO ICS COM CICLO ROTATIVO GERADO!")
    print(f"Nome do arquivo: {nome_arquivo}")
    print(f"Total de eventos gerados: {eventos_gerados_count} (até {data_fim_recorrencia.strftime('%d/%m/%Y')})")
    print("Este arquivo contém milhares de eventos explícitos, garantindo a rotação A, B, C...")
    print("="*50)

    print("\nConfirmação da Rotação (Início):")

    data_proxima = DATA_INICIO_GERACAO
    mapa_portugues = {
        0: 'Segunda-feira', 1: 'Terça-feira', 2: 'Quarta-feira',
        3: 'Quinta-feira', 4: 'Sexta-feira'
    }

    temp_index = STARTING_WORKOUT_INDEX
    temp_date = data_proxima

    print(f"--- Rotação a partir de {data_proxima.strftime('%d/%m/%Y')} ---")

    dias_exibidos = 0
    while dias_exibidos < 5:
        if temp_date.weekday() in DIAS_UTEIS:
            summary = WORKOUT_SEQUENCE[temp_index]["summary"]
            dia_nome_pt = mapa_portugues[temp_date.weekday()]

            print(f"-> {dia_nome_pt} ({temp_date.strftime('%d/%m')}) às {HORA_INICIO:02d}:00: {summary}")

            temp_index = (temp_index + 1) % len(WORKOUT_SEQUENCE)
            dias_exibidos += 1

        temp_date += timedelta(days=1)

    print("\nInício da próxima semana (Continuação da rotação):")

    data_proxima_segunda = temp_date
    while data_proxima_segunda.weekday() != 0:
        data_proxima_segunda += timedelta(days=1)

    summary_segunda_w2 = WORKOUT_SEQUENCE[temp_index]["summary"]
    print(f"-> Segunda-feira ({data_proxima_segunda.strftime('%d/%m')}) às {HORA_INICIO:02d}:00: {summary_segunda_w2}")
    print("-" * 30)


try:
    gerar_arquivo_ics_rotativo(
        WORKOUT_SEQUENCE,
        HORA_INICIO,
        DURACAO_MINUTOS,
        FUZO_HORARIO,
        NOME_ARQUIVO,
        LOCAL_ACADEMIA,
        DATA_INICIO_GERACAO,
        DATA_FIM_RECORRENCIA,
        STARTING_WORKOUT_INDEX
    )
except Exception as e:
    print(f"\n❌ Ocorreu um erro durante a geração do arquivo: {e}")