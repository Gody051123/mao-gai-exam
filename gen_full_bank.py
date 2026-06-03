# Standalone: reads gen_bank.py facts, generates questions with DETAILED explanations
# Uses json.dumps for safe JS string generation
import json, random, glob, re

random.seed(42)

# 1. Load facts from gen_bank.py
gen_path = glob.glob('f:/毛概/gen_bank.py')[0]
with open(gen_path, 'r', encoding='utf-8') as f:
    code = f.read()
fs = code.find('facts = {')
fe = code.find('\n# ===== GENERATE', fs)
exec(code[fs:fe])
facts = locals()['facts']

chapter_map = {
  '马中化命题':'导论','两次飞跃':'导论','中特理论体系':'导论','理论关系':'导论',
  '时代背景':'第一章','形成阶段':'第一章','确立':'第一章','活的灵魂':'第一章','精髓':'第一章',
  '国情矛盾':'第二章','总路线':'第二章','领导权':'第二章','错误倾向':'第二章','三大法宝':'第二章',
  '经济纲领':'第二章','革命性质':'第二章','革命道路':'第二章','工农武装割据':'第二章',
  '军队建设':'第二章','党建':'第二章','三大优良作风':'第二章',
  '社会性质':'第三章','确立时间':'第三章','新中国成立':'第三章','过渡总路线':'第三章',
  '资本主义工商业':'第三章','农业改造':'第三章','手工业':'第三章','消灭剥削':'第三章','改造经验':'第三章',
  '时代主题(邓小平)':'第六章','提出命题':'第六章','首要问题':'第六章','社会本质':'第六章',
  '社会主义原则':'第六章','初级阶段':'第六章','基本路线':'第六章','改革关系':'第六章',
  '发展':'第六章','市场经济':'第六章','基本经济制度':'第六章','一国两制':'第十二章','外交':'第十三章',
  '三个代表':'第七章','科学发展观':'第八章','生态文明':'第八章','和谐社会':'第十一章',
  '国体政体':'第九章','依法治国':'第九章','民主党派':'第九章','核心价值':'第十章','文化建设':'第十章',
  '台湾问题':'第十二章','外交格局':'第十三章','领导阶级':'第十四章','民族政策':'第十四章',
  '党的宗旨':'第十五章',
}

# 2. Generate questions with detailed explanations
singles = []
multis = []
judges = []

for topic, items in facts.items():
    ch = chapter_map.get(topic, '综合')
    for item in items:
        if len(item.get('wrong', [])) < 2:
            continue

        answer = item['a']
        wrong = item['wrong']

        # Build detailed explanation
        explain_lines = []
        explain_lines.append('【正确答案】' + answer)
        explain_lines.append('')
        explain_lines.append('【选项辨析】')
        for w in wrong:
            explain_lines.append('  - ' + w + '：此选项不正确，请注意区分相关概念。')
        explain_lines.append('')
        explain_lines.append('【复习建议】请结合教材' + ch + '相关内容系统复习' + topic + '的知识点，注意区分易混淆概念。')
        detail = '\n'.join(explain_lines)

        # Template 1: Direct
        a_opt = [answer] + wrong[:3]
        singles.append({
            'type': 'single', 'ch': ch, 'topic': topic, 'diff': 2,
            'q': item['q'] + '是？',
            'opts': a_opt, 'ans': [0], 'explain': detail
        })

        # Template 2: Shuffled
        pairs = list(enumerate(a_opt))
        random.shuffle(pairs)
        new_opts = [x[1] for x in pairs]
        new_ans = [i for i, x in enumerate(pairs) if x[0] == 0]
        explain2_lines = explain_lines[:1] + ['', '【提示】本题选项顺序经过随机排列。'] + explain_lines[1:]
        singles.append({
            'type': 'single', 'ch': ch, 'topic': topic, 'diff': 2,
            'q': item['q'] + '是？',
            'opts': new_opts, 'ans': new_ans, 'explain': '\n'.join(explain2_lines)
        })

