# Build detail_map.json from gen_bank.py facts
# Pure ASCII - all Chinese constructed at runtime from existing data
import json, glob, random, sys

random.seed(42)

# Read gen_bank.py
gen_path = glob.glob('f:/*/gen_bank.py')[0]
with open(gen_path, 'r', encoding='utf-8') as f:
    gen_code = f.read()

# Execute to get 'facts' dict
ns = {}
exec(gen_code, ns)
facts = ns['facts']

# Read .md files for detailed content
md_text = ''
for mf in glob.glob('f:/*/*.md'):
    with open(mf, 'r', encoding='utf-8') as f:
        md_text += f.read()

# Extract key knowledge segments from md files
# Map: topic -> detailed explanation segments
md_segments = {}
for mf in glob.glob('f:/*/*.md'):
    if '解析' not in mf and '知识要点' not in mf:
        continue
    with open(mf, 'r', encoding='utf-8') as f:
        content = f.read()
    # Split into sections by ## headers
    import re
    sections = re.split(r'\n## ', content)
    for sec in sections:
        if not sec.strip():
            continue
        # First line is the section title
        lines = sec.split('\n')
        title = lines[0].strip().lstrip('#').strip()
        body = '\n'.join(lines[1:]).strip()
        if len(body) > 50:
            md_segments[title] = body[:800]

print(f'Loaded {len(md_segments)} knowledge segments from MD files')

# Build DETAILS: (topic, answer_substring) -> full explanation
DETAILS = {}

# For each fact, find the best matching segment from MD files
for topic, items in facts.items():
    for item in items:
        answer = item['a']
        key = topic + '\x00' + answer

        # Search for relevant content in MD segments
        best_match = ''
        best_score = 0

        for seg_title, seg_body in md_segments.items():
            # Score by keyword overlap
            score = 0
            keywords = [topic[:4], answer[:4]] + [w[:2] for w in item.get('wrong', [])]
            for kw in keywords:
                if kw and kw in seg_title + seg_body[:200]:
                    score += 1

            if score > best_score:
                best_score = score
                best_match = seg_body

        if best_score >= 2:
            DETAILS[key] = best_match[:600]
        else:
            # Build fallback explanation from fact data
            wrong_str = '、'.join(item.get('wrong', []))
            detail = '正确答案是' + answer + '。'
            if item.get('wrong'):
                detail += '\n\n易混淆选项：' + wrong_str
                detail += '\n\n请仔细区分各选项的含义。'
            detail += '\n\n知识点定位：' + topic
            DETAILS[key] = detail

print(f'Built {len(DETAILS)} detailed explanations')

# Save as JSON
json_path = glob.glob('f:/*/')[0] + 'detail_map.json'
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(DETAILS, f, ensure_ascii=False, indent=2)
print(f'Saved to {json_path}')
print('JSON size:', len(json.dumps(DETAILS, ensure_ascii=False)))

# Now inject into HTML
html_path = glob.glob('f:/*/index.html')[0]
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Build JS injection
json_str = json.dumps(DETAILS, ensure_ascii=False)
js_code = '''
/* === DETAILED EXPLANATIONS === */
var DETAIL_DB = ''' + json_str + ''';

(function enrichExplanations() {
  if (!DETAIL_DB || !QUESTION_BANK) return;
  var count = 0;
  QUESTION_BANK.forEach(function(q) {
    // Try exact match first
    var ansText = '';
    if (q.ans && q.opts && q.ans.length > 0) {
      ansText = q.ans.map(function(a){return q.opts[a];}).join('');
    }
    var key = q.topic + '\x00' + ansText;

    if (DETAIL_DB[key]) {
      q._origExplain = q.explain;
      q.explain = DETAIL_DB[key];
      count++;
    } else {
      // Try partial match
      for (var k in DETAIL_DB) {
        if (k.startsWith(q.topic + '\x00')) {
          var detailAns = k.split('\x00')[1];
          if (ansText.indexOf(detailAns.substring(0,4)) >= 0 || detailAns.indexOf(ansText.substring(0,4)) >= 0) {
            q._origExplain = q.explain;
            q.explain = DETAIL_DB[k];
            count++;
            break;
          }
        }
      }
    }
  });
  console.log('Enriched ' + count + ' explanations from detail database');
})();
'''

# Inject before closing </script>
pos = html.rfind('</script>')
if pos > 0:
    html = html[:pos] + js_code + '\n' + html[pos:]
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Injected JS detail lookup into HTML ({len(js_code)} chars)')
else:
    print('ERROR: </script> not found')
