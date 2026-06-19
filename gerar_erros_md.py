import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('qwen_errors.json', encoding='utf-8') as f:
    records = json.load(f)

for r in records:
    r['others_correct'] = sum(1 for v in r['others'].values() if v.get('correct'))
    r['others_total'] = len(r['others'])

fp = sorted([r for r in records if r['error_type'] == 'FP'], key=lambda x: -x['others_correct'])
fn = sorted([r for r in records if r['error_type'] == 'FN'], key=lambda x: -x['others_correct'])

fp_sel = fp[:1] + [x for x in fp if x['others_correct']==3][:3] + [x for x in fp if x['others_correct']==0][:2]
fn_sel = [x for x in fn if x['others_correct']==4][:4] + [x for x in fn if x['others_correct']==3][:4] + [x for x in fn if x['others_correct']==0][:2]

def outros_table(r):
    lines = []
    for m, v in sorted(r['others'].items()):
        mark = 'CERTO' if v.get('correct') else 'ERROU'
        lines.append(f"  - `{m}` -> `{v['pred']}` ({mark}, conf {v.get('conf','?')}): {v.get('expl','')[:200]}")
    return '\n'.join(lines)

def classify_fp(expl):
    e = expl.lower()
    if 'no human fingerprint' in e or 'no distinct human' in e or 'lacks' in e or 'featureless' in e:
        return "Codigo humano minimalista -- ausencia de fingerprints fez o qwen aplicar a regra default (sem fingerprint = AI)."
    if 'pedagogical' in e or 'restating' in e:
        return "Comentarios didaticos interpretados como AI pedagogico -- eram de autoria humana."
    return "Codigo humano limpo sem marcas de autoria visiveis suficientes para o qwen reconhecer."

def classify_fn(expl):
    e = expl.lower()
    if ('import' in e and ('unused' in e or 'leftover' in e)):
        return "Import nao utilizado interpretado como fingerprint humano -- o dataset H-AIRosettaMP inclui AI que deliberadamente imita codigo com imports mortos."
    if 'hardcoded' in e or 'specific' in e or 'filename' in e or 'project gutenberg' in e:
        return "Valor hardcoded ou nome especifico interpretado como evidencia de sessao humana -- AI pode gerar constantes especificas contextualmente."
    if 'pep 8' in e or 'spacing' in e or 'indent' in e or 'style' in e or 'inconsistent' in e:
        return "Estilo nao-padrao interpretado como fingerprint humano -- AI pode gerar codigo que viola PEP 8 ou usa estilo misto."
    if 'padding' in e or 'align' in e or 'workaround' in e or 'manually' in e:
        return "Padrao tecnico especifico interpretado como workaround humano -- AI pode reproduzir idiomas tecnicos sofisticados."
    if 'rosetta' in e or 'stack overflow' in e:
        return "Referencia a plataforma de codigo interpretada como evidencia de autoria humana."
    if 'unused' in e or 'leftover' in e or 'dead' in e:
        return "Artefato de codigo morto interpretado como fingerprint humano -- padrão deliberado do dataset."
    return "AI com fingerprints humanos deliberadamente inseridos -- o gerador H-AIRosettaMP produz codigo que imita tracos de autoria."

out = []
out.append("# Erros do Melhor Modelo (qwen3.7-max) -- Analise com Codigo Real\n")
out.append("**Modelo analisado:** `qwen3.7-max` (melhor acuracia geral: 0.558)")
out.append("**Erros totais:** 523 em 6 rodadas (448 FN + 75 FP)")
out.append("**Base:** codigo real recuperado via seed de cada rodada\n")
out.append("---\n")

out.append("## Visao Geral dos Erros\n")
out.append("| Tipo | Total | 4/4 outros acertaram | 3/4 acertaram | Ninguem acertou |")
out.append("|---|---|---|---|---|")
out.append("| FN -- AI classificado como `human` | 448 | 4 (0.9%) | 38 (8.5%) | 185 (41.3%) |")
out.append("| FP -- Humano classificado como `ai` | 75 | 1 (1.3%) | 3 (4.0%) | 30 (40.0%) |\n")
out.append("> Em ~40% dos erros de ambos os tipos, nenhum outro modelo acertou. Os erros sao amplamente compartilhados. Os casos onde so o qwen errou sao raros e revelam pontos especificos de fraqueza.\n")
out.append("---\n")