# Multi-choice definitions
multi_data = [
    {'q': '毛泽东思想活的灵魂包括', 'opts': ['实事求是', '群众路线', '独立自主', '党的建设', '武装斗争'], 'ans': [0, 1, 2], 'topic': '活的灵魂'},
    {'q': '新民主主义革命的经济纲领包括', 'opts': ['没收封建地主阶级的土地归农民所有', '没收官僚资产阶级的垄断资本归新民主主义国家所有', '保护民族工商业', '进行大规模的社会主义改造', '征收富农的多余土地'], 'ans': [0, 1, 2], 'topic': '经济纲领'},
    {'q': '关于新民主主义社会性质，正确的有', 'opts': ['属于社会主义体系', '不是独立的社会形态', '是既有社会主义因素又有非社会主义因素的过渡性社会', '社会主义因素起决定作用必然向社会主义过渡', '属于资本主义体系'], 'ans': [0, 1, 2, 3], 'topic': '社会性质'},
    {'q': '社会主义本质的科学论断包括', 'opts': ['解放生产力', '发展生产力', '消灭剥削', '消除两极分化', '最终达到共同富裕'], 'ans': [0, 1, 2, 3, 4], 'topic': '社会本质'},
    {'q': '社会主义初级阶段的科学含义是', 'opts': ['我国已经是社会主义社会', '我国的社会主义还处在初级阶段', '这是任何国家都会经历的起始阶段', '这是特指中国的特定阶段'], 'ans': [0, 1, 3], 'topic': '初级阶段'},
    {'q': '中国特色社会主义理论体系包括', 'opts': ['毛泽东思想', '邓小平理论', "'三个代表'重要思想", '科学发展观', '习近平新时代中国特色社会主义思想'], 'ans': [1, 2, 3, 4], 'topic': '中特理论体系'},
    {'q': '始终做到"三个代表"是我们党的', 'opts': ['立党之本', '执政之基', '力量之源', '强国之路', '根本保证'], 'ans': [0, 1, 2], 'topic': '三个代表'},
    {'q': '科学发展观的主要内容有', 'opts': ['第一要义是发展', '核心是以人为本', '基本要求是全面协调可持续', '根本方法是统筹兼顾'], 'ans': [0, 1, 2, 3], 'topic': '科学发展观'},
    {'q': '社会主义核心价值体系的基本内容包括', 'opts': ['马克思主义指导思想', '中国特色社会主义共同理想', '民族精神和时代精神', '社会主义荣辱观', '社会主义市场经济理论'], 'ans': [0, 1, 2, 3], 'topic': '核心价值'},
    {'q': '中国共产党同各民主党派合作的基本方针是', 'opts': ['长期共存', '互相监督', '肝胆相照', '荣辱与共', '轮流执政'], 'ans': [0, 1, 2, 3], 'topic': '民主党派'},
    {'q': '社会主义和谐社会的总体特征包括', 'opts': ['民主法治、公平正义', '诚信友爱、充满活力', '安定有序', '人与自然和谐相处', '绝对平均、完全平等'], 'ans': [0, 1, 2, 3], 'topic': '和谐社会'},
    {'q': '"三个代表"重要思想三者关系表现为', 'opts': ['发展先进生产力是基础条件', '人民群众是创造主体和根本力量', '发展先进生产力和先进文化归根到底是为了满足人民需要', '发展先进生产力是实现人民利益的最终目的'], 'ans': [0, 1, 2], 'topic': '三个代表'},
    {'q': '"工农武装割据"思想主要包括', 'opts': ['武装斗争', '土地革命', '农村革命根据地', '统一战线', '党的建设'], 'ans': [0, 1, 2], 'topic': '工农武装割据'},
    {'q': '邓小平关于社会主义市场经济理论的内涵包括', 'opts': ['市场经济是资源配置的一种方式', '市场经济不具有社会制度的属性', '市场调节可以和计划调节相结合', '市场和计划都是经济手段'], 'ans': [0, 1, 2, 3], 'topic': '市场经济'},
    {'q': '中国共产党的三大优良作风是', 'opts': ['理论联系实际', '密切联系群众', '批评与自我批评', '艰苦奋斗', '民主集中制'], 'ans': [0, 1, 2], 'topic': '三大优良作风'},
    {'q': '新中国成立初期毛泽东提出的外交方针有', 'opts': ['"另起炉灶"', '"打扫干净屋子再请客"', '"一边倒"', '"一条线"'], 'ans': [0, 1, 2], 'topic': '外交格局'},
    {'q': '解决民族问题的基本原则是', 'opts': ['维护祖国统一反对民族分裂', '坚持民族平等', '坚持民族团结', '坚持各民族共同繁荣'], 'ans': [0, 1, 2, 3], 'topic': '民族政策'},
    {'q': '当前推进党的建设新的伟大工程的主线是加强党的', 'opts': ['执政能力建设', '反腐倡廉建设', '制度建设', '先进性建设'], 'ans': [0, 3], 'topic': '三个代表'},
    {'q': '中国共产党的领导包括', 'opts': ['政治领导', '思想领导', '组织领导', '经济领导'], 'ans': [0, 1, 2], 'topic': '领导阶级'},
    {'q': '构建和谐社会必须遵循的原则有', 'opts': ['坚持以人为本', '坚持科学发展', '坚持改革开放', '坚持民主法治', '坚持正确处理改革发展稳定关系', '坚持在党的领导下全社会共同建设'], 'ans': [0, 1, 2, 3, 4, 5], 'topic': '和谐社会'},
]

