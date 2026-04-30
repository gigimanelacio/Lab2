import re

file_path = "wireless-festival.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update HTML structure for demo-tickets
old_demo_tickets = r'<div class="demo-tickets">.*?</div>'
new_demo_tickets = """
<style>
.demo-table-container { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 8px; margin-bottom: 24px; }
.demo-col h4 { font-size: 10px; color: var(--muted); margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; }
.demo-col .ticket-chip { margin-right: 0; margin-bottom: 4px; width: 100%; box-sizing: border-box; justify-content: flex-start; padding: 4px 8px; font-size: 11px; }
</style>
<div class="demo-table-container" id="demo-table-container">
  <!-- Filled by JS -->
</div>
"""
# Replace the old container
if 'id="demo-table-container"' not in content:
    content = re.sub(old_demo_tickets, new_demo_tickets, content, flags=re.DOTALL)

# 2. Update carregarDados() injection to fill the 4 columns
old_injection = r'const cont = document\.querySelector\(\'\.demo-tickets\'\);.*?updateUI\(entrou, reimb, sumVal, vData, vData\.slice\(0, 5\)\);'
new_injection = """
        const cont = document.getElementById('demo-table-container');
        if (cont && bData.length > 0) {
           const ativosNormais = bData.filter(b => b.estado === 'Ativo' && b.id_tipo_bilhete !== 3).slice(0, 3);
           const ativosCancelados = bData.filter(b => b.estado === 'Ativo' && b.id_tipo_bilhete === 3).slice(0, 3);
           const utilizados = bData.filter(b => b.estado === 'Utilizado').slice(0, 3);
           const reembolsados = bData.filter(b => b.estado === 'Reembolsado').slice(0, 3);
           
           cont.innerHTML = `
             <div class="demo-col"><h4>Válidos</h4>
               ${ativosNormais.map(b => `<div class="ticket-chip valid" onclick="loadRfid('${b.rfid}')"><div class="chip-status green"></div>${b.rfid}</div>`).join('')}
             </div>
             <div class="demo-col"><h4>Usados</h4>
               ${utilizados.map(b => `<div class="ticket-chip paid" onclick="loadRfid('${b.rfid}')"><div class="chip-status amber"></div>${b.rfid}</div>`).join('')}
             </div>
             <div class="demo-col"><h4>Reembolsados</h4>
               ${reembolsados.map(b => `<div class="ticket-chip refund" onclick="loadRfid('${b.rfid}')"><div class="chip-status red"></div>${b.rfid}</div>`).join('')}
             </div>
             <div class="demo-col"><h4>Cancelados</h4>
               ${ativosCancelados.map(b => `<div class="ticket-chip" style="background:rgba(254,188,46,0.1);border-color:var(--amber);color:var(--amber)" onclick="loadRfid('${b.rfid}')"><div class="chip-status amber"></div>${b.rfid}</div>`).join('')}
             </div>
           `;
        }
        
        updateUI(entrou, reimb, sumVal, vData, vData.slice(0, 5));
"""
content = re.sub(old_injection, new_injection.strip(), content, flags=re.DOTALL)


# 3. Update simularScan() to fetch ticket details and use id_tipo_bilhete
old_scan_start = r'const { data } = await sb\.from\(\'bilhetes\'\)\.select\(\'estado\'\)\.eq\(\'rfid\', rfid\)\.single\(\);[\s\S]*?estado = data\?\.estado;'
new_scan_start = """
          const { data } = await sb.from('bilhetes').select('estado, id_tipo_bilhete').eq('rfid', rfid).single();
          estado = data?.estado;
          var tipoBilhete = data?.id_tipo_bilhete;
"""
content = re.sub(old_scan_start, new_scan_start.strip(), content)

old_simular = r'if \(estado === \'Reembolsado\'\) \{[\s\S]*?\}'
new_simular = """
      if (estado === 'Reembolsado') {
        res.className = 'scan-result denied';
        res.innerHTML = `<div><div class="result-icon">🚫</div><div style="font-size:20px;font-weight:700;letter-spacing:.1em">ACESSO NEGADO</div><div style="margin-top:6px;font-size:12px">Bilhete reembolsado após cancelamento do artista</div><div class="result-code">estado = 'Reembolsado' — RFID na blacklist local</div></div>`;
      } else if (estado === 'Utilizado') {
        res.className = 'scan-result denied';
        res.innerHTML = `<div><div class="result-icon">⚠️</div><div>DUPLA ENTRADA DETETADA</div><div style="margin-top:6px;font-size:12px">Esta pulseira já entrou no recinto</div><div class="result-code">estado = 'Utilizado' — entrada já registada</div></div>`;
      } else {
        // Se id_tipo_bilhete === 3, é o bilhete com o concerto cancelado
        if (tipoBilhete === 3) {
           res.className = 'scan-result';
           res.style.background = 'rgba(254, 188, 46, 0.1)';
           res.style.borderColor = 'var(--amber)';
           res.innerHTML = `<div><div class="result-icon" style="color:var(--amber)">⚠️</div><div style="font-size:20px;font-weight:700;letter-spacing:.1em;color:var(--amber)">ALERTA DE CANCELAMENTO</div><div style="margin-top:6px;font-size:12px;color:var(--text)">Atenção: O artista principal <b>Kanye West</b> cancelou a atuação para este dia.<br>O cliente tem direito a pedir reembolso do bilhete em vez de entrar.<br><br><button onclick="document.getElementById('scan-result').innerHTML='<div><div class=\\'result-icon\\' style=\\'color:var(--green)\\'>💸</div><div style=\\'font-size:20px;font-weight:700;letter-spacing:.1em\\'>REEMBOLSO PROCESSADO</div><div style=\\'margin-top:6px;font-size:12px\\'>Pulseira inativada e fundos devolvidos.</div></div>'" style="background:var(--red);color:white;border:none;padding:8px 12px;border-radius:4px;cursor:pointer;margin-right:10px;font-weight:bold">Pedir Reembolso</button> <button onclick="document.getElementById('scan-result').innerHTML='<div><div class=\\'result-icon\\' style=\\'color:var(--green)\\'>✅</div><div style=\\'font-size:20px;font-weight:700;letter-spacing:.1em\\'>ACESSO PERMITIDO</div><div style=\\'margin-top:6px;font-size:12px\\'>O cliente abdicou do reembolso e decidiu entrar.</div></div>'" style="background:var(--green);color:white;border:none;padding:8px 12px;border-radius:4px;cursor:pointer;font-weight:bold">Entrar Mesmo Assim</button></div><div class="result-code">id_tipo_bilhete = 3 — Afetado por Cancelamento</div></div>`;
        } else {
           res.className = 'scan-result granted';
           res.style = '';
           res.innerHTML = `<div><div class="result-icon" style="color:var(--green)">✅</div><div style="font-size:20px;font-weight:700;letter-spacing:.1em">ACESSO PERMITIDO</div><div style="margin-top:6px;font-size:12px">A registar entrada na tabela VALIDACOES...</div><div class="result-code">UPDATE bilhetes SET estado='Utilizado' WHERE rfid='${rfid}'</div></div>`;
        }
      }
"""

content = re.sub(old_simular, new_simular.strip(), content, flags=re.DOTALL)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("done")
