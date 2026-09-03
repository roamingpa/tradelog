import re
import unicodedata
from decimal import Decimal, InvalidOperation


CHAT_LINE_RE = re.compile(
    r'^\[?\d{1,2}[/-]\d{1,2}[/-]\d{2,4},?\s+\d{1,2}:\d{2}(?::\d{2})?\]?\s*-?\s*([^:]+):\s*(.*)$'
)
SIMPLE_SPEAKER_RE = re.compile(r'^([^:\n]{2,60}):\s+(.+)$')
CARD_CODE_RE = re.compile(r'\b((?:OP|ST|EB|PRB)\s*\d{1,2}\s*[- ]?\s*\d{3}|P\s*[- ]?\s*\d{3})\b', re.IGNORECASE)
PHONE_RE = re.compile(r'(?:\+?56\s*)?(?:9\s*)?(?:\d[\s.-]*){8,}')
SHIPPING_RE = re.compile(r'\b(env[ií]o|enviar|despacho|despachar|chilexpress|starken|bluexpress|direcci[oó]n)\b', re.IGNORECASE)
PICKUP_RE = re.compile(r'\b(retiro|retirar|entrega presencial|metro|estaci[oó]n|juntamos|juntar)\b', re.IGNORECASE)
CURRENCY_RE = re.compile(r'\b(usd|us\$|d[oó]lar(?:es)?|ars|argentino(?:s)?|clp|peso(?:s)?|\$)\b', re.IGNORECASE)


def parse_whatsapp_import(raw_text, *, transaction_kind, cards, contacts, own_names=()):
    text = (raw_text or '').strip()
    card_index = _build_card_index(cards)
    contact_index = _build_contact_index(contacts)
    participants = _extract_participants(text)
    contact_suggestion = _guess_contact_name(participants, own_names)
    contact = _match_contact(text, contact_suggestion, contact_index)
    items = _merge_duplicate_items(_extract_items(text, card_index))
    is_shipping = _detect_shipping(text)
    currency = _detect_currency(text)

    return {
        'ok': bool(text),
        'transaction_kind': transaction_kind,
        'looks_like_chat': bool(participants),
        'contact': contact,
        'contact_suggestion': contact_suggestion,
        'items': items,
        'unmatched_codes': [item['code'] for item in items if not item['matched']],
        'currency': currency,
        'is_shipping': is_shipping,
        'instructions': _extract_instruction_lines(text) if is_shipping else '',
        'notes': _build_notes(text),
    }


def _build_card_index(cards):
    index = {}
    for card in cards:
        code = _normalize_card_code(card.code)
        index.setdefault(code, []).append(card)
    return index


def _build_contact_index(contacts):
    by_name = {}
    by_phone = []
    for contact in contacts:
        by_name[_normalize_text(contact.name)] = contact
        phone = _digits(contact.whatsapp)
        if phone:
            by_phone.append((phone, contact))
    return {'by_name': by_name, 'by_phone': by_phone}


def _extract_participants(text):
    counts = {}
    for line in text.splitlines():
        clean_line = line.strip()
        match = CHAT_LINE_RE.match(clean_line) or SIMPLE_SPEAKER_RE.match(clean_line)
        if not match:
            continue
        name = match.group(1).strip()
        counts[name] = counts.get(name, 0) + 1
    return sorted(counts.items(), key=lambda item: item[1], reverse=True)


def _guess_contact_name(participants, own_names):
    own = {_normalize_text(name) for name in own_names if name}
    for name, _count in participants:
        normalized = _normalize_text(name)
        if normalized and normalized not in own and normalized != 'tu':
            return name
    return ''


def _match_contact(text, contact_suggestion, contact_index):
    if contact_suggestion:
        contact = contact_index['by_name'].get(_normalize_text(contact_suggestion))
        if contact:
            return _serialize_contact(contact, 'name')

    phones = [_digits(match.group(0)) for match in PHONE_RE.finditer(text)]
    for pasted_phone in phones:
        if len(pasted_phone) < 8:
            continue
        for contact_phone, contact in contact_index['by_phone']:
            if pasted_phone.endswith(contact_phone[-8:]) or contact_phone.endswith(pasted_phone[-8:]):
                return _serialize_contact(contact, 'phone')
    return None


def _extract_items(text, card_index):
    items = []
    for line in text.splitlines():
        for match in CARD_CODE_RE.finditer(line):
            code = _normalize_card_code(match.group(1))
            matches = card_index.get(code, [])
            card = matches[0] if matches else None
            quantity = _extract_quantity(line, match)
            items.append({
                'code': code,
                'matched': card is not None,
                'card_id': str(card.pk) if card else '',
                'card_name': card.name if card else '',
                'card_label': str(card) if card else code,
                'card_image_url': card.image_url if card else '',
                'quantity': quantity,
                'unit_price': _extract_price(line, quantity),
                'variants_count': len(matches),
            })
    return items


