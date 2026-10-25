from pathlib import Path
import argparse,hashlib,json,random,sys

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'authoring'))
from detailed_questions import QUESTIONS
from semester7_questions import QUESTIONS7
from learning_details import refine
QUESTIONS.update(QUESTIONS7)
parser=argparse.ArgumentParser()
parser.add_argument('--brainm',type=Path)
args=parser.parse_args()
def read(path):return json.loads((root/path).read_text(encoding='utf-8'))
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
course=read('authoring/course-config.json')
lessons={}
for sem in [5,6,7]:
    for l in read(f'authoring/semester-{sem}.json'):lessons[l['id']]={**l,'semester':sem}
missing=set(lessons)-set(QUESTIONS)
if missing:raise SystemExit('Detailed source is incomplete: '+', '.join(sorted(missing)))
course['contentVersion']='rkis-2026-10-25-structure-3'
course['assessment']={'mode':'autonomous','url':'assessment.json'}
course['lectures']=[];notes={};keys={};models={};glossary=[];integrated_solutions={}
literature=read('authoring/literature.json')
supplements=read('authoring/supplements.json')
code_question={'s05-01-dotnet':4,'s05-05-model':3,'s05-06-invariants':2,'s05-08-interfaces':1,'s05-09-business':1,'s05-10-money':4,'s05-11-states':2,'s05-12-rules':1,'s05-13-batch':1,'s05-14-connections':3,'s05-15-commands':4,'s05-16-repository':3,'s05-17-binding':1,'s05-18-editing':1,'s05-19-navigation':3,'s06-01-passwords':3,'s06-02-login':1,'s06-03-roles':2,'s06-04-lockout':2,'s06-05-images':3,'s06-06-administration':4,'s06-07-interface':4,'s07-01-files':2,'s07-02-json':2,'s07-03-http':2,'s07-04-validation':2,'s07-05-docx':2}
supplement_question={'s05-04-diagnostics':[2,4],'s05-07-collections':[2],'s05-10-money':[1],'s05-15-commands':[4],'s06-04-lockout':[3],'s06-05-images':[1],'s07-02-json':[4],'s07-03-http':[1],'s07-05-docx':[2]}

def numeric(value):
    try:return float(value.replace(',','.'))
    except ValueError:return None

def shuffled_options(task_id,texts):
    options=[{'id':f'o{i}','text':value} for i,value in enumerate(texts)]
    random.Random(int(hashlib.sha256(task_id.encode()).hexdigest()[:16],16)).shuffle(options)
    return options

