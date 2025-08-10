import requests

def get_index_composition(index_code):
    """
    Получаем состав индекса по коду (secid индекса) из API Мосбиржи.
    Возвращает список secid входящих ценных бумаг.
    Если индекс не найден или состав пуст, возвращает пустой список.
    """
    url = f"https://iss.moex.com/iss/engines/stock/markets/index/indices/{index_code}/composition.json"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        composition_data = data.get('composition', {}).get('data', [])
        composition_columns = data.get('composition', {}).get('columns', [])
        if not composition_data or not composition_columns:
            return []

        secid_idx = composition_columns.index('SECID')
        instruments = [row[secid_idx] for row in composition_data]
        return instruments
    except Exception as e:
        print(f"Ошибка при получении состава индекса {index_code}: {e}")
        return []

def get_futures_tickers_by_instrument(instrument):
    """
    Получаем список всех тикеров фьючерсов Московской биржи, начинающихся на instrument.
    Используется API ISS по доске RFUD (фьючерсы).

    Возвращает список уникальных тикеров.
    """
    url = "https://iss.moex.com/iss/engines/futures/markets/forts/boards/RFUD/securities.json"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()

        securities_data = data.get('securities', {}).get('data', [])
        securities_columns = data.get('securities', {}).get('columns', [])

        if not securities_data or not securities_columns:
            return []

        secid_idx = securities_columns.index('SECID')
        tickers = []

        for row in securities_data:
            secid = row[secid_idx]
            # Для надёжного совпадения фильтруем по началу secid
            # Добавляем условие, что секюрид должен начинаться с instrument (без учета регистра — данные в верхнем)
            if secid.upper().startswith(instrument.upper()):
                tickers.append(secid)

        return sorted(set(tickers))
    except Exception as e:
        print(f"Ошибка при получении фьючерсов по инструменту {instrument}: {e}")
        return []

def main():
    print("Программа для получения фьючерсных тикеров по инструменту или индексу с Московской биржи")
    base_input = input("Введите базовое имя инструмента или код индекса (например RGBI, IMOEX): ").strip().upper()

    # Сначала пытаемся получить состав индекса
    components = get_index_composition(base_input)
    all_tickers = []

    if components:
        print(f"Найден состав индекса {base_input}, количество входящих инструментов: {len(components)}")
        # Добавим фьючерсы самого индекса (если есть)
        index_fut_tickers = get_futures_tickers_by_instrument(base_input)
        if index_fut_tickers:
            print(f"Фьючерсы по самому индексу {base_input}: {', '.join(index_fut_tickers)}")
            all_tickers.extend(index_fut_tickers)
        else:
            print(f"Фьючерсы по самому индексу {base_input} не найдены.")

        # Далее для каждого инструмента из состава загружаем фьючерсы
        for instr in components:
            fut_tickers = get_futures_tickers_by_instrument(instr)
            if fut_tickers:
                print(f"Фьючерсы по {instr}: {', '.join(fut_tickers)}")
                all_tickers.extend(fut_tickers)
            else:
                print(f"Фьючерсы по {instr} не найдены.")
    else:
        # Если состав не найден — предполагаем обычный инструмент
        print(f"Состав индекса не найден или пуст, ищем фьючерсы по инструменту {base_input}")
        all_tickers = get_futures_tickers_by_instrument(base_input)

    all_tickers = sorted(set(all_tickers))

    print("\n\nОбщий список всех найденных фьючерсных тикеров:")
    if all_tickers:
        print(", ".join(all_tickers))
    else:
        print("Фьючерсные тикеры не найдены.")

if __name__ == "__main__":
    main()