def _merge_duplicate_items(items):
    merged = []
    positions = {}
    for item in items:
        key = item['card_id'] or item['code']
        if key not in positions:
            positions[key] = len(merged)
            merged.append(item)
            continue
        existing = merged[positions[key]]
        existing['quantity'] += item['quantity']
        if existing['unit_price'] in {'0', '0.00'} and item['unit_price'] not in {'0', '0.00'}:
            existing['unit_price'] = item['unit_price']
    return merged


def _extract_quantity(line, code_match):
    before = line[:code_match.start()]
    after = line[code_match.end():]
    before_match = re.search(r'(?:^|\s)(\d{1,2})\s*x?\s*$', before, re.IGNORECASE)
    if before_match:
        return max(1, int(before_match.group(1)))
    after_match = re.search(r'^\s*(?:x\s*)?(\d{1,2})\b', after, re.IGNORECASE)
    if after_match and re.search(r'^\s*x', after, re.IGNORECASE):
        return max(1, int(after_match.group(1)))
    units_match = re.search(r'\b(\d{1,2})\s*(?:un|unds|unidades)\b', line, re.IGNORECASE)
    if units_match:
        return max(1, int(units_match.group(1)))
    return 1


def _extract_price(line, quantity=1):
    cleaned = CARD_CODE_RE.sub(' ', line)
    patterns = [
        r'\$\s*([\d.]+(?:,\d{1,2})?)\s*(k|mil)?',
        r'\b([\d]+(?:[.,]\d+)?)\s*(k|mil)\b',
        r'\b([\d.]{4,}(?:,\d{1,2})?)\s*(?:clp|c/u|cada|ea)?\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, cleaned, re.IGNORECASE)
        if not match:
            continue
        multiplier = 1000 if len(match.groups()) > 1 and match.group(2) else 1
        amount = _parse_decimal(match.group(1))
        if amount is not None:
            price = amount * multiplier
            if quantity > 1 and re.search(r'\b(total|por todo|ambas|ambos)\b', cleaned, re.IGNORECASE):
                price = price / Decimal(quantity)
            return _format_decimal(price)
    return '0'


def _parse_decimal(value):
    normalized = value.strip().replace(' ', '')
    if ',' in normalized and normalized.rfind(',') > normalized.rfind('.'):
        normalized = normalized.replace('.', '').replace(',', '.')
    else:
        normalized = normalized.replace('.', '')
    try:
        return Decimal(normalized)
    except InvalidOperation:
        return None


def _format_decimal(value):
    normalized = value.quantize(Decimal('0.01')) if value != value.to_integral_value() else value.quantize(Decimal('1'))
    return format(normalized, 'f')


def _detect_currency(text):
    match = CURRENCY_RE.search(text)
    if not match:
        return None
    token = _normalize_text(match.group(1))
    if token in {'usd', 'us$', 'dolar', 'dolares'}:
        return 'USD'
    if token in {'ars', 'argentino', 'argentinos'}:
        return 'ARS'
    return 'CLP'


def _detect_shipping(text):
    has_shipping = SHIPPING_RE.search(text)
    has_pickup = PICKUP_RE.search(text)
    if has_shipping:
        return True
    if has_pickup:
        return False
    return None


def _extract_instruction_lines(text):
    lines = []
    for line in text.splitlines():
        if SHIPPING_RE.search(line):
            lines.append(line.strip())
    return '\n'.join(lines[:5])


def _build_notes(text):
    return f'Importado desde WhatsApp:\n{text}'


def _serialize_contact(contact, matched_by):
    return {'id': str(contact.pk), 'name': contact.name, 'matched_by': matched_by}


def _normalize_card_code(value):
    compact = re.sub(r'\s+', '', (value or '').upper()).replace('_', '-')
    compact = compact.replace(' ', '')
    match = re.match(r'^(OP|ST|EB|PRB)(\d{1,2})-?(\d{3})$', compact)
    if match:
        prefix, set_number, card_number = match.groups()
        return f'{prefix}{int(set_number):02d}-{card_number}'
    if '-' in compact:
        prefix, number = compact.split('-', 1)
        return f'{prefix}-{number}'
    if compact.startswith('P') and len(compact) > 1:
        return f'P-{compact[1:]}'
    return f'{compact[:-3]}-{compact[-3:]}' if len(compact) > 3 else compact


def _normalize_text(value):
    decomposed = unicodedata.normalize('NFKD', value or '')
    ascii_text = ''.join(ch for ch in decomposed if not unicodedata.combining(ch))
    return re.sub(r'\s+', ' ', ascii_text).strip().casefold()


def _digits(value):
    return re.sub(r'\D+', '', value or '')