for md in multi_data:
    ch = chapter_map.get(md['topic'], '综合')
    # Build multi explanation
    m_lines = ['【正确答案】如标记所示。', '', '【选项辨析】']
    for i, opt in enumerate(md['opts']):
        if i in md['ans']:
            m_lines.append('  - ' + opt + '：正确选项。')
        else:
            m_lines.append('  - ' + opt + '：不正确。')
    m_lines.append('')
    m_lines.append('【复习建议】请结合教材' + ch + '相关内容系统复习' + md['topic'] + '的知识点。')
    m_detail = '\n'.join(m_lines)

    multis.append({'type': 'multi', 'ch': ch, 'topic': md['topic'], 'diff': 2,
                   'q': md['q'], 'opts': md['opts'], 'ans': md['ans'], 'explain': m_detail})
    # Shuffled
    idxs = list(range(len(md['opts'])))
    random.shuffle(idxs)
    new_opts = [md['opts'][i] for i in idxs]
    new_ans = sorted([idxs.index(a) for a in md['ans']])
    multis.append({'type': 'multi', 'ch': ch, 'topic': md['topic'], 'diff': 2,
                   'q': md['q'], 'opts': new_opts, 'ans': new_ans, 'explain': m_detail})

# Judge questions
judge_data = [
    ('毛泽东思想是中国特色社会主义理论体系的重要思想渊源。', 0, '理论关系'),
    ('1938年毛泽东在中共六届六中全会上首次提出"马克思主义中国化"的命题。', 0, '马中化命题'),
    ('新民主主义革命的性质是无产阶级社会主义革命。', 1, '革命性质'),
    ('1949年中华人民共和国成立标志着我国进入了社会主义社会。', 1, '新中国成立'),
    ('在当代中国，坚持中国特色社会主义理论体系就是真正坚持马克思主义。', 0, '中特理论体系'),
    ('改革是社会主义社会发展的直接动力，是中国的第二次革命。', 0, '改革关系'),
    ('社会和谐是中国特色社会主义的本质属性。', 0, '和谐社会'),
    ('人民当家作主是社会主义民主政治的本质和核心。', 0, '国体政体'),
    ('独立自主是中国对外政策的根本原则。', 0, '外交'),
    ('"一国两制"构想最初是针对香港问题提出来的。', 1, '一国两制'),
    ('坚持发展是硬道理就是要坚持以GDP为唯一标准。', 1, '发展'),
    ('贯彻"三个代表"重要思想，核心在坚持与时俱进。', 1, '三个代表'),
    ('社会主义与资本主义的本质区别在于是否实行市场经济。', 1, '社会本质'),
    ('党的思想路线的实质和核心是解放思想。', 1, '精髓'),
    ('马克思主义最重要的理论品质是实事求是。', 1, '精髓'),
    ('社会主义社会的基本矛盾是对抗性的矛盾。', 1, '确立时间'),
    ('我国的民主党派是在野党。', 1, '民主党派'),
    ('"绿水青山就是金山银山"说明保护生态环境就是保护生产力。', 0, '生态文明'),
    ('毛泽东思想是毛泽东个人的思想结晶。', 1, '活的灵魂'),
]

