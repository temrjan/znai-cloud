"""Query expansion utilities for better search recall."""
import logging
from typing import List, Set

logger = logging.getLogger(__name__)


# Common Russian synonyms and related terms for business/legal domain
SYNONYM_MAP = {
    # Contracts & Agreements
    'договор': ['контракт', 'соглашение', 'сделка'],
    'контракт': ['договор', 'соглашение'],
    'соглашение': ['договор', 'контракт'],

    # Legal terms
    'закон': ['законодательство', 'нормативный акт', 'правовой акт'],
    'право': ['права', 'правовой'],
    'обязанность': ['обязательство', 'долг'],
    'ответственность': ['обязательство', 'санкция'],

    # Business
    'компания': ['организация', 'фирма', 'предприятие', 'юридическое лицо'],
    'организация': ['компания', 'фирма', 'предприятие'],
    'сотрудник': ['работник', 'персонал', 'служащий'],
    'работник': ['сотрудник', 'персонал', 'служащий'],
    'руководитель': ['директор', 'начальник', 'менеджер'],
    'директор': ['руководитель', 'начальник'],

    # Finance
    'оплата': ['платеж', 'выплата', 'вознаграждение'],
    'платеж': ['оплата', 'выплата'],
    'зарплата': ['заработная плата', 'оклад', 'вознаграждение'],
    'цена': ['стоимость', 'тариф', 'расценка'],
    'стоимость': ['цена', 'тариф'],

    # Documents
    'документ': ['бумага', 'акт', 'справка'],
    'заявление': ['заявка', 'обращение', 'ходатайство'],
    'отчет': ['отчетность', 'доклад'],

    # Actions
    'купить': ['приобрести', 'покупка'],
    'продать': ['реализовать', 'продажа'],
    'получить': ['получение', 'приобрести'],
    'оформить': ['оформление', 'зарегистрировать'],

    # Time
    'срок': ['период', 'дата', 'время'],
    'дата': ['срок', 'число'],

    # Common queries
    'как': ['каким образом', 'способ'],
    'правила': ['порядок', 'регламент', 'процедура'],
    'порядок': ['правила', 'процедура', 'алгоритм'],
    'условия': ['требования', 'критерии'],

    # Technical (if needed)
    'ошибка': ['проблема', 'сбой', 'неполадка'],
    'настройка': ['конфигурация', 'параметр'],
}

# English synonyms (basic)
SYNONYM_MAP_EN = {
    'contract': ['agreement', 'deal'],
    'agreement': ['contract', 'deal'],
    'company': ['organization', 'firm', 'business'],
    'employee': ['worker', 'staff'],
    'price': ['cost', 'rate'],
    'payment': ['pay', 'compensation'],
    'document': ['file', 'paper'],
    'rules': ['regulations', 'policy', 'guidelines'],
    'how': ['method', 'way'],
}


def expand_query(query: str, max_expansions: int = 3) -> str:
    """
    Expand query with synonyms for better recall.

    Args:
        query: Original search query
        max_expansions: Maximum number of synonym terms to add per word

    Returns:
        Expanded query string
    """
    query_lower = query.lower()
    words = query_lower.split()

    expansions: Set[str] = set()

    # Check each word against synonym map
    for word in words:
        # Clean word from punctuation
        clean_word = ''.join(c for c in word if c.isalnum())

        # Check Russian synonyms
        if clean_word in SYNONYM_MAP:
            synonyms = SYNONYM_MAP[clean_word][:max_expansions]
            expansions.update(synonyms)

        # Check English synonyms
        if clean_word in SYNONYM_MAP_EN:
            synonyms = SYNONYM_MAP_EN[clean_word][:max_expansions]
            expansions.update(synonyms)

    # Remove words already in query
    expansions -= set(words)

    if expansions:
        expanded = f"{query} {' '.join(expansions)}"
        logger.debug(f"Query expanded: '{query}' -> '{expanded}'")
        return expanded

    return query


def get_query_variations(query: str) -> List[str]:
    """
    Generate multiple query variations for multi-query retrieval.

    Args:
        query: Original search query

    Returns:
        List of query variations including original
    """
    variations = [query]

    # Add expanded version
    expanded = expand_query(query)
    if expanded != query:
        variations.append(expanded)

    return variations
