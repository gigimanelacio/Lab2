import re

file_path = "wireless-festival.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add global functions processarEntrada and processarReembolso just before simularScan
new_functions = """
    window.processarEntrada = async function(rfid) {
       // Atualizar UI imediatamente para loading
       const res = document.getElementById('scan-result');
       res.innerHTML = `<div><div class="result-icon">⌛</div><div>A processar na BD...</div></div>`;
       
       // 1. Alterar estado do bilhete
       await sb.from('bilhetes').update({ estado: 'Utilizado' }).eq('rfid', rfid);
       
       // 2. Registar validacao
       const { data: b } = await sb.from('bilhetes').select('id').eq('rfid', rfid).single();
       if (b) {
           await sb.from('validacoes').insert({ id_bilhete: b.id, id_porta: 1, direcao: 'Entrada' });
       }
       
       res.className = 'scan-result granted';
       res.style = '';
       res.innerHTML = `<div><div class="result-icon" style="color:var(--green)">✅</div><div style="font-size:20px;font-weight:700;letter-spacing:.1em">ACESSO REGISTADO NA BD</div><div style="margin-top:6px;font-size:12px">Bilhete alterado para 'Utilizado' e Validação inserida.</div></div>`;
    };

    window.processarReembolso = async function(rfid) {
       const res = document.getElementById('scan-result');
       res.innerHTML = `<div><div class="result-icon">⌛</div><div>A processar reembolso...</div></div>`;
       
       await sb.from('bilhetes').update({ estado: 'Reembolsado' }).eq('rfid', rfid);
       
       res.className = 'scan-result denied';
       res.style = '';
       res.innerHTML = `<div><div class="result-icon" style="color:var(--green)">💸</div><div style="font-size:20px;font-weight:700;letter-spacing:.1em">REEMBOLSO EFETUADO NA BD</div><div style="margin-top:6px;font-size:12px">O bilhete foi marcado como 'Reembolsado' com sucesso.</div></div>`;
    };

    async function simularScan() {
"""

content = content.replace("    async function simularScan() {", new_functions.strip())


# 2. Update simularScan logic to call these functions
old_buttons = """<button onclick="document.getElementById('scan-result').innerHTML='<div><div class=\\'result-icon\\' style=\\'color:var(--green)\\'>💸</div><div style=\\'font-size:20px;font-weight:700;letter-spacing:.1em\\'>REEMBOLSO PROCESSADO</div><div style=\\'margin-top:6px;font-size:12px\\'>Pulseira inativada e fundos devolvidos.</div></div>'" style="background:var(--red);color:white;border:none;padding:8px 12px;border-radius:4px;cursor:pointer;margin-right:10px;font-weight:bold">Pedir Reembolso</div> <button onclick="document.getElementById('scan-result').innerHTML='<div><div class=\\'result-icon\\' style=\\'color:var(--green)\\'>✅</div><div style=\\'font-size:20px;font-weight:700;letter-spacing:.1em\\'>ACESSO PERMITIDO</div><div style=\\'margin-top:6px;font-size:12px\\'>O cliente abdicou do reembolso e decidiu entrar.</div></div>'" style="background:var(--green);color:white;border:none;padding:8px 12px;border-radius:4px;cursor:pointer;font-weight:bold">Entrar Mesmo Assim</button>"""

new_buttons = """<button onclick="window.processarReembolso('${rfid}')" style="background:var(--red);color:white;border:none;padding:8px 12px;border-radius:4px;cursor:pointer;margin-right:10px;font-weight:bold">Pedir Reembolso</button> <button onclick="window.processarEntrada('${rfid}')" style="background:var(--green);color:white;border:none;padding:8px 12px;border-radius:4px;cursor:pointer;font-weight:bold">Entrar Mesmo Assim</button>"""

content = content.replace(old_buttons, new_buttons)

# Fix the normal "ACESSO PERMITIDO" to actually trigger processarEntrada(rfid) automatically
old_granted = """           res.className = 'scan-result granted';
           res.style = '';
           res.innerHTML = `<div><div class="result-icon" style="color:var(--green)">✅</div><div style="font-size:20px;font-weight:700;letter-spacing:.1em">ACESSO PERMITIDO</div><div style="margin-top:6px;font-size:12px">A registar entrada na tabela VALIDACOES...</div><div class="result-code">UPDATE bilhetes SET estado='Utilizado' WHERE rfid='${rfid}'</div></div>`;"""

new_granted = """           res.className = 'scan-result granted';
           res.style = '';
           res.innerHTML = `<div><div class="result-icon" style="color:var(--green)">✅</div><div style="font-size:20px;font-weight:700;letter-spacing:.1em">ACESSO PERMITIDO</div><div style="margin-top:6px;font-size:12px">A registar entrada na tabela VALIDACOES...</div><div class="result-code">UPDATE bilhetes SET estado='Utilizado' WHERE rfid='${rfid}'</div></div>`;
           // Realizar o registo automaticamente na BD se não for cancelado:
           await window.processarEntrada(rfid);"""

content = content.replace(old_granted, new_granted)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updates applied to simularScan")
