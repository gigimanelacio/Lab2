import re

file_path = "wireless-festival.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add logic to carregarDados() to populate demo RFIDs dynamically
injection = """
        // Populate real RFIDs for demo
        const cont = document.querySelector('.demo-tickets');
        if (cont && bData.length > 0) {
           const rfidAtivo = bData.find(b => b.estado === 'Ativo')?.rfid;
           const rfidUtilizado = bData.find(b => b.estado === 'Utilizado')?.rfid;
           const rfidReembolsado = bData.find(b => b.estado === 'Reembolsado')?.rfid;
           
           cont.innerHTML = `
             ${rfidAtivo ? `<div class="ticket-chip valid" onclick="loadRfid('${rfidAtivo}')"><div class="chip-status green"></div>${rfidAtivo} (Ativo)</div>` : ''}
             ${rfidUtilizado ? `<div class="ticket-chip paid" onclick="loadRfid('${rfidUtilizado}')"><div class="chip-status amber"></div>${rfidUtilizado} (Utilizado)</div>` : ''}
             ${rfidReembolsado ? `<div class="ticket-chip refund" onclick="loadRfid('${rfidReembolsado}')"><div class="chip-status red"></div>${rfidReembolsado} (Reembolsado)</div>` : ''}
           `;
        }
        
        updateUI(entrou, reimb, sumVal, vData, vData.slice(0, 5));
"""
content = content.replace("updateUI(entrou, reimb, sumVal, vData, vData.slice(0, 5));", injection.strip())


# 2. Update simularScan() logic to check for cancelled artists
old_simular = """
      if (estado === 'Reembolsado') {
        res.className = 'scan-result denied';
        res.innerHTML = `<div><div class="result-icon">🚫</div><div style="font-size:20px;font-weight:700;letter-spacing:.1em">ACESSO NEGADO</div><div style="margin-top:6px;font-size:12px">Bilhete reembolsado após cancelamento do artista</div><div class="result-code">estado = 'Reembolsado' — RFID na blacklist local</div></div>`;
      } else if (estado === 'Utilizado') {
        res.className = 'scan-result denied';
        res.innerHTML = `<div><div class="result-icon">⚠️</div><div>DUPLA ENTRADA DETETADA</div><div style="margin-top:6px;font-size:12px">Esta pulseira já entrou no recinto</div><div class="result-code">estado = 'Utilizado' — entrada já registada</div></div>`;
      } else {
        res.className = 'scan-result granted';
        res.innerHTML = `<div><div class="result-icon" style="color:var(--green)">✅</div><div style="font-size:20px;font-weight:700;letter-spacing:.1em">ACESSO PERMITIDO</div><div style="margin-top:6px;font-size:12px">A registar entrada na tabela VALIDACOES...</div><div class="result-code">UPDATE bilhetes SET estado='Utilizado' WHERE rfid='${rfid}'</div></div>`;
      }
"""

new_simular = """
      if (estado === 'Reembolsado') {
        res.className = 'scan-result denied';
        res.innerHTML = `<div><div class="result-icon">🚫</div><div style="font-size:20px;font-weight:700;letter-spacing:.1em">ACESSO NEGADO</div><div style="margin-top:6px;font-size:12px">Bilhete reembolsado após cancelamento do artista</div><div class="result-code">estado = 'Reembolsado' — RFID na blacklist local</div></div>`;
      } else if (estado === 'Utilizado') {
        res.className = 'scan-result denied';
        res.innerHTML = `<div><div class="result-icon">⚠️</div><div>DUPLA ENTRADA DETETADA</div><div style="margin-top:6px;font-size:12px">Esta pulseira já entrou no recinto</div><div class="result-code">estado = 'Utilizado' — entrada já registada</div></div>`;
      } else {
        // Verificar se há artistas cancelados
        let cancelados = [];
        try {
           const { data } = await sb.from('concertos').select('*, artistas(nome)').eq('estado', 'Cancelado');
           cancelados = data || [];
        } catch(e) {}
        
        if (cancelados.length > 0) {
           const nomes = cancelados.map(c => c.artistas?.nome || 'Artista').join(', ');
           res.className = 'scan-result';
           res.style.background = 'rgba(254, 188, 46, 0.1)';
           res.style.borderColor = 'var(--amber)';
           res.innerHTML = `<div><div class="result-icon" style="color:var(--amber)">⚠️</div><div style="font-size:20px;font-weight:700;letter-spacing:.1em;color:var(--amber)">ALERTA DE CANCELAMENTO</div><div style="margin-top:6px;font-size:12px;color:var(--text)">Atenção: O(s) artista(s) <b>${nomes}</b> cancelaram a atuação.<br>O cliente tem direito a pedir reembolso do bilhete (e saldo cashless) em vez de entrar.<br><br><button onclick="document.getElementById('scan-result').innerHTML='<div><div class=\\'result-icon\\' style=\\'color:var(--green)\\'>💸</div><div style=\\'font-size:20px;font-weight:700;letter-spacing:.1em\\'>REEMBOLSO PROCESSADO</div><div style=\\'margin-top:6px;font-size:12px\\'>Pulseira inativada e fundos devolvidos.</div></div>'" style="background:var(--red);color:white;border:none;padding:8px 12px;border-radius:4px;cursor:pointer;margin-right:10px;font-weight:bold">Pedir Reembolso</div> <button onclick="document.getElementById('scan-result').innerHTML='<div><div class=\\'result-icon\\' style=\\'color:var(--green)\\'>✅</div><div style=\\'font-size:20px;font-weight:700;letter-spacing:.1em\\'>ACESSO PERMITIDO</div><div style=\\'margin-top:6px;font-size:12px\\'>O cliente abdicou do reembolso e decidiu entrar.</div></div>'" style="background:var(--green);color:white;border:none;padding:8px 12px;border-radius:4px;cursor:pointer;font-weight:bold">Entrar Mesmo Assim</button></div><div class="result-code">SELECT * FROM concertos WHERE estado = 'Cancelado'</div></div>`;
        } else {
           res.className = 'scan-result granted';
           res.style = '';
           res.innerHTML = `<div><div class="result-icon" style="color:var(--green)">✅</div><div style="font-size:20px;font-weight:700;letter-spacing:.1em">ACESSO PERMITIDO</div><div style="margin-top:6px;font-size:12px">A registar entrada na tabela VALIDACOES...</div><div class="result-code">UPDATE bilhetes SET estado='Utilizado' WHERE rfid='${rfid}'</div></div>`;
        }
      }
"""

content = content.replace(old_simular.strip(), new_simular.strip())

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("done")
