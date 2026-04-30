file_path = "wireless-festival.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. HTML Replace
old_html = '''        <div class="demo-tickets">
          <div class="ticket-chip valid" onclick="loadRfid('RFID-VALID-001')">
            <div class="chip-status green"></div>RFID-VALID-001 (Ativo)
          </div>
          <div class="ticket-chip paid" onclick="loadRfid('RFID-PAID-002')">
            <div class="chip-status amber"></div>RFID-PAID-002 (Pago)
          </div>
          <div class="ticket-chip refund" onclick="loadRfid('RFID-REFUND-003')">
            <div class="chip-status red"></div>RFID-REFUND-003 (Reembolsado)
          </div>
        </div>'''
new_html = '''<style>
.demo-table-container { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 8px; margin-bottom: 24px; }
.demo-col h4 { font-size: 10px; color: var(--muted); margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; }
.demo-col .ticket-chip { margin-right: 0; margin-bottom: 4px; width: 100%; box-sizing: border-box; justify-content: flex-start; padding: 4px 8px; font-size: 11px; }
</style>
        <div class="demo-table-container" id="demo-table-container">
          <!-- Filled by JS -->
        </div>'''
content = content.replace(old_html, new_html)


# 2. JS carregarDados() Replace
old_js1 = '''        // Populate real RFIDs for demo
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
        }'''
new_js1 = '''        const cont = document.getElementById('demo-table-container');
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
               ${ativosCancelados.map(b => `<div class="ticket-chip" style="background:rgba(254,188,46,0.1);border-color:var(--amber);color:var(--amber);cursor:pointer" onclick="loadRfid('${b.rfid}')"><div class="chip-status amber"></div>${b.rfid}</div>`).join('')}
             </div>
           `;
        }'''
content = content.replace(old_js1, new_js1)


# 3. Add id_tipo_bilhete extraction
old_js2 = '''          const { data } = await sb.from('bilhetes').select('estado').eq('rfid', rfid).single();
          estado = data?.estado;'''
new_js2 = '''          const { data } = await sb.from('bilhetes').select('estado, id_tipo_bilhete').eq('rfid', rfid).single();
          estado = data?.estado;
          var tipoBilhete = data?.id_tipo_bilhete;'''
content = content.replace(old_js2, new_js2)


# 4. simularScan() logic replace
old_js3 = '''      } else {
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
           res.innerHTML = `<div><div class="result-icon" style="color:var(--amber)">⚠️</div><div style="font-size:20px;font-weight:700;letter-spacing:.1em;color:var(--amber)">ALERTA DE CANCELAMENTO</div><div style="margin-top:6px;font-size:12px;color:var(--text)">Atenção: O(s) artista(s) <b>${nomes}</b> cancelaram a atuação.<br>O cliente tem direito a pedir reembolso do bilhete (e saldo cashless) em vez de entrar.<br><br><button onclick="document.getElementById('scan-result').innerHTML='<div><div class=\\'result-icon\\' style=\\'color:var(--green)\\'>💸</div><div style=\\'font-size:20px;font-weight:700;letter-spacing:.1em\\'>REEMBOLSO PROCESSADO</div><div style=\\'margin-top:6px;font-size:12px\\'>Pulseira inativada e fundos devolvidos.</div></div>'" style="background:var(--red);color:white;border:none;padding:8px 12px;border-radius:4px;cursor:pointer;margin-right:10px;font-weight:bold">Pedir Reembolso</button> <button onclick="document.getElementById('scan-result').innerHTML='<div><div class=\\'result-icon\\' style=\\'color:var(--green)\\'>✅</div><div style=\\'font-size:20px;font-weight:700;letter-spacing:.1em\\'>ACESSO PERMITIDO</div><div style=\\'margin-top:6px;font-size:12px\\'>O cliente abdicou do reembolso e decidiu entrar.</div></div>'" style="background:var(--green);color:white;border:none;padding:8px 12px;border-radius:4px;cursor:pointer;font-weight:bold">Entrar Mesmo Assim</button></div><div class="result-code">SELECT * FROM concertos WHERE estado = 'Cancelado'</div></div>`;
        } else {
           res.className = 'scan-result granted';
           res.style = '';
           res.innerHTML = `<div><div class="result-icon" style="color:var(--green)">✅</div><div style="font-size:20px;font-weight:700;letter-spacing:.1em">ACESSO PERMITIDO</div><div style="margin-top:6px;font-size:12px">A registar entrada na tabela VALIDACOES...</div><div class="result-code">UPDATE bilhetes SET estado='Utilizado' WHERE rfid='${rfid}'</div></div>`;
        }
      }'''
new_js3 = '''      } else {
        // Usa o id_tipo_bilhete = 3 para simular o bilhete afetado por cancelamento
        if (tipoBilhete === 3) {
           res.className = 'scan-result';
           res.style.background = 'rgba(254, 188, 46, 0.1)';
           res.style.borderColor = 'var(--amber)';
           res.innerHTML = `<div><div class="result-icon" style="color:var(--amber)">⚠️</div><div style="font-size:20px;font-weight:700;letter-spacing:.1em;color:var(--amber)">ALERTA DE CANCELAMENTO</div><div style="margin-top:6px;font-size:12px;color:var(--text)">Atenção: O artista principal cancelou a atuação para o dia deste bilhete.<br>O cliente tem direito a pedir reembolso.<br><br><button onclick="document.getElementById('scan-result').innerHTML='<div><div class=\\'result-icon\\' style=\\'color:var(--green)\\'>💸</div><div style=\\'font-size:20px;font-weight:700;letter-spacing:.1em\\'>REEMBOLSO PROCESSADO</div><div style=\\'margin-top:6px;font-size:12px\\'>Pulseira inativada e fundos devolvidos.</div></div>'" style="background:var(--red);color:white;border:none;padding:8px 12px;border-radius:4px;cursor:pointer;margin-right:10px;font-weight:bold">Pedir Reembolso</button> <button onclick="document.getElementById('scan-result').innerHTML='<div><div class=\\'result-icon\\' style=\\'color:var(--green)\\'>✅</div><div style=\\'font-size:20px;font-weight:700;letter-spacing:.1em\\'>ACESSO PERMITIDO</div><div style=\\'margin-top:6px;font-size:12px\\'>O cliente abdicou do reembolso e decidiu entrar.</div></div>'" style="background:var(--green);color:white;border:none;padding:8px 12px;border-radius:4px;cursor:pointer;font-weight:bold">Entrar Mesmo Assim</button></div><div class="result-code">id_tipo_bilhete = 3 (Afetado por cancelamento)</div></div>`;
        } else {
           res.className = 'scan-result granted';
           res.style = '';
           res.innerHTML = `<div><div class="result-icon" style="color:var(--green)">✅</div><div style="font-size:20px;font-weight:700;letter-spacing:.1em">ACESSO PERMITIDO</div><div style="margin-top:6px;font-size:12px">A registar entrada na tabela VALIDACOES...</div><div class="result-code">UPDATE bilhetes SET estado='Utilizado' WHERE rfid='${rfid}'</div></div>`;
        }
      }'''
content = content.replace(old_js3, new_js3)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("HTML, UI Table and logic replaced.")
