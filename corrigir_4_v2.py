#!/usr/bin/env python3
"""Corrige Habacuque e Malaquias — v2"""
import json, os, re, time, urllib.request

BASE = "https://www.liriocatolico.com.br/biblia_online/biblia_pastoral"

def buscar(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = r.read()
            # Tenta UTF-8 primeiro, depois latin-1
            try:
                return raw.decode('utf-8')
            except:
                return raw.decode('latin-1', errors='replace')
    except:
        return None

def extrair(html):
    verses = []
    # Remove scripts e styles
    html = re.sub(r'<script[\s\S]*?</script>', '', html, flags=re.I)
    html = re.sub(r'<style[\s\S]*?</style>', '', html, flags=re.I)

    # Converte br em newline, remove demais tags
    html = re.sub(r'<br\s*/?>', '\n', html, flags=re.I)
    html = re.sub(r'</p>', '\n', html, flags=re.I)
    texto = re.sub(r'<[^>]+>', ' ', html)

    # Limpa entidades HTML
    for e, r in [('&nbsp;',' '),('&amp;','&'),('&quot;','"'),
                 ('&#8220;','"'),('&#8221;','"'),('&#8216;',"'"),
                 ('&#8217;',"'"),('&#8211;','–'),('&#8212;','—'),
                 ('&eacute;','é'),('&atilde;','ã'),('&ccedil;','ç'),
                 ('&oacute;','ó'),('&aacute;','á'),('&iacute;','í'),
                 ('&uacute;','ú'),('&otilde;','õ'),('&ecirc;','ê'),
                 ('&acirc;','â'),('&ocirc;','ô')]:
        texto = texto.replace(e, r)

    # Procura versiculos linha por linha
    for linha in texto.split('\n'):
        linha = linha.strip()
        if not linha:
            continue
        m = re.match(r'^(\d{1,3})[.\s]\s*(.{5,})', linha)
        if m:
            num = int(m.group(1))
            txt = m.group(2).strip()
            if 1 <= num <= 200:
                if not verses or verses[-1]['number'] != num:
                    verses.append({'number': num, 'text': txt})

    # Se nao achou, tenta texto corrido
    if len(verses) < 2:
        verses = []
        tc = re.sub(r'\s+', ' ', texto)
        # Divide pelo padrao "numero espaco texto"
        matches = list(re.finditer(r'(?<!\d)(\d{1,3})(?!\d)\s+([A-ZÀ-Úa-zà-ú])', tc))
        for i, m in enumerate(matches):
            num = int(m.group(1))
            if num < 1 or num > 200:
                continue
            inicio = m.start(2)
            fim = matches[i+1].start(1) if i+1 < len(matches) else inicio+500
            txt = tc[inicio:fim].strip()
            if len(txt) > 5:
                if not verses or verses[-1]['number'] != num:
                    verses.append({'number': num, 'text': txt})

    return sorted(verses, key=lambda v: v['number'])

def salvar(abbrev, nome, cap, total, verses):
    path = os.path.join('livros', abbrev, f'{cap}.json')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = {
        'livro': nome, 'abbrev': abbrev, 'capitulo': cap,
        'total_capitulos': total, 'total_versiculos': len(verses),
        'fonte': 'Biblia Pastoral — Ed. Paulus',
        'versiculos': verses
    }
    if not verses:
        data['status'] = 'pendente'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return len(verses)

def ja_ok(path):
    if not os.path.exists(path):
        return False
    try:
        with open(path, encoding='utf-8') as f:
            d = json.load(f)
        return len(d.get('versiculos', [])) > 0 and d.get('status') != 'pendente'
    except:
        return False

def processar(abbrev, nome_url, nome, total):
    print(f'📖 {nome} ({total} caps) — /{nome_url}/')
    for cap in range(1, total + 1):
        path = os.path.join('livros', abbrev, f'{cap}.json')
        if ja_ok(path):
            print(f'   Cap {cap}: ja ok')
            continue
        url = f'{BASE}/{nome_url}/{cap}/'
        html = buscar(url)
        if html:
            verses = extrair(html)
            n = salvar(abbrev, nome, cap, total, verses)
            status = f'{n} versiculos' if n > 0 else '❌ sem versiculos'
            print(f'   Cap {cap}: {status}')
        else:
            print(f'   Cap {cap}: ❌ URL nao encontrada')
            salvar(abbrev, nome, cap, total, [])
        time.sleep(0.5)

def main():
    print('=' * 50)
    print('Corrigindo Habacuque e Malaquias')
    print('=' * 50)
    print()

    processar('hc', 'habacuc',   'Habacuque', 3)
    print()
    processar('ml', 'malaquias', 'Malaquias',  4)

    print()
    print('Pronto! Agora rode:')
    print('  git add .')
    print('  git commit -m "fix: Habacuque e Malaquias corrigidos"')
    print('  git push')

if __name__ == '__main__':
    main()