out.append("## Parte 1 -- Falsos Positivos: Humano classificado como `ai`\n")

for i, r in enumerate(fp_sel, 1):
    ok = r['others_correct']
    total = r['others_total']
    lang = r['language'].lower()
    out.append(f"### FP {i} | {r['language']} | Rodada {r['run_id']} | Outros corretos: {ok}/{total}\n")
    out.append(f"```{lang}")
    out.append(r['code'])
    out.append("```\n")
    out.append(f"**qwen3.7-max** ERROU -> prediu `ai` (conf {r['qwen_conf']})")
    out.append(f"> {r['qwen_expl']}\n")
    out.append("**Outros modelos nesta rodada:**")
    out.append(outros_table(r))
    out.append(f"\n**Causa do erro:** {classify_fp(r['qwen_expl'])}\n")
    out.append("---\n")

out.append("## Parte 2 -- Falsos Negativos: AI classificado como `human`\n")

for i, r in enumerate(fn_sel, 1):
    ok = r['others_correct']
    total = r['others_total']
    lang = r['language'].lower()
    out.append(f"### FN {i} | {r['language']} | Rodada {r['run_id']} | Outros corretos: {ok}/{total}\n")
    out.append(f"```{lang}")
    out.append(r['code'])
    out.append("```\n")
    out.append(f"**qwen3.7-max** ERROU -> prediu `human` (conf {r['qwen_conf']})")
    out.append(f"> {r['qwen_expl']}\n")
    out.append("**Outros modelos nesta rodada:**")
    out.append(outros_table(r))
    out.append(f"\n**Causa do erro:** {classify_fn(r['qwen_expl'])}\n")
    out.append("---\n")

out.append("## Parte 3 -- Sintese dos Padroes de Erro\n")
out.append("### Falsos Positivos (humano -> AI)\n")
out.append("| Padrao | Descricao | Freq. estimada |")
out.append("|---|---|---|")
out.append("| Codigo minimalista | Sem marcas de autoria -- qwen aplica default (sem fingerprint = AI) | ~60% |")
out.append("| Comentarios didaticos | Comentarios inline interpretados como AI pedagogico | ~25% |")
out.append("| Codigo funcional compacto | Implementacoes curtas e elegantes sem idiossincrasias | ~15% |\n")
out.append("### Falsos Negativos (AI -> humano)\n")
out.append("| Padrao | Descricao | Freq. estimada |")
out.append("|---|---|---|")
out.append("| Import nao utilizado | AI com import morto -- fingerprint falso mais comum | ~35% |")
out.append("| Valor hardcoded especifico | AI usa nomes/numeros especificos que parecem contexto humano | ~20% |")
out.append("| Estilo inconsistente | AI viola PEP 8 ou usa estilo misto | ~15% |")
out.append("| Comentario informal | AI gera comentarios coloquiais ou em primeira pessoa | ~15% |")
out.append("| Bug ou falha logica | AI comete erros que parecem humanos | ~15% |\n")
out.append("### Quando os outros modelos acertam e o qwen erra\n")
out.append("- **FN exclusivos do qwen (4/4 outros acertaram):** apenas 4 casos em 448 FN -- qwen e facilmente enganado por AI que usa padroes especificos (spacing, alinhamento, nomes contextuais)")
out.append("- **FP exclusivo do qwen (4/4 outros acertaram):** 1 caso em 75 FP -- codigo C com comentarios placeholder que qwen interpretou como AI")
out.append("- **Conclusao:** qwen erra principalmente junto com os outros modelos. Seus erros unicos revelam que ele interpreta os fingerprints do prompt com mais literalidade -- qualquer ausencia de marca humana vira AI, e qualquer marca humana vira human, mesmo quando sao artificiais.")

with open('ERROS_QWEN.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print('Gerado ERROS_QWEN.md')
