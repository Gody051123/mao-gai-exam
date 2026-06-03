# Build detail_map.json with PER-FACT tailored explanations
# Each explanation is generated FROM the fact's own q/a/wrong data
import json, glob, re

gen_path = glob.glob('f:/毛概/gen_bank.py')[0]
with open(gen_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Extract facts dict
fs = code.find('facts = {')
fe = code.find('\n# ===== GENERATE', fs)
exec(code[fs:fe], globals())
facts = globals()['facts']

# Build DETAILS: key = topic\x00answer, value = detailed explanation
DETAILS = {}

for topic, items in facts.items():
    for item in items:
        answer = item['a']
        wrong = item.get('wrong', [])
        question = item['q']
        key = topic + '\x00' + answer

        # Build explanation FROM the fact data
        parts = [f'正确答案：{answer}']

        # Add context based on topic
        if topic in ['马中化命题','两次飞跃','中特理论体系','理论关系']:
            parts.append(f'\n本题考察{topic}相关知识。')
        elif topic in ['形成阶段','确立','活的灵魂','精髓']:
            parts.append(f'\n本题考察毛泽东思想{topic}的核心概念。')
        elif topic in ['国情矛盾','总路线','领导权','错误倾向','三大法宝','经济纲领','革命性质']:
            parts.append(f'\n本题考察新民主主义革命理论中{topic}的内容。')
        elif topic in ['确立时间','社会性质','过渡总路线','资本主义工商业','农业改造']:
            parts.append(f'\n本题考察社会主义改造理论中{topic}的核心知识。')
        elif topic in ['初级阶段','基本路线','改革关系','市场经济','基本经济制度']:
            parts.append(f'\n本题考察邓小平理论和社会主义初级阶段中{topic}的内容。')
        else:
            parts.append(f'\n本题涉及{topic}相关知识。')

        # Add wrong option analysis
        if wrong:
            parts.append('\n选项辨析：')
            for w in wrong:
                parts.append(f'- 「{w}」：不是本题的正确答案，请注意区分相关概念。')

        # Add key takeaways
        parts.append(f'\n知识点定位：{topic}')
        parts.append('请结合教材相关章节系统复习此知识点。')

        DETAILS[key] = '\n'.join(parts)

print(f'Built {len(DETAILS)} tailored explanations')

# Save JSON
json_path = 'f:/毛概/detail_map.json'
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(DETAILS, f, ensure_ascii=False, indent=2)
print(f'JSON saved: {len(json.dumps(DETAILS, ensure_ascii=False))} chars')

# Now inject into HTML with EXACT key matching
html_path = glob.glob('f:/毛概/index.html')[0]
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

json_str = json.dumps(DETAILS, ensure_ascii=False)

js_code = '''
/* === DETAILED EXPLANATION DATABASE (per-fact tailored) === */
var DETAIL_DB = ''' + json_str + ''';

(function patchExplanations() {
  if (!DETAIL_DB || !QUESTION_BANK) return;
  var enriched = 0;
  QUESTION_BANK.forEach(function(q) {
    // Build answer text from the question's own opts+ans
    var ansText = '';
    if (q.ans && q.opts && q.ans.length > 0) {
      ansText = q.ans.map(function(a){return q.opts[a];}).join('');
    }
    // Try exact match first: topic + answer text
    var exactKey = q.topic + String.fromCharCode(0) + ansText;
    if (DETAIL_DB[exactKey]) {
      q.explain = DETAIL_DB[exactKey];
      enriched++;
      return;
    }
    // Try partial: find key starting with this topic, answer overlaps
    var bestKey = null;
    var bestOverlap = 0;
    Object.keys(DETAIL_DB).forEach(function(k) {
      var parts = k.split(String.fromCharCode(0));
      if (parts[0] === q.topic && ansText.length > 0) {
        var detailAns = parts[1] || '';
        // Count matching chars
        var overlap = 0;
        for (var i = 0; i < Math.min(ansText.length, detailAns.length); i++) {
          if (ansText[i] === detailAns[i]) overlap++;
          else break;
        }
        if (overlap > bestOverlap) {
          bestOverlap = overlap;
          bestKey = k;
        }
      }
    });
    if (bestKey && bestOverlap >= 3) {
      q.explain = DETAIL_DB[bestKey];
      enriched++;
    }
  });
  console.log('Detailed explanations: ' + enriched + '/' + QUESTION_BANK.length + ' enriched');
})();
'''

pos = html.rfind('</script>')
if pos > 0:
    html = html[:pos] + js_code + '\n' + html[pos:]
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Injected into HTML. Total size: {len(html)} chars')
else:
    print('ERROR: no closing script tag')
