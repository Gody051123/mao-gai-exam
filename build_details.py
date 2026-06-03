# Pure ASCII script - reads gen_bank.py, builds DETAILS in memory from fact data
# All Chinese content stays inside Python, never touches bash/Write tool
import json, random, glob

random.seed(42)

# 1. Read gen_bank.py and extract facts
exec(open(glob.glob('f:/*/gen_bank.py')[0], 'r', encoding='utf-8').read())

# 2. Build detailed explanations for each fact
# Each detail is constructed from the fact's own data (q, a, wrong)
DETAILS = {}

def add_detail(topic, answer, text):
    DETAILS[(topic, answer)] = text

# Mapping of topic -> (answer_key -> detail text)
# We build these by reading the .md analysis files and extracting relevant content
# or by constructing from known knowledge patterns

# For now, load from a JSON file that was created correctly
import os
detail_file = glob.glob('f:/*/detail_map.json')
if detail_file:
    with open(detail_file[0], 'r', encoding='utf-8') as f:
        DETAILS = json.load(f)
    print(f'Loaded {len(DETAILS)} details from JSON')
else:
    # Build basic details from fact data
    for topic, items in facts.items():
        for item in items:
            key = (topic, item['a'])
            # Build a reasonable explanation from the fact data
            wrong_str = '、'.join(item['wrong'])
            detail = '正确答案是' + item['a'] + '。'
            if item.get('wrong'):
                detail += '\n\n易混淆选项：' + wrong_str + '。'
                detail += '\n请仔细区分各选项的含义和适用场景。'
            DETAILS[str(key)] = detail
    print(f'Built {len(DETAILS)} basic details')

# 3. Modify gen_bank.py generation logic to use DETAILS
# Read the HTML and inject details
html_path = glob.glob('f:/*/index.html')[0]
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Build a JS lookup object
js_detail = 'const DETAIL_MAP = ' + json.dumps(DETAILS, ensure_ascii=False) + ';\n'
js_detail += '''
function getDetail(topic, answer) {
  const key = JSON.stringify([topic, answer]);
  return DETAIL_MAP[key] || '';
}
// Patch QUESTION_BANK with detailed explanations
QUESTION_BANK.forEach(function(q) {
  var key = JSON.stringify([q.topic, q.ans ? q.ans.map(function(a){return q.opts[a];}).join('') : '']);
  // Try lookup by topic+correct answer text
  for (var k in DETAIL_MAP) {
    var parts = JSON.parse(k);
    if (parts[0] === q.topic) {
      // Check if answer matches
      if (q.ans && q.opts && q.ans.length > 0) {
        var correctText = q.ans.map(function(a){return q.opts[a];}).join('');
        if (correctText.indexOf(parts[1].substring(0,4)) >= 0 || parts[1].indexOf(correctText.substring(0,4)) >= 0) {
          q.explain = DETAIL_MAP[k];
          break;
        }
      }
    }
  }
});
'''

# Inject before init()
init_pos = html.find('function init() {')
if init_pos > 0:
    html = html[:init_pos] + js_detail + '\n' + html[init_pos:]
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print('Injected JS detail lookup into HTML')
else:
    print('Init not found')