def make_model(lecture,q,unit):
    model_id=f'{lecture["id"]}-q{q}-model'
    scenarios=[]
    for index,field in enumerate(['worked','changed']):
        given,conclusion,value=unit[field]
        initial=unit.get('initial' if index==0 else 'changedInitial') or {'Вход':given}
        final=unit.get('final' if index==0 else 'changedFinal') or {'Результат':value}
        branch='yes' if value.lower()=='да' else 'no' if value.lower()=='нет' else None
        frames=[{'label':'Исходное состояние. '+given,'variables':initial,'console':[]},
          {'label':'Учитываем правило: '+unit['terms'][0][0]+'.','variables':initial,'console':[]},
          {'label':unit['explain'].split('. ')[0]+'.','variables':final,'console':[]},
          {'label':conclusion,'variables':final,'console':[value] if unit.get('code') and 'Console.WriteLine' in unit['code'] else []}]
        if branch:
            frames[2]['branch']=branch;frames[3]['branch']=branch
        if unit.get('objects') and index==0:
            for i,frame in enumerate(frames):
                frame['links']=unit['objects']['links'];frame['objects']=unit['objects']['before' if i<2 else 'after']
        scenarios.append({'id':'worked' if index==0 else 'changed','title':'Исходный пример' if index==0 else 'Изменённые условия','given':given,'frames':frames,'review':conclusion+' '+unit['explain'],'accepted':[value],'hint':'Сопоставьте исходное состояние и правило. '+unit['terms'][0][1]})
    # A real trace of every loop iteration, including the skipped elements.
    if lecture['id']=='s05-02-csharp' and q==3:
        for scenario,prices in zip(scenarios,[[100,0,250],[0,-20,40]]):
            total=0;frames=[{'label':'Инициализация накопителя.','line':1,'variables':{'total':'0','price':'—'},'console':[]}]
            for price in prices:
                frames.append({'label':f'Цикл получает очередное price = {price}.','line':2,'variables':{'total':str(total),'price':str(price)},'console':[]})
                frames.append({'label':f'Проверка {price} > 0: '+('да' if price>0 else 'нет')+'.','line':3,'variables':{'total':str(total),'price':str(price)},'console':[]})
                if price>0:
                    total+=price;frames.append({'label':f'Добавляем {price}; total = {total}.','line':3,'variables':{'total':str(total),'price':str(price)},'console':[]})
            frames.append({'label':'Цикл завершён. Печать итоговой суммы.','line':4,'variables':{'total':str(total),'price':'последний элемент'},'console':[str(total)]})
            scenario['frames']=frames
    identity=lecture['id']
    case_code={
      ('s05-02-csharp',1):['Console.WriteLine(5 / 2);','Console.WriteLine(5m / 2);'],
      ('s05-02-csharp',4):['decimal price = 125.50m;\nint count = 3;\ndecimal total = price * count;\nConsole.WriteLine(total);','decimal price = 80m;\nint count = 2;\ndecimal total = price * count;\nConsole.WriteLine(total);'],
      ('s05-03-types',1):['int a = 10;\nint b = a;\nb = 20;\nConsole.WriteLine(a);','var a = new List<int> {10};\nvar b = a;\nb.Add(20);\nConsole.WriteLine(a.Count);'],
      ('s05-03-types',3):['string s = "ИС";\nstring t = s;\nt += "!";\nConsole.WriteLine(s);\nConsole.WriteLine(t);','string s = "код";\nstring t = s;\nt += "!";\nConsole.WriteLine(s);\nConsole.WriteLine(t);'],
      ('s05-03-types',4):['var products = new Dictionary<int, string> { [7] = "Блокнот", [8] = "Ручка" };\nint id = 7;\nif (products.TryGetValue(id, out var name))\n    Console.WriteLine(name);\nelse\n    Console.WriteLine("Товар не найден");','var products = new Dictionary<int, string> { [7] = "Блокнот", [8] = "Ручка" };\nint id = 99;\nif (products.TryGetValue(id, out var name))\n    Console.WriteLine(name);\nelse\n    Console.WriteLine("Товар не найден");'],
      ('s05-04-diagnostics',3):['decimal price = 120m;\nint count = 3;\ndecimal total = price + count;\nConsole.WriteLine(total);','decimal price = 120m;\nint count = 3;\ndecimal total = price * count;\nConsole.WriteLine(total);'],
      ('s05-07-collections',3):['var stock = new List<int> {0,2,5};\nvar query = stock.Where(x => x > 0);\nstock.Add(3);\nvar snapshot = query.ToList();\nConsole.WriteLine(snapshot.Count);','var stock = new List<int> {0,2,5};\nvar query = stock.Where(x => x > 0);\nvar snapshot = query.ToList();\nstock.Add(3);\nConsole.WriteLine(snapshot.Count);'],
      ('s05-10-money',3):['Console.WriteLine(Math.Round(2.345m, 2, MidpointRounding.AwayFromZero));','Console.WriteLine(Math.Round(2.345m, 2, MidpointRounding.ToEven));']
    }
    if (identity,q) in case_code:
        for scenario,code in zip(scenarios,case_code[(identity,q)]):scenario['code']=code
    if (identity,q)==('s05-03-types',3):
        for scenario,output in zip(scenarios,[['ИС','ИС!'],['код','код!']]):scenario['frames'][-1]['console']=output
    if (identity,q)==('s05-02-csharp',2):
        for scenario,output in zip(scenarios,[['Допустимо'],['Количество должно быть больше нуля']]):scenario['frames'][-1]['console']=output
    if (identity,q)==('s05-03-types',4):
        for scenario,output in zip(scenarios,[['Блокнот'],['Товар не найден']]):scenario['frames'][-1]['console']=output
    for scenario in scenarios:
        if 'Console.WriteLine' not in (scenario.get('code') or unit.get('code') or ''):
            for frame in scenario['frames']:frame.pop('console',None)
    flow_actions={
      's05-02-csharp':('Вывести «Допустимо»','Сообщить об ограничении'),
      's05-03-types':('Вернуть найденный товар','Показать «Товар не найден»'),
      's05-06-invariants':('Принять новое значение','Сохранить прежнее значение'),
      's05-09-business':('Подтвердить заказ','Сохранить черновик'),
      's05-11-states':('Status ← Confirmed','Не менять Status'),
      's05-12-rules':('Продолжить операцию','Вернуть нарушение правила'),
      's05-13-batch':('Commit','Rollback')}
    yes,no=flow_actions.get(identity,('Выполнить допустимое действие','Отклонить изменение'))
    return model_id,{'id':model_id,'title':unit['title'],'mode':unit.get('mode','table'),'code':unit.get('code'),'condition':unit.get('condition'),'yes':yes,'no':no,'task':unit['resultQuestion'],'output':'Для выбранного сценария запишите ответ: число, слово или «да/нет» согласно условию. Сначала сделайте прогноз, затем проследите состояния и сравните результаты двух запусков.','scenarios':scenarios}

