"""Generate produk.html from index.html (header/footer) and products.json. Run: python build.py"""
import json, re, html, urllib.parse as u

s = open('index.html', encoding='utf-8').read()
P = json.load(open('products.json', encoding='utf-8'))

def clean(n):  # Tokopedia titles are SEO keyword lists; keep the first phrase
    n = re.split(r'\s+[|/]\s*|/', n.strip())[0].strip()
    return n[:1].upper() + n[1:]

cards = ''
for p in P:
    n = clean(p['name'])
    wa = 'https://wa.me/6282258475758?text=' + u.quote(f'Halo, saya ingin meminta penawaran untuk {n}')
    cards += f'''<li class="card" data-name="{html.escape(n.lower())}"><img src="{p['img']}" alt="{html.escape(n)}" width="200" height="200" loading="lazy"><h2>{html.escape(n)}</h2><p>Hubungi untuk harga</p><a class="btn" href="{wa}">Minta Penawaran</a><a class="alt" href="{p['url']}" rel="noopener">Lihat di Tokopedia<span class="sr"> : {html.escape(n)}</span></a></li>\n'''

css = '''.cat{padding-block:clamp(2.5rem,6vw,4.5rem)}
.cat h1{font-size:clamp(2.25rem,4.5vw,3.5rem)}.cat .lead{color:var(--muted);margin-top:.75rem;max-width:60ch}
.cat label{display:block;margin-top:1.75rem;font-weight:600;color:var(--navy)}
.cat input{display:block;width:min(100%,420px);min-height:48px;margin-top:.4rem;padding:0 1rem;border:1.5px solid var(--navy);border-radius:2px;font:inherit}
.grid{list-style:none;padding:0;margin-top:2rem;display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:1.25rem}
.card{display:flex;flex-direction:column;gap:.5rem;border:1px solid var(--line);padding:1rem}
.card[hidden]{display:none}
.card img{width:100%;height:auto;aspect-ratio:1;object-fit:contain;background:var(--mist)}
.card h2{font:600 1.0625rem/1.3 var(--serif);color:var(--navy)}
.card p{font-size:.875rem;color:var(--muted)}
.card .btn{margin-top:auto;justify-content:center;white-space:nowrap;padding-inline:1rem}
.card .alt{display:inline-flex;align-items:center;min-height:44px;font-size:.875rem;color:var(--navy)}
.sr{position:absolute;left:-9999px}
#empty{margin-top:2rem;color:var(--muted)}
'''
main = f'''<main id="main"><section class="cat"><div class="wrap">
<h1>Produk</h1>
<p class="lead">Perlengkapan medis dan habis pakai yang tersedia melalui Ofamed. Harga dan ketersediaan, silakan tanyakan lewat WhatsApp.</p>
<label for="q">Cari produk</label><input id="q" type="search" autocomplete="off">
<p id="empty" role="status" hidden>Produk tidak ditemukan. Hubungi kami, kami bantu carikan.</p>
<ul class="grid">
{cards}</ul>
</div></section></main>
<script>
const q=document.getElementById('q'),cs=[...document.querySelectorAll('.card')],em=document.getElementById('empty');
q.addEventListener('input',()=>{{const v=q.value.trim().toLowerCase();let n=0;for(const c of cs){{const h=!c.dataset.name.includes(v);c.hidden=h;n+=!h}}em.hidden=n>0}});
</script>'''

a, b = s.index('<main'), s.index('</main>') + 7
out = s[:a] + main + s[b:]
# drop index-only script (reel) and fix nav state
out = re.sub(r'<script>\n// auto-advance.*?</script>\n', '', out, flags=re.S)
out = out.replace('<li><a href="index.html" aria-current="page">Beranda</a></li><li><a href="produk.html">', '<li><a href="index.html">Beranda</a></li><li><a href="produk.html" aria-current="page">')
out = out.replace('</style>', css + '</style>', 1)
out = re.sub(r'<title>.*?</title>', '<title>Produk | Ofamed</title>', out)
assert 'aria-current="page">Produk' in out and out.count('<main') == 1
open('produk.html', 'w', encoding='utf-8').write(out)
print(len(P), 'products')
