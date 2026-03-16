#!/usr/bin/env python3
"""
Preenche o repositorio Jbreccio/biblia-catolica-json
Fonte: MaatheusGois/bible — pt-br/arc (Almeida Revista e Corrigida)
CORS aberto, dominio publico

Como usar:
  1. Clone seu repositorio:
     git clone https://github.com/Jbreccio/biblia-catolica-json
     cd biblia-catolica-json

  2. Rode este script na raiz do repositorio:
     python3 preencher_biblia.py

  3. Faca o commit:
     git add .
     git commit -m "feat: adiciona textos biblicos completos pt-BR"
     git push

O script baixa cada livro uma vez (cache local) e gera
todos os arquivos livros/{abbrev}/{cap}.json
"""

import json, os, time, urllib.request

BASE_URL = "https://raw.githubusercontent.com/MaatheusGois/bible/main/versions/pt-br/arc"

# (abbrev_seu_repo, id_no_MaatheusGois, nome, total_caps)
LIVROS = [
    # ANTIGO TESTAMENTO
    ("gn",  "gn",  "Genesis",                50),
    ("ex",  "ex",  "Exodo",                  40),
    ("lv",  "lv",  "Levitico",               27),
    ("nm",  "nm",  "Numeros",                36),
    ("dt",  "dt",  "Deuteronomio",           34),
    ("js",  "js",  "Josue",                  24),
    ("jz",  "jz",  "Juizes",                 21),
    ("rt",  "rt",  "Rute",                    4),
    ("1sm", "1sm", "1 Samuel",               31),
    ("2sm", "2sm", "2 Samuel",               24),
    ("1rs", "1rs", "1 Reis",                 22),
    ("2rs", "2rs", "2 Reis",                 25),
    ("1cr", "1cr", "1 Cronicas",             29),
    ("2cr", "2cr", "2 Cronicas",             36),
    ("ed",  "ed",  "Esdras",                 10),
    ("ne",  "ne",  "Neemias",                13),
    ("et",  "et",  "Ester",                  10),
    ("jo",  "job", "Jo",                     42),
    ("sl",  "ps",  "Salmos",                150),
    ("pv",  "pv",  "Proverbios",             31),
    ("ec",  "ec",  "Eclesiastes",            12),
    ("ct",  "sg",  "Cantico dos Canticos",    8),
    ("is",  "is",  "Isaias",                 66),
    ("jr",  "jr",  "Jeremias",               52),
    ("lm",  "lm",  "Lamentacoes",             5),
    ("ez",  "ez",  "Ezequiel",               48),
    ("dn",  "dn",  "Daniel",                 12),
    ("os",  "ho",  "Oseias",                 14),
    ("jl",  "jl",  "Joel",                    3),
    ("am",  "am",  "Amos",                    9),
    ("ob",  "ob",  "Abdias",                  1),
    ("jn",  "jnh", "Jonas",                   4),
    ("mq",  "mic", "Miqueias",                7),
    ("na",  "na",  "Naum",                    3),
    ("hc",  "hab", "Habacuque",               3),
    ("sf",  "zep", "Sofonias",                3),
    ("ag",  "hag", "Ageu",                    2),
    ("zc",  "zec", "Zacarias",               14),
    ("ml",  "mal", "Malaquias",               4),
    # NOVO TESTAMENTO
    ("mt",  "mt",  "Mateus",                 28),
    ("mc",  "mk",  "Marcos",                 16),
    ("lc",  "lk",  "Lucas",                  24),
    ("jo2", "jn",  "Joao",                   21),
    ("at",  "ac",  "Atos dos Apostolos",     28),
    ("rm",  "ro",  "Romanos",                16),
    ("1co", "1co", "1 Corintios",            16),
    ("2co", "2co", "2 Corintios",            13),
    ("gl",  "ga",  "Galatas",                 6),
    ("ef",  "eph", "Efesios",                 6),
    ("fp",  "php", "Filipenses",              4),
    ("cl",  "col", "Colossenses",             4),
    ("1ts", "1th", "1 Tessalonicenses",       5),
    ("2ts", "2th", "2 Tessalonicenses",       3),
    ("1tm", "1ti", "1 Timoteo",               6),
    ("2tm", "2ti", "2 Timoteo",               4),
    ("tt",  "tit", "Tito",                    3),
    ("fm",  "phm", "Filemon",                 1),
    ("hb",  "heb", "Hebreus",               13),
    ("tg",  "jas", "Tiago",                   5),
    ("1pe", "1pe", "1 Pedro",                 5),
    ("2pe", "2pe", "2 Pedro",                 3),
    ("1jo", "1jn", "1 Joao",                  5),
    ("2jo", "2jn", "2 Joao",                  1),
    ("3jo", "3jn", "3 Joao",                  1),
    ("jd",  "jud", "Judas",                   1),
    ("ap",  "rev", "Apocalipse",             22),
]

