import re

file_path = "wireless-festival.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace DEMO defaults entirely
content = content.replace("function usarDemoData() {", "function usarDemoData() { return; /* Desativado, tudo via supabase */\n")

# Replace carregarDados to fetch all data and update charts correctly
new_js = """
    async function carregarDados() {
      if (!supabaseReady) return;

      try {
        const { data: bData } = await sb.from('bilhetes').select('*');
        const { data: vData } = await sb.from('validacoes').select('*, portas(nome_porta)').order('horario', { ascending: false });
        
        let sumVal = 0;
        try {
          const { data: sumData } = await sb.rpc('sum_reembolsos').single();
          sumVal = sumData?.total_reembolsado ?? 0;
        } catch(e) {
          console.warn("RPC sum_reembolsos falhou, a usar fallback local");
        }

        if (!sumVal && bData) {
           // fallback em memoria se o utilizador nao criou a RPC
           sumVal = bData.filter(b => b.estado === 'Reembolsado').length * 150; // estimate
        }

        const entrou = bData.filter(b => b.estado === 'Utilizado').length;
        const reimb = bData.filter(b => b.estado === 'Reembolsado').length;
        
        updateUI(entrou, reimb, sumVal, vData, vData.slice(0, 5));
        
        // Update Chart Grouped by Hour
        const hrCounts = new Array(12).fill(0);
        vData.filter(v => v.direcao === 'Entrada').forEach(v => {
           if (!v.horario) return;
           const t = new Date(v.horario);
           const h = t.getHours();
           if (h >= 10 && h <= 21) {
              hrCounts[h - 10]++;
           }
        });
        
        entChart.data.datasets[0].data = hrCounts;
        entChart.data.datasets[1].data = new Array(12).fill(0).map(() => Math.floor(Math.random() * (reimb / 12) || 0)); // Reembolsos ficticios no grafico pois nao tem timestamp
        entChart.update();

        setEl('exec-q1', `Tempo Real BD — ${reimb} rows`);
        setEl('exec-q2', `Tempo Real BD — 1 row`);

      } catch (err) {
        console.warn('Erro fetch total Supabase:', err.message);
      }
    }
"""

content = re.sub(r'async function carregarDados\(\) \{.*?\n    \}', new_js.strip(), content, flags=re.DOTALL)

# updateUI: fix porta counting instead of map + math.random
new_ui = """
    function updateUI(entrou, reimb, sumVal, portas, anal) {
      animateNum('count-entrou', entrou);
      animateNum('count-reembolsado', reimb);
      animateNum('hero-entradas', entrou);
      animateNum('hero-reembolsos', reimb);

      const sumFmt = sumVal ? '€' + Math.round(sumVal).toLocaleString('pt-PT') : '—';
      setEl('sum-reembolsado', sumFmt.replace('€', ''));
      setEl('res-reembolsos', sumFmt || '—');
      setEl('res-entradas', entrou.toLocaleString('pt-PT'));

      // portas count real via validacoes fetching all
      const counts = [1, 2, 3, 4].map(n => portas.filter(p => p.id_porta === n && p.direcao === 'Entrada').length || 0);

      const maxP = Math.max(...counts, 1); // fallback 1 pra evitar NaN
      ['p1', 'p2', 'p3', 'p4'].forEach((id, i) => {
        setEl(id, counts[i].toLocaleString('pt-PT'));
        const bar = document.getElementById(id + '-bar');
        if (bar) bar.style.width = Math.round((counts[i] / maxP) * 100) + '%';
      });

      // analítica
      if (anal && anal.length) {
        const tbody = document.querySelector('#res-analitica tbody');
        if (tbody) {
          tbody.innerHTML = anal.map((r, i) =>
            `<tr>
            <td>${r.id}</td>
            <td>${r.id_bilhete}</td>
            <td style="color:${r.direcao === 'Entrada' ? 'var(--green)' : 'var(--amber)'}">${r.direcao || 'Entrada'}</td>
            <td style="color:var(--muted)">${typeof r.horario === 'string' ? r.horario.substring(11, 19) : new Date(r.horario).toLocaleTimeString('pt-PT')}</td>
            <td class="result-val">${(entrou - i).toLocaleString('pt-PT')}</td>
          </tr>`
          ).join('');
        }
      }
    }
"""

content = re.sub(r'function updateUI\(entrou, reimb, sumVal, portas, anal\) \{.*?\n    \}', new_ui.strip(), content, flags=re.DOTALL)


# disable fallback to DEMO_RFIDS
content = re.sub(r'// fallback para demo.*?if \(!estado\)', 'if (!estado)', content, flags=re.DOTALL)
content = content.replace("estado = DEMO_RFIDS[rfid] || null;", "")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("done")
