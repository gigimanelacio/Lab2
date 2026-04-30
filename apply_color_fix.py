import re

file_path = "wireless-festival.html"
with open(file_path, "r", encoding="utf-8") as f:
    c = f.read()

replacement1 = r"""res.innerHTML = `<div><div class="result-icon">⌛</div><div>A processar na BD...</div></div>`;
       
       // Mudança visual da tag na tabela
       const chip = document.getElementById(`chip-${rfid}`);
       if (chip) {
           chip.className = 'ticket-chip paid';
           chip.style = '';
           const dot = chip.querySelector('.chip-status');
           if (dot) dot.className = 'chip-status amber';
       }"""
c = re.sub(r'res\.innerHTML = `<div><div class="result-icon">⌛</div><div>A processar na BD\.\.\.</div></div>`;', replacement1, c, count=1)

replacement2 = r"""res.innerHTML = `<div><div class="result-icon">⌛</div><div>A processar reembolso...</div></div>`;
       
       // Mudança visual da tag na tabela
       const chip = document.getElementById(`chip-${rfid}`);
       if (chip) {
           chip.className = 'ticket-chip refund';
           chip.style = '';
           const dot = chip.querySelector('.chip-status');
           if (dot) dot.className = 'chip-status red';
       }"""
c = re.sub(r'res\.innerHTML = `<div><div class="result-icon">⌛</div><div>A processar reembolso\.\.\.</div></div>`;', replacement2, c, count=1)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(c)

print("done")
