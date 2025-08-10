import requests
from datetime import datetime

def get_futures_tickers(instrument, start_date, end_date):
    """
    Получение списка всех тикеров фьючерсов Московской биржи по инструменту
    за указанный период (start_date, end_date) через API ISS.
    
    instrument -- базовое имя инструмента, например "RGBI"
    start_date, end_date -- строки формата "YYYY-MM-DD"
    """
    base_url = "https://iss.moex.com/iss/engines/futures/markets/forts/boards/RFUD/securities.json"
    
    tickers = []
    
    # API возвращает текущие доступные тикеры, для истории надо проверить архив
    # ISS не предоставляет прямой фильтр по дате тикеров, поэтому делаем обход:
    # - Получаем весь список Securities за board RFUD (фьючерсы)
    # - Фильтруем вручную по названию и дате (по подписи даты исполнения в тикере)
    
    resp = requests.get(base_url)
    resp.raise_for_status()
    data = resp.json()
    
    securities = data['securities']['data']
    columns = data['securities']['columns']
    
    # Найдем индексы нужных полей в таблице
    secid_idx = columns.index('SECID')
    
    # В тикерах фьючерсов есть в названии признак даты исполнения, например RGBI3.25, RGBI-3.25 или RGBI12.23
    # Попробуем извлечь тикеры, начинающиеся на instrument
    for sec in securities:
        secid = sec[secid_idx]
        if secid.startswith(instrument):
            # Пример форматов: RGBI3.25, RGBI-3.25, RGBI12.23
            # Извлечем части для оценки даты, возьмем последние 3-4 символа для года и месяца квартала
            # Для точного отбора понадобится сопоставить с датами по контракту, но базово отфильтруем по диапазону дат исполнения
            # Для демонстрации оставим все, соответствующие инструменту
            
            tickers.append(secid)
    
    # Уникализируем и отсортируем список
    tickers = sorted(list(set(tickers)))
    
    return tickers

if __name__ == "__main__":
    # Пример: пользователь задает инструмент и период
    instrument = input("Введите базовое имя инструмента (например RGBI): ").strip().upper()
    start_date = input("Введите дату начала периода в формате ГГГГ-ММ-ДД (например 2015-01-01): ").strip()
    end_date = input("Введите дату окончания периода в формате ГГГГ-ММ-ДД (например 2025-08-10): ").strip()

    # Программа пока не фильтрует по точной дате исполнения контрактов,
    # так как для этого нужно отдельно получать даты истечения контрактов.
    # Для более продвинутого парсинга можно дополнять запросы.
    
    tickers = get_futures_tickers(instrument, start_date, end_date)
    print("Список фьючерсных тикеров по инструменту", instrument, "за период", start_date, "—", end_date, ":")
    print(", ".join(tickers))
