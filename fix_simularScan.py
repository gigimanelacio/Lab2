import re

file_path = "wireless-festival.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

new_simular_scan = """    async function simularScan() {
      const rfid = document.getElementById('rfid-field').value.trim();
      const res = document.getElementById('scan-result');
      if (!rfid) return;

      // estado de checking
      res.className = 'scan-result checking';
      res.innerHTML = `<div><div class="result-icon">⌛</div><div>A verificar no sistema...</div><div class="result-code">QUERY: SELECT estado FROM bilhetes WHERE rfid = '${rfid}'</div></div>`;

      await new Promise(r => setTimeout(r, 900));

      let estado = null;
      let tipoBilhete = null;

      if (supabaseReady) {
        try {
          const { data } = await sb.from('bilhetes').select('estado, id_tipo_bilhete').eq('rfid', rfid).single();
          estado = data?.estado;
          tipoBilhete = data?.id_tipo_bilhete;
        } catch (e) { /* fallback para demo */ }
      }

      if (!estado) {
        res.className = 'scan-result denied';
        res.innerHTML = `<div><div class="result-icon">🚫</div><div>BILHETE NÃO ENCONTRADO</div><div class="result-code">RFID desconhecido no sistema</div></div>`;
        return;
      }

      if (estado === 'Reembolsado') {
        res.className = 'scan-result denied';
        res.innerHTML = `<div><div class="result-icon">🚫</div><div style="font-size:20px;font-weight:700;letter-spacing:.1em">ACESSO NEGADO</div><div style="margin-top:6px;font-size:12px">Bilhete reembolsado após cancelamento do artista</div><div class="result-code">estado = 'Reembolsado' — RFID na blacklist local</div></div>`;
      } else if (estado === 'Utilizado') {
        res.className = 'scan-result denied';
        res.innerHTML = `<div><div class="result-icon">⚠️</div><div>DUPLA ENTRADA DETETADA</div><div style="margin-top:6px;font-size:12px">Esta pulseira já entrou no recinto</div><div class="result-code">estado = 'Utilizado' — entrada já registada</div></div>`;
      } else {
        // estado === 'Ativo'
        
        // Verifica se é o bilhete afetado pelo cancelamento (tipo 3 na nossa lógica)
        if (tipoBilhete === 3) {
           res.className = 'scan-result';
           res.style.background = 'rgba(254, 188, 46, 0.1)';
           res.style.borderColor = 'var(--amber)';
           res.innerHTML = `<div><div class="result-icon" style="color:var(--amber)">⚠️</div><div style="font-size:20px;font-weight:700;letter-spacing:.1em;color:var(--amber)">ALERTA DE CANCELAMENTO</div><div style="margin-top:6px;font-size:12px;color:var(--text)">Atenção: O artista principal cancelou a atuação para o dia deste bilhete.<br>O cliente tem direito a pedir reembolso.<br><br><button onclick="window.processarReembolso('${rfid}')" style="background:var(--red);color:white;border:none;padding:8px 12px;border-radius:4px;cursor:pointer;margin-right:10px;font-weight:bold">Pedir Reembolso</button> <button onclick="window.processarEntrada('${rfid}')" style="background:var(--green);color:white;border:none;padding:8px 12px;border-radius:4px;cursor:pointer;font-weight:bold">Entrar Mesmo Assim</button></div><div class="result-code">id_tipo_bilhete = 3 (Afetado por cancelamento)</div></div>`;
        } else {
           res.className = 'scan-result granted';
           res.style = '';
           res.innerHTML = `<div><div class="result-icon" style="color:var(--green)">✅</div><div style="font-size:20px;font-weight:700;letter-spacing:.1em">ACESSO PERMITIDO</div><div style="margin-top:6px;font-size:12px">A registar entrada na tabela VALIDACOES...</div><div class="result-code">UPDATE bilhetes SET estado='Utilizado' WHERE rfid='${rfid}'</div></div>`;
           // regista entrada real na BD
           await window.processarEntrada(rfid);
        }
      }
    }"""

# Extract from async function simularScan() { to // Enter no input faz scan
pattern = re.compile(r'    async function simularScan\(\) \{.*?\}(?=\s*// Enter no input faz scan)', re.DOTALL)

if pattern.search(content):
    content = pattern.sub(new_simular_scan, content)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("simularScan replaced successfully!")
else:
    print("Could not find the simularScan block!")