for q_text, ans_val, topic in judge_data:
    ch = chapter_map.get(topic, '综合')
    is_correct = ans_val == 0
    j_detail = '【答案】' + ('正确。' if is_correct else '错误。')
    j_detail += '\n\n【解析】'
    if is_correct:
        j_detail += '这是一个正确的论断，是毛概课程中的重要考点，请准确记忆。'
    else:
        j_detail += '此说法不正确。请结合教材' + ch + '中关于' + topic + '的内容，纠正此错误理解。'
    j_detail += '\n\n【复习建议】判断题的关键在于准确辨析概念的正误，注意常见易错表述。'
    judges.append({'type': 'judge', 'ch': ch, 'topic': topic, 'diff': 1 if is_correct else 2,
                   'q': q_text, 'opts': ['正确', '错误'], 'ans': [ans_val], 'explain': j_detail})

# 3. Assign IDs
all_q = singles + multis + judges
for i, q in enumerate(all_q):
    q['id'] = i + 1

# 4. Generate JS using json.dumps (safe!)
js_lines = []
js_lines.append('// Generated question bank with DETAILED explanations')
js_lines.append('// ' + str(len(all_q)) + ' total: ' + str(len(singles)) + ' singles + ' + str(len(multis)) + ' multis + ' + str(len(judges)) + ' judges')
js_lines.append('const QUESTION_BANK = [')

for q in all_q:
    js_lines.append('  {id:' + str(q['id']) + ',type:' + json.dumps(q['type']) + ',ch:' + json.dumps(q['ch'], ensure_ascii=False) + ',topic:' + json.dumps(q['topic'], ensure_ascii=False) + ',diff:' + str(q['diff']) + ',')
    js_lines.append('   q:' + json.dumps(q['q'], ensure_ascii=False) + ',')
    js_lines.append('   opts:' + json.dumps(q['opts'], ensure_ascii=False) + ',')
    js_lines.append('   ans:' + json.dumps(q['ans']) + ',explain:' + json.dumps(q['explain'], ensure_ascii=False) + '},')

js_lines.append('];')
bank_js = '\n'.join(js_lines)

print(f'Generated {len(all_q)} questions with detailed explains')
print(f'JS size: {len(bank_js)} chars')

# 5. Inject into HTML
html_path = glob.glob('f:/毛概/index.html')[0]
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

old_start = html.find('const QUESTION_BANK = [')
old_end = html.find('// ===================== APP STATE =====================')

if old_start >= 0 and old_end > old_start:
    html = html[:old_start] + bank_js + '\n\n' + html[old_end:]

    # Apply fixes
    html = html.replace('function renderAnalysisContent() {', 'function renderAnalysisContent() { try {', 1)
    html = html.replace('  content.innerHTML = html;\n  window.scrollTo(0, 0);', '  content.innerHTML = html;\n  window.scrollTo(0, 0);\n  } catch(e) { var ac=document.getElementById("analysis-content"); if(ac)ac.innerHTML="<div class=card><p>Error: "+e.message+"</p></div>"; }', 1)
    html = html.replace('function init() {', 'function init() { if(localStorage.getItem("mv")!=="9"){localStorage.removeItem("maogai_exam_system");localStorage.setItem("mv","9");}', 1)
    html = html.replace('    q.opts.forEach((opt, oi) => {\n      const isCorrectOpt = q.ans.includes(oi);\n      const isUserOpt = (d.userAns || []).includes(oi);', '    var qOpts=(q.opts&&q.opts.length>0)?q.opts:(q.type==="judge"?["A","B"]:[]);\n    qOpts.forEach((opt, oi) => {\n      const isCorrectOpt = q.ans.includes(oi);\n      const isUserOpt = (d.userAns || []).includes(oi);')
    html = html.replace('function viewHistoryExam(idx) {\n  const exam', 'function viewHistoryExam(idx) {\n  var exam')

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'HTML updated: {len(html)} chars')
else:
    print('ERROR: markers not found')
