import re

file_path = "wireless-festival.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update carregarDados() to add IDs to chips and prevent re-rendering
old_demo_js = """        const cont = document.getElementById('demo-table-container');
        if (cont && bData.length > 0) {"""

new_demo_js = """        const cont = document.getElementById('demo-table-container');
        // Só povoar a tabela de demo na primeira vez para os bilhetes não saltarem de coluna em realtime
        if (cont && !cont.hasAttribute('data-loaded') && bData.length > 0) {
           cont.setAttribute('data-loaded', 'true');"""

if old_demo_js in content:
    content = content.replace(old_demo_js, new_demo_js)

# Add id="chip-${b.rfid}" to all chips
# Válidos
content = content.replace(
    """<div class="ticket-chip valid" onclick="loadRfid('${b.rfid}')"><div class="chip-status green"></div>${b.rfid}</div>""",
    """<div class="ticket-chip valid" id="chip-${b.rfid}" onclick="loadRfid('${b.rfid}')"><div class="chip-status green"></div>${b.rfid}</div>"""
)
# Usados
content = content.replace(
    """<div class="ticket-chip paid" onclick="loadRfid('${b.rfid}')"><div class="chip-status amber"></div>${b.rfid}</div>""",
    """<div class="ticket-chip paid" id="chip-${b.rfid}" onclick="loadRfid('${b.rfid}')"><div class="chip-status amber"></div>${b.rfid}</div>"""
)
# Reembolsados
content = content.replace(
    """<div class="ticket-chip refund" onclick="loadRfid('${b.rfid}')"><div class="chip-status red"></div>${b.rfid}</div>""",
    """<div class="ticket-chip refund" id="chip-${b.rfid}" onclick="loadRfid('${b.rfid}')"><div class="chip-status red"></div>${b.rfid}</div>"""
)
# Cancelados
content = content.replace(
    """<div class="ticket-chip" style="background:rgba(254,188,46,0.1);border-color:var(--amber);color:var(--amber);cursor:pointer" onclick="loadRfid('${b.rfid}')"><div class="chip-status amber"></div>${b.rfid}</div>""",
    """<div class="ticket-chip" id="chip-${b.rfid}" style="background:rgba(254,188,46,0.1);border-color:var(--amber);color:var(--amber);cursor:pointer" onclick="loadRfid('${b.rfid}')"><div class="chip-status amber"></div>${b.rfid}</div>"""
)


# 2. Update processarEntrada and processarReembolso to change DOM classes
old_processar = """    window.processarEntrada = async function(rfid) {
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
    };"""

new_processar = """    window.processarEntrada = async function(rfid) {
       // Atualizar UI imediatamente para loading
       const res = document.getElementById('scan-result');
       res.innerHTML = `<div><div class="result-icon">⌛</div><div>A processar na BD...</div></div>`;
       
       // Mudança visual da tag na tabela
       const chip = document.getElementById(`chip-${rfid}`);
       if (chip) {
           chip.className = 'ticket-chip paid';
           chip.style = ''; // Limpar estilos inline (como os do Cancelado)
           const dot = chip.querySelector('.chip-status');
           if (dot) dot.className = 'chip-status amber';
       }

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
       
       // Mudança visual da tag na tabela
       const chip = document.getElementById(`chip-${rfid}`);
       if (chip) {
           chip.className = 'ticket-chip refund';
           chip.style = '';
           const dot = chip.querySelector('.chip-status');
           if (dot) dot.className = 'chip-status red';
       }

       await sb.from('bilhetes').update({ estado: 'Reembolsado' }).eq('rfid', rfid);
       
       res.className = 'scan-result denied';
       res.style = '';
       res.innerHTML = `<div><div class="result-icon" style="color:var(--green)">💸</div><div style="font-size:20px;font-weight:700;letter-spacing:.1em">REEMBOLSO EFETUADO NA BD</div><div style="margin-top:6px;font-size:12px">O bilhete foi marcado como 'Reembolsado' com sucesso.</div></div>`;
    };"""

if old_processar in content:
    content = content.replace(old_processar, new_processar)
else:
    print("Warning: old_processar not found! Regex or exact match failed.")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Color update logic applied.")
