import re

file_path = "wireless-festival.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. HTML Replacement
old_html = """<style>
.demo-table-container { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 8px; margin-bottom: 24px; }
.demo-col h4 { font-size: 10px; color: var(--muted); margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; }
.demo-col .ticket-chip { margin-right: 0; margin-bottom: 4px; width: 100%; box-sizing: border-box; justify-content: flex-start; padding: 4px 8px; font-size: 11px; }
</style>
        <div class="demo-table-container" id="demo-table-container">
          <!-- Filled by JS -->
        </div>"""

new_html = """<style>
.demo-scroll-list { display: flex; overflow-x: auto; gap: 8px; margin-bottom: 12px; padding-bottom: 8px; scrollbar-width: thin; scrollbar-color: rgba(255,255,255,0.2) transparent; }
.demo-scroll-list::-webkit-scrollbar { height: 6px; }
.demo-scroll-list::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 4px; }
.demo-scroll-list .ticket-chip { flex: 0 0 auto; margin-right: 0; padding: 4px 10px; font-size: 11px; }
.demo-legend { display: flex; flex-wrap: wrap; gap: 12px; font-size: 11px; color: var(--muted); margin-bottom: 24px; }
.legend-item { display: flex; align-items: center; gap: 6px; }
</style>
        <div class="demo-scroll-list" id="demo-table-container">
          <!-- Filled by JS -->
        </div>
        <div class="demo-legend">
          <div class="legend-item"><div class="chip-status green"></div> Válido</div>
          <div class="legend-item"><div class="chip-status amber"></div> Usado</div>
          <div class="legend-item"><div class="chip-status red"></div> Reemb.</div>
          <div class="legend-item"><div class="chip-status amber" style="background:transparent;border:2px solid var(--amber)"></div> Canc.</div>
        </div>"""

if old_html in content:
    content = content.replace(old_html, new_html)
else:
    print("Warning: old HTML block not found")

# 2. JS Replacement
old_js = """           cont.innerHTML = `
             <div class="demo-col"><h4>Válidos</h4>
               ${ativosNormais.map(b => `<div class="ticket-chip valid" id="chip-${b.rfid}" onclick="loadRfid('${b.rfid}')"><div class="chip-status green"></div>${b.rfid}</div>`).join('')}
             </div>
             <div class="demo-col"><h4>Usados</h4>
               ${utilizados.map(b => `<div class="ticket-chip paid" id="chip-${b.rfid}" onclick="loadRfid('${b.rfid}')"><div class="chip-status amber"></div>${b.rfid}</div>`).join('')}
             </div>
             <div class="demo-col"><h4>Reembolsados</h4>
               ${reembolsados.map(b => `<div class="ticket-chip refund" id="chip-${b.rfid}" onclick="loadRfid('${b.rfid}')"><div class="chip-status red"></div>${b.rfid}</div>`).join('')}
             </div>
             <div class="demo-col"><h4>Cancelados</h4>
               ${ativosCancelados.map(b => `<div class="ticket-chip" id="chip-${b.rfid}" style="background:rgba(254,188,46,0.1);border-color:var(--amber);color:var(--amber);cursor:pointer" onclick="loadRfid('${b.rfid}')"><div class="chip-status amber"></div>${b.rfid}</div>`).join('')}
             </div>
           `;"""

new_js = """           // Flat list para o scroll horizontal
           const itemsHTML = [
               ...ativosNormais.map(b => `<div class="ticket-chip valid" id="chip-${b.rfid}" onclick="loadRfid('${b.rfid}')"><div class="chip-status green"></div>${b.rfid}</div>`),
               ...utilizados.map(b => `<div class="ticket-chip paid" id="chip-${b.rfid}" onclick="loadRfid('${b.rfid}')"><div class="chip-status amber"></div>${b.rfid}</div>`),
               ...reembolsados.map(b => `<div class="ticket-chip refund" id="chip-${b.rfid}" onclick="loadRfid('${b.rfid}')"><div class="chip-status red"></div>${b.rfid}</div>`),
               ...ativosCancelados.map(b => `<div class="ticket-chip" id="chip-${b.rfid}" style="background:rgba(254,188,46,0.1);border-color:var(--amber);color:var(--amber);cursor:pointer" onclick="loadRfid('${b.rfid}')"><div class="chip-status amber" style="background:transparent;border:2px solid var(--amber)"></div>${b.rfid}</div>`)
           ].join('');
           cont.innerHTML = itemsHTML;"""

if old_js in content:
    content = content.replace(old_js, new_js)
else:
    print("Warning: old JS block not found")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updates applied.")