cache_livros = {}

def baixar_capitulo(id_repo, cap):
    """Baixa um capitulo especifico do MaatheusGois/bible"""
    url = f"{BASE_URL}/{id_repo}/{cap}.json"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        return None

def gerar_arquivo(abbrev, nome, cap, total_caps, id_repo):
    path = os.path.join("livros", abbrev, f"{cap}.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Pula se ja existe com versiculos preenchidos
    if os.path.exists(path):
        with open(path) as f:
            existente = json.load(f)
        if existente.get("verses") or existente.get("versiculos"):
            vv = existente.get("verses") or existente.get("versiculos", [])
            if len(vv) > 0 and existente.get("status") != "pendente":
                return True  # ja preenchido

    # Baixa o capitulo
    data = baixar_capitulo(id_repo, cap)

    if data and data.get("verses"):
        # Formato MaatheusGois: {"chapter": 1, "verses": [{"verse": 1, "text": "..."}]}
        versiculos = [
            {"number": v["verse"], "text": v["text"]}
            for v in data["verses"]
            if v.get("text", "").strip()
        ]
        resultado = {
            "livro": nome,
            "abbrev": abbrev,
            "capitulo": cap,
            "total_capitulos": total_caps,
            "total_versiculos": len(versiculos),
            "versiculos": versiculos
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        return True
    else:
        # Salva placeholder se nao encontrou
        resultado = {
            "livro": nome,
            "abbrev": abbrev,
            "capitulo": cap,
            "total_capitulos": total_caps,
            "total_versiculos": 0,
            "versiculos": [],
            "status": "pendente"
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        return False

def main():
    print("=" * 60)
    print("Preenchendo repositorio biblia-catolica-json")
    print("Fonte: MaatheusGois/bible pt-br/arc")
    print("=" * 60)
    print()

    total_ok = 0
    total_erro = 0
    total_geral = sum(caps for _, _, _, caps in LIVROS)

    for abbrev, id_repo, nome, total_caps in LIVROS:
        print(f"📖 {nome} ({total_caps} caps)...", end=" ", flush=True)
        ok_livro = 0

        for cap in range(1, total_caps + 1):
            sucesso = gerar_arquivo(abbrev, nome, cap, total_caps, id_repo)
            if sucesso:
                ok_livro += 1
                total_ok += 1
            else:
                total_erro += 1
            # Pequeno delay para nao sobrecarregar o GitHub
            time.sleep(0.05)

        print(f"✅ {ok_livro}/{total_caps}")

    print()
    print("=" * 60)
    print(f"✅ Preenchidos: {total_ok}/{total_geral} capitulos")
    if total_erro > 0:
        print(f"⚠️  Pendentes:  {total_erro} (rodar novamente para tentar)")
    print()
    print("Agora rode:")
    print("  git add .")
    print('  git commit -m "feat: adiciona textos biblicos completos pt-BR"')
    print("  git push")
    print("=" * 60)

if __name__ == "__main__":
    main()