for lecture_id,lesson in lessons.items():
    units=QUESTIONS[lecture_id];slides=[]
    def add(suffix,kind,title,body='',speech=None,notebook='',**extra):
        sid=lecture_id+'-'+suffix
        slide={'id':sid,'kind':kind,'title':title,'kicker':extra.pop('kicker','МДК.05.02'),**extra}
        if body:slide['body']=body
        if notebook:slide['notebook']=notebook
        slides.append(slide)
        notes[sid]={'script':speech if speech is not None else body,'preparation':'','notebook':notebook,'questions':'','answer':'','estimatedSeconds':max(30,round(len((speech or body).split())*60/105))}
        return sid
    add('title','title',lesson['title'],f'МДК.05.02 · {lesson["semester"]} семестр',speech=lesson['goal']+' Сквозной пример относится к учебной системе заказов. Важно различать данные, выполняемое правило и фактически полученный результат.')
    selected=[literature[x] for x in lesson['reading']]
    for group,label in [('primary','Основная литература'),('additional','Дополнительная литература')]:
        entries=[{'citation':v['citation'],'url':v['url']} for v in selected if v['group']==group]
        if not entries:entries=[{'citation':v['citation'],'url':v['url']} for v in literature.values() if v['group']==group][:1]
        add('reading-'+group,'literature',label,speech='Перечисленные издания дают предметную основу темы. Примеры конкретного API нужно сверять с документацией его версии; закрытым книгам не приписываются непроверенные страницы и цитаты.',references=entries,readingGroup=group)
    add('materials','materials','Материалы к занятиям',speech='Папка курса доступна по ссылке и QR-коду. Исходные примеры C# открываются отдельной ссылкой; вернитесь из материалов к вопросам темы.')
    add('agenda','agenda','Вопросы темы',speech='Начнём с исходных понятий, затем проследим механизм, изменим условия и проверим выводы. В этой теме последовательно разберём: '+'. '.join(u['title'] for u in units)+'.')
    add('context','theory','Предметная задача',lesson['goal'],speech=lesson['goal']+' '+lesson['explain'].split('. ')[0]+'.')
    add('method','theory','Как исследовать поведение программы',bullets=['Зафиксировать исходные значения и требуемый результат.','Связать операцию с изменением конкретных значений или ссылок.','Проверить исходный и изменённый случаи, затем обосновать границу вывода.'],speech='В разборе сначала сохраняем исходное состояние. После каждого существенного оператора сравниваем старые и новые значения. Если результат не совпал с прогнозом, возвращаемся к первому различию в состоянии, а не меняем сразу весь код. После исходного случая отдельно решаем задачу с изменёнными данными.')
    add('case-input','example','Исходные данные сквозного примера',units[0]['worked'][0],speech=units[0]['worked'][0]+' Не подменяйте исходные условия итогом: сначала запишите прогноз, который можно проверить по конкретному наблюдению.')
    add('notation','theory','Читаем вход, операцию и результат',bullets=[f'{term}: {definition}' for term,definition in units[0]['terms']],speech='Введённые обозначения нужны для чтения примера. '+units[0]['explain'])
    add('diagnostic','questions','Предварительный прогноз',units[0]['changed'][0],speech='До объяснения темы предложите предварительный ответ и сохраните его. В конце сравните рассуждение с результатом трассировки. Здесь не раскрываем ключ.')
    for q,unit in enumerate(units,1):
        prefix=f'q{q}';model_id,model=make_model(lesson,q,unit);models[model_id]=refine(lecture_id,q,model)
        add(prefix+'-section','section',unit['title'],unit['worked'][0],speech=unit['worked'][0]+' Для ответа потребуются понятия текущего вопроса.',kicker=f'Вопрос {q}')
        for index,(term,definition) in enumerate(unit['terms'],1):
            context=unit['explain'].split('. ')[min(index-1,len(unit['explain'].split('. '))-1)]
            sid=add(prefix+f'-definition-{index}','notebook',term,body=context,notebook=f'{term} — {definition}',speech=f'{term} — {definition} '+context+'. В примере ищем конкретный признак этого понятия: '+unit['worked'][0],kicker=f'Определения · вопрос {q}')
            glossary.append({'term':term,'definition':f'{term} — {definition}','slideIds':[sid]})
        add(prefix+'-mechanism','theory','Как работает механизм',unit['explain'],speech=unit['explain']+' Переходя к схеме, проследите, какие именно входные данные используются правилом и какое наблюдение подтвердит результат.',kicker=f'Логика применения · вопрос {q}')
        add(prefix+'-visual','process','Проследим состояние по шагам',speech='Показ: откройте разбор в шапке слайда. Выберите «Исходный пример», сначала рассмотрите начальные значения, затем переходите по шагам. '+unit['worked'][1]+' Переключите сценарий: движение остановится, а значения вернутся к началу другого случая. Полное объяснение изменённого случая остаётся в ответах преподавателя до попытки группы.',learning={'id':model_id},kicker=f'Схема и наблюдение · вопрос {q}')
        code=unit.get('code') or (lesson['code'] if q==code_question.get(lecture_id) else '')
        if code:
            code_lines=code.splitlines()
            for part,offset in enumerate(range(0,len(code_lines),9),1):
                add(prefix+f'-code-{part}','example','Код и его назначение',body=lesson['codeCaption'] if not unit.get('code') else 'Учебный фрагмент. Сопоставьте операцию, её входы и наблюдаемый результат.',code='\n'.join(code_lines[offset:offset+9]),codeLanguage='csharp',speech='Прочитайте показанный фрагмент сверху вниз. '+unit['worked'][0]+' Входы операции должны соответствовать этим условиям. '+unit['worked'][1]+' '+context+'. Обратите внимание, какие значения меняются, а какие сохраняются; продолжение относится к тому же примеру.',kicker=f'Пример кода · вопрос {q}')
        for supplement_index,supplement in enumerate(supplements.get(lecture_id,[])):
            if supplement_question.get(lecture_id,[])[supplement_index]!=q:continue
            lines=supplement['code'].splitlines()
            for part,offset in enumerate(range(0,len(lines),9),1):
                add(prefix+f'-supplement-{supplement_index+1}-{part}','example',supplement['title'],supplement['body'],speech=supplement['speech'],code='\n'.join(lines[offset:offset+9]),codeLanguage='csharp',kicker=f'Применение · вопрос {q}')
        add(prefix+'-worked','example','Разбираем исходный случай',unit['worked'][0],bullets=[unit['worked'][1],unit['explain'].split('. ')[0]+'.'],speech='Исходное условие: '+unit['worked'][0]+' Применяем введённое правило и получаем проверяемый вывод: '+unit['worked'][1]+' Для проверки откройте схему предыдущего разбора и сопоставьте конечное состояние с этим выводом.',kicker=f'Разбор по шагам · вопрос {q}')
        sid=add(prefix+'-changed','questions','Изменяем условие',unit['changed'][0],speech='Сначала прочитайте новые исходные данные и дайте группе время на ответ. Не переносите прежний результат без проверки изменившегося условия.',practice={'solutionId':model_id},kicker=f'Перенос решения · вопрос {q}');notes[sid]['answer']=unit['changed'][1]+' '+unit['explain']
        add(prefix+'-mistake','warning','Почему типичная ошибка меняет результат','Ошибка: «'+unit['wrong'][0]+'»',bullets=[unit['terms'][0][0]+' — '+unit['terms'][0][1],unit['worked'][1]],speech='Утверждение «'+unit['wrong'][0]+'» ошибочно. '+unit['explain']+' Это видно из исходного случая: '+unit['worked'][1],kicker=f'Антиошибка · вопрос {q}')
        add(prefix+'-takeaway','summary','Проверяем основание вывода',unit['worked'][1],notebook=unit['terms'][0][0]+' — '+unit['terms'][0][1],speech=unit['worked'][1]+' В рассуждении должны присутствовать исходные данные, применённое правило и наблюдение. '+unit['explain'].split('. ')[0]+'.',kicker=f'Контроль понимания · вопрос {q}')
        sid=add(prefix+'-practice','example','Практика: '+unit['title'],speech='Откройте практику. Сначала запишите прогноз для исходных данных. Перейдите по всем шагам, сохраните результат для сравнения. Затем выберите изменённый случай, заново решите задачу и сравните выводы. '+unit['resultQuestion']+' До самостоятельной попытки не открывайте разбор.',learning={'id':model_id,'passport':True},kicker=f'Разбор задачи · вопрос {q}')
        notes[sid]['questions']=unit['changed'][0];notes[sid]['answer']=unit['changed'][1]+' '+unit['explain'];notes[sid]['estimatedSeconds']=480
        choices=[unit['changed'][1],*unit['wrong'],'Предоставленных исходных данных недостаточно даже для указанного в условии вывода.']
        task_id='task-'+lecture_id+'-'+prefix+'-test-single'
        sid=add(prefix+'-test-single','test','Примените правило к ситуации',task={'id':task_id,'type':'single','prompt':unit['changed'][0],'options':shuffled_options(task_id,choices)},speech='Прочитайте условие и выберите один ответ. Обоснуйте выбор тем, какое условие изменилось относительно исходного примера.',kicker=f'Самопроверка · вопрос {q} · 1 из 4')
        keys[task_id]={'type':'single','correct':['o0'],'explanation':unit['changed'][1]+' '+unit['explain'],'optionExplanations':{f'o{i}':(unit['changed'][1] if i==0 else 'Этот вывод не следует из условия. '+unit['explain']) for i in range(len(choices))}};notes[sid]['answer']=keys[task_id]['explanation']
        task_id='task-'+lecture_id+'-'+prefix+'-test-multiple'
        facts=[unit['changed'][1],unit['explain'].split('. ')[0]+'.',*unit['wrong'],'Достаточно наличия кода: наблюдаемый результат проверять не требуется.']
        sid=add(prefix+'-test-multiple','test','Выберите два обоснованных утверждения',task={'id':task_id,'type':'multiple','choose':2,'prompt':unit['changed'][0]+' Выберите ровно два верных утверждения.','options':shuffled_options(task_id,facts)},speech='Здесь нужны два верных утверждения: вывод для заданного случая и верное объяснение механизма. Каждый выбранный пункт нужно обосновать независимо.',kicker=f'Самопроверка · вопрос {q} · 2 из 4')
        keys[task_id]={'type':'multiple','correct':['o0','o1'],'explanation':unit['changed'][1]+' '+unit['explain']};notes[sid]['answer']=keys[task_id]['explanation']
        task_id='task-'+lecture_id+'-'+prefix+'-test-short';value=unit['changed'][2]
        sid=add(prefix+'-test-short','test','Определите результат',task={'id':task_id,'type':'short','prompt':unit['changed'][0]+' '+unit['resultQuestion']},speech='Укажите требуемый результат в форме, названной в условии. Если ответ числовой, не добавляйте единицы к числу в поле; смысл единиц проговорите отдельно.',kicker=f'Самопроверка · вопрос {q} · 3 из 4')
        keys[task_id]={'type':'short','explanation':unit['changed'][1]+' '+unit['explain']}
        if numeric(value) is not None:keys[task_id]['numeric']={'value':numeric(value),'tolerance':0}
        else:keys[task_id]['accepted']=[value]
        notes[sid]['answer']=keys[task_id]['explanation']
        task_id='task-'+lecture_id+'-'+prefix+'-test-matching'
        pairs=[*unit['terms'],('Исходные данные примера',unit['worked'][0]),('Обоснованный результат примера',unit['worked'][1])]
        matching_options=shuffled_options(task_id,[d for t,d in pairs])
        for option in matching_options:option['id']=option['id'].replace('o','d')
        sid=add(prefix+'-test-matching','test','Соотнесите понятия, данные и результат',task={'id':task_id,'type':'matching','prompt':'Сопоставьте понятия с их признаками, а вход и результат — с соответствующими фактами исходного примера.','items':[{'id':f't{i}','text':t} for i,(t,d) in enumerate(pairs)],'options':matching_options},speech='Сопоставьте понятия по смыслу, а не по длине формулировки или расположению. Затем различите входное условие и полученный результат. После ответа поясните, почему признаки не взаимозаменяемы.',kicker=f'Самопроверка · вопрос {q} · 4 из 4')
        keys[task_id]={'type':'matching','pairs':{f't{i}':f'd{i}' for i in range(len(pairs))},'explanation':'\n'.join(f'{t} — {d}' for t,d in pairs)};notes[sid]['answer']=keys[task_id]['explanation']
    solution_id=lecture_id+'-integrated-solution'
    sid=add('integrated-practice','example','Практическая задача по теме',lesson['task'],speech='Это самостоятельное применение материала всей темы. '+lesson['task']+' Сначала зафиксируйте решение и наблюдаемый результат, затем сверьте его с ограничениями. '+lesson['boundary']+' Разбор открывайте после попытки.',practice={'solutionId':solution_id},kicker='Самостоятельная работа')
    notes[sid]['answer']=lesson['answer'];notes[sid]['estimatedSeconds']=360
    integrated_solutions[solution_id]=lesson['answer']
    add('final','questions','Вопросы и итоговое обсуждение',lesson['goal'],bullets=[u['title'] for u in units],speech='Вернитесь к предварительному прогнозу. Сопоставьте его с изученными определениями, наблюдениями и результатами практики. '+lesson['boundary']+' Обсудите, при изменении каких условий первоначальный вывод перестанет быть верным.')
    course['lectures'].append({'id':lecture_id,'title':lesson['title'],'sourceTitle':lesson['title'],'semester':lesson['semester'],'question':'; '.join(u['title'] for u in units),'slides':slides})
