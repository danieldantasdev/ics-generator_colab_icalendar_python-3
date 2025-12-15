from icalendar import Calendar, Event, vDatetime, vRecur
from datetime import datetime, date, timedelta
from dateutil.rrule import rrule, WEEKLY, MO, TU, WE, TH, FR, SA, SU
import pytz
import os

LOCAL_ACADEMIA = 'Smart Fit - R. Professor José de Souza, 1216 - Jardim Vinte e Cinco de Agosto, Duque de Caxias, RJ - 25071-202'
FUZO_HORARIO = pytz.timezone('America/Sao_Paulo')
NOME_ARQUIVO = 'treino_academia_abc.ics'

HORA_INICIO = 19
DURACAO_MINUTOS = 90

DATA_INICIO_GERACAO = datetime.now().date()
DATA_FIM_RECORRENCIA = date(2030, 12, 31)

CICLO_TREINO = [
    {"dia_da_semana": MO, "summary": "Treino A: Peito & Tríceps"},
    {"dia_da_semana": TU, "summary": "Treino B: Costas & Bíceps"},
    {"dia_da_semana": WE, "summary": "Treino C: Ombro & Perna"},
    {"dia_da_semana": TH, "summary": "Treino A: Peito & Tríceps"},
    {"dia_da_semana": FR, "summary": "Treino B: Costas & Bíceps"},
]


def encontrar_proxima_segunda(data_atual):
    """Encontra a data da próxima segunda-feira ou a de hoje se já for segunda."""
    dias_para_segunda = (7 - data_atual.weekday() + 0) % 7
    if data_atual.weekday() == 5:
        dias_para_segunda = 2
    elif data_atual.weekday() == 6:
        dias_para_segunda = 1
    elif data_atual.weekday() == 0:
        dias_para_segunda = 0
    return data_atual + timedelta(days=dias_para_segunda)

def gerar_arquivo_ics_abc(ciclo, hora_inicio, duracao_minutos, fuso_horario, nome_arquivo, local_academia, data_inicio_geracao, data_fim_recorrencia):
    """
    Cria um arquivo .ics agregando os dias da semana para cada tipo de treino
    (A, B, C) e define uma única RRULE com todos os dias de ocorrência (BYDAY).
    """
    data_inicio_base = encontrar_proxima_segunda(data_inicio_geracao)

    cal = Calendar()
    cal.add('prodid', '-//Academia Treino ABC//SmartFit//')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', 'Meu Treino ABC na Smart Fit')
    cal.add('x-wr-timezone', fuso_horario.zone)

    mapa_dia_ical = {
        MO: 'MO', TU: 'TU', WE: 'WE', TH: 'TH', FR: 'FR', SA: 'SA', SU: 'SU'
    }

    dt_fim_local = fuso_horario.localize(
        datetime(data_fim_recorrencia.year, data_fim_recorrencia.month, data_fim_recorrencia.day, 23, 59, 59)
    )

    until_utc_string = dt_fim_local.astimezone(pytz.utc).strftime('%Y%m%dT%H%M%SZ')

    treinos_agregados = {}

    for item in ciclo:
        summary = item["summary"]
        dia_rrule_obj = item["dia_da_semana"]
        dia_rrule_str = mapa_dia_ical[dia_rrule_obj]

        if summary not in treinos_agregados:
            treinos_agregados[summary] = {
                "dias_rrule_str": [],
                "first_day_obj": dia_rrule_obj
            }

        treinos_agregados[summary]["dias_rrule_str"].append(dia_rrule_str)

    for summary, data in treinos_agregados.items():

        first_day_of_reccurence = data["first_day_obj"]

        dias_para_data_inicial = first_day_of_reccurence.weekday
        data_inicial_evento = data_inicio_base + timedelta(days=(dias_para_data_inicial - data_inicio_base.weekday() + 7) % 7)

        dtstart = fuso_horario.localize(
            datetime(data_inicial_evento.year,
                     data_inicial_evento.month,
                     data_inicial_evento.day,
                     hora_inicio, 0, 0)
        )
        dtend = dtstart + timedelta(minutes=duracao_minutos)

        event = Event()
        event.add('summary', summary)
        event.add('dtstart', dtstart)
        event.add('dtend', dtend)
        event.add('description', f"Dia de treino: {summary}")
        event.add('location', local_academia)
        event.add('uid', f'treino-{summary.lower().replace(" ", "-").replace("&", "").replace(":", "")}-smartfit-abc')

        byday_string = ",".join(data["dias_rrule_str"])
        rrule_string = f'FREQ=WEEKLY;BYDAY={byday_string};UNTIL={until_utc_string}'
        event.add('rrule', rrule_string)

        cal.add_component(event)

    with open(nome_arquivo, 'wb') as f:
        f.write(cal.to_ical())

    print(f"🎉 Arquivo .ics gerado com sucesso!")
    print(f"Nome do arquivo: {nome_arquivo}")
    print("-" * 30)
    print(f"Local: {local_academia}")
    print(f"Intervalo de recorrência: De {data_inicio_base.strftime('%d/%m/%Y')} até {data_fim_recorrencia.strftime('%d/%m/%Y')}")
    print("\nVERIFICAÇÃO CRÍTICA:")
    print("O arquivo contém APENAS 3 EVENTOS VEVENT (A, B, C), mas cada um tem a regra de repetição:")
    print("1. Treino A: Repete toda Segunda (MO) E Quinta (TH).")
    print("2. Treino B: Repete toda Terça (TU) E Sexta (FR).")
    print("3. Treino C: Repete toda Quarta (WE).")
    print("Seu calendário (iPhone/Google) irá exibir os 5 treinos por semana!")
    print("-" * 30)

    print("Primeira Semana de Treino (Confirmação dos 5 dias):")
    data_proxima = data_inicio_base
    mapa_portugues = {
        0: 'Segunda-feira', 1: 'Terça-feira', 2: 'Quarta-feira',
        3: 'Quinta-feira', 4: 'Sexta-feira'
    }

    for item in ciclo:
        dia_index = item['dia_da_semana'].weekday
        summary = item['summary']

        dia_nome_pt = mapa_portugues[dia_index]
        data_treino = data_proxima + timedelta(days=dia_index)
        print(f"-> {dia_nome_pt} ({data_treino.strftime('%d/%m')}) às {HORA_INICIO:02d}:00: {summary}")
    print("-" * 30)


try:
    gerar_arquivo_ics_abc(
        CICLO_TREINO,
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