course['glossary']=glossary
write(root/'public/course.json',course)
write(root/'public/teacher-pack.json',{'schemaVersion':1,'courseId':'rkis','contentVersion':course['contentVersion'],'notes':notes})
write(root/'public/assessment.json',{'courseId':'rkis','contentVersion':course['contentVersion'],'keys':keys})
write(root/'public/workbenches.json',models)
old_explanations=dict(integrated_solutions)
old_explanations.update({mid:spec['scenarios'][1]['review'] for mid,spec in models.items()})
write(root/'public/explanations.json',old_explanations)
write(root/'authoring/detailed-coverage.json',{'reference':'2026-OKFKS-lecture@e36d019','detailedLectures':list(QUESTIONS),'missingLectures':sorted(missing),'lectures':[{'id':l['id'],'slides':len(l['slides']),'questions':len(QUESTIONS.get(l['id'],[])),'tasks':sum(bool(s.get('task')) for s in l['slides'])} for l in course['lectures']]})
if args.brainm:
    if missing:raise SystemExit('Teacher export requires all detailed lectures')
    from export_teacher import export
    export(root,args.brainm)
print(json.dumps({'detailedLectures':len(QUESTIONS),'totalLectures':len(course['lectures']),'slides':sum(len(l['slides']) for l in course['lectures']),'workbenches':len(models),'tests':len(keys),'missing':len(missing)},ensure_ascii=False))
