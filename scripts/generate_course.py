from pathlib import Path
import argparse, hashlib, json, re

parser=argparse.ArgumentParser()
parser.add_argument('--brainm',type=Path,help='Optional BrainM Git root for teacher Markdown; never part of the public build')
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
def read(path): return json.loads((root/path).read_text(encoding='utf-8'))
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
literature=read('authoring/literature.json')
supplements=read('authoring/supplements.json')
lessons=[]
for semester in [5,6,7]:
    for lesson in read(f'authoring/semester-{semester}.json'):
        lesson['semester']=semester
        lessons.append(lesson)
course={'schemaVersion':1,'contentVersion':'rkis-2026-10-25-2','id':'rkis','code':'МДК.05.02',
    'discipline':'Разработка кода информационных систем','year':'2026–2027',
    'heroTitle':'Разработка кода','heroAccent':'информационных систем','slogan':'От предметной модели к работающему приложению.',
    'mascot':'brand/rhino-rkis.png','mascotAlt':'Носорог разрабатывает приложение на C#',
    'logo':'brand/synergy-wordmark.jpg','mark':'brand/synergy-mark.png','ornament':'brand/side-ornament.png',
    'font':'fonts/raleway-cyrillic.woff2','topicArrow':'brand/topic-arrow.webp',
    'materialsUrl':'https://disk.yandex.ru/d/S7PWVBaKBr2ECg','demo':False,'semesters':[5,6,7],
    'literature':{g:[{'citation':v['citation'],'url':v['url']} for v in literature.values() if v['group']==g] for g in ['primary','additional']},
    'lectures':[]}
notes={}
prose={}
def visual(l):
    items=[{'title':t,'text':v} for t,v in l['steps']]
    if l['id'] in ['s05-03-types','s05-12-rules','s05-17-binding','s06-03-roles','s06-07-interface']:
        return {'type':'comparison','columns':['Условие или уровень','Смысл и наблюдение'],'rows':l['steps'],'caption':'Сопоставьте основание и наблюдение; строки таблицы не означают течение времени.'}
    if l['id']=='s05-09-business':
        return {'type':'layers','items':items,'caption':'Слои разделяют ответственность; порядок блоков не является временем выполнения.'}
    return {'type':'process','items':items,'caption':'Учебный разбор: исходное состояние, операция, проверка и наблюдаемый результат.'}

for l in lessons:
    slides=[]; texts={}
    def add(suffix,kind,title,script,body='',**extra):
        slide={'id':l['id']+'-'+suffix,'kind':kind,'title':title,'kicker':('Вопрос 1' if suffix=='question' else 'МДК.05.02'),**extra}
        if body: slide['body']=body
        slides.append(slide)
        is_task=suffix=='transfer'
        notes[slide['id']]={'script':script,'preparation':('Общая среда примеров — .NET 10 / C#. Интерфейсы: Windows Forms и WPF. MySQL/MariaDB через MySqlConnector, PostgreSQL через Npgsql. Код на слайдах может быть явно обозначенным фрагментом; перед живым показом подготовьте его окружение.' if suffix=='title' else ''),
          'notebook':extra.get('notebook',''),'questions':l['task'] if is_task else '',
          'answer':l['answer'] if is_task else '',
          'estimatedSeconds':max(30,round(len(script.split())/110*60))+(240 if is_task else 0)}
        texts[slide['id']]=script
    add('title','title',l['title'],l['goal']+' Сегодня последовательно свяжем понятия с конкретным поведением приложения. Сквозной учебный пример — система заказов: товар, позиция и документ.', 'МДК.05.02 · '+str(l['semester'])+' семестр')
    add('question','section',l['questions'][0], 'Начнём с вопроса: '+l['questions'][0]+' '+l['definition'],l['goal'])
    add('definition','notebook','Ключевое понятие', l['definition']+' Обратите внимание на отличие: '+l['questions'][1]+' Вернёмся к этому различию в разборе конкретных значений.',notebook=l['definition'])
    # Keep prose readable and preserve its order instead of shrinking a dense slide.
    sentences=re.split(r'(?<=[.!?])\s+(?=[А-ЯA-Z0-9])',l['explain'])
    groups=[]; chunk=[]; chars=0
    for sentence in sentences:
        if chars+len(sentence)>430 and chunk:
            groups.append(' '.join(chunk));chunk=[];chars=0
        chunk.append(sentence);chars+=len(sentence)
    if chunk:groups.append(' '.join(chunk))
    for i,paragraph in enumerate(groups):
        title=l['questions'][min(i,len(l['questions'])-1)]
        add(f'explain-{i+1}','theory',title,paragraph,paragraph)
    add('mechanism','process','Разбор механизма', '\n\n'.join(f'{t}. {v}' for t,v in l['steps'])+'\n\n'+l['result'],visual=visual(l))
    lines=l['code'].splitlines()
    # Continuations keep actual code order, no elided executable statements.
    codechunks=[lines[i:i+10] for i in range(0,len(lines),10)]
    for i,chunk in enumerate(codechunks):
        suffix=f'code-{i+1}'
        title='Пример кода' if len(codechunks)==1 else f'Пример кода · {i+1}'
        add(suffix,'example',title,l['codeCaption']+'\n\n'+l['result'] if i==len(codechunks)-1 else l['codeCaption']+' Фрагмент продолжается на следующем экране; граница слайда не завершает конструкцию.',l['codeCaption'],code='\n'.join(chunk),codeLanguage='sql' if l['code'].startswith('UPDATE') else 'csharp')
    add('result','example','Наблюдение и вывод',l['result']+' Сопоставьте наблюдение с исходным состоянием: '+l['steps'][0][1]+' Изменение вызвано описанной операцией, поэтому при других входных данных результат требуется проверить заново.',l['result'])
    add('boundary','warning','Граница применимости',l['boundary'],l['boundary'])
    for index,supplement in enumerate(supplements.get(l['id'],[]),1):
        supplement_lines=supplement['code'].splitlines()
        for part,offset in enumerate(range(0,len(supplement_lines),10),1):
            add(f'supplement-{index}-{part}','example',supplement['title'],supplement['speech'],supplement['body'],code='\n'.join(supplement_lines[offset:offset+10]),codeLanguage='csharp')
    add('transfer','questions','Проверьте изменённый случай','Условие: '+l['task']+'\n\nПауза: дайте группе сначала сформулировать самостоятельное решение. Обсудите входные условия, действие и ожидаемое наблюдение. После попытки откройте разбор отдельной командой; до этого не читайте ключ вслух.',l['task'],practice={'solutionId':l['id']+'-transfer'})
    add('summary','summary','Что позволяет объяснить модель',l['goal']+' '+l['result'],bullets=[l['goal'],l['result']])
    selected=[literature[x] for x in l['reading']]
    for group,title in [('primary','Основная литература'),('additional','Дополнительная литература')]:
        refs=[{'citation':v['citation'],'url':v['url']} for v in selected if v['group']==group]
        if refs:
            add('reading-'+group,'literature',title,'Для самостоятельного чтения используйте перечисленные издания по теме. Сопоставляйте изученное правило с примером приложения; синтаксис конкретного API уточняется по документации его версии.',references=refs,readingGroup=group)
    add('materials','materials','Материалы','Откройте папку материалов по ссылке или QR-коду. Вернитесь к условию изменённого случая и объясните результат своими словами.')
    course['lectures'].append({'id':l['id'],'title':l['title'],'sourceTitle':l['title'],'semester':l['semester'],'question':' '.join(l['questions']),'slides':slides})
    prose[l['id']]=texts

write(root/'public/course.json',course)
pack={'schemaVersion':1,'courseId':course['id'],'contentVersion':course['contentVersion'],'notes':notes}
write(root/'public/teacher-pack.json',pack)
write(root/'public/explanations.json',{l['id']+'-transfer':l['answer'] for l in lessons})
write(root/'authoring/curriculum-map.json',{'courseId':'rkis','hours':{'5':38,'6':14,'7':10},'lectures':[{'lectureId':l['id'],'semester':l['semester'],'academicHours':2,'title':l['title'],'outcome':l['goal'],'slideIds':[s['id'] for s in c['slides']]} for l,c in zip(lessons,course['lectures'])]})

site='https://olgakraven.github.io/2026-RKIS-lecture/'
readme=['# Разработка кода информационных систем','']
for semester in [5,6,7]:
    readme.extend([f'## {semester} семестр',''])
    for l in lessons:
        if l['semester']==semester:readme.append(f'- [{l["title"]}]({site}?lecture={l["id"]}&slide={l["id"]}-title)')
    readme.append('')
(root/'README.md').write_text('\n'.join(readme),encoding='utf-8')

if args.brainm:
    folder=args.brainm/'BrainM/Проекты/Разработка кода информационных систем'
    sha=hashlib.sha256((root/'public/course.json').read_bytes()).hexdigest()
    for l,c in zip(lessons,course['lectures']):
        target=folder/'Тексты преподавателя'/l['id'];target.mkdir(parents=True,exist_ok=True)
        metadata=f'---\ncourseId: rkis\nlectureId: {l["id"]}\ncontentVersion: {course["contentVersion"]}\nsourceKind: local\nsourceSha256: {sha}\n---\n\n# {l["title"]}\n\n'
        teacher=[metadata];presenter=[metadata];alignment=[]
        for number,s in enumerate(c['slides'],1):
            anchor=s['id'];n=notes[anchor]
            teacher.append(f'<a id="{anchor}"></a>\n\n## {number}. {s["title"]}\n\n'+prose[l['id']][anchor]+'\n')
            presenter.append(f'<a id="{anchor}"></a>\n\n## {number}. {s["title"]} · {anchor}\n\n'+n['script']+'\n')
            if s.get('code'):
                teacher.append('```'+s['codeLanguage']+'\n'+s['code']+'\n```\n')
                presenter.append('Показ: сопоставьте каждую строку с исходными данными и результатом.\n\n```'+s['codeLanguage']+'\n'+s['code']+'\n```\n')
            if n['answer']:
                teacher.append('### Разбор после самостоятельной попытки\n\n'+n['answer']+'\n')
                presenter.append('### Ожидаемый ответ и обсуждение после попытки\n\n'+n['answer']+'\n')
            alignment.append({'lectureId':l['id'],'slideId':anchor,'displayNumber':number,'title':s['title'],'anchors':{'teacher':anchor,'presenter':anchor}})
        (target/'lecture.teacher.md').write_text('\n'.join(teacher),encoding='utf-8')
        (target/'lecture.presenter.md').write_text('\n'.join(presenter),encoding='utf-8')
        write(target/'alignment.json',{'schemaVersion':1,'courseId':'rkis','contentVersion':course['contentVersion'],'sourceKind':'local','sourceSha256':sha,'lectureIds':[l['id']],'documents':{'teacher':'lecture.teacher.md','presenter':'lecture.presenter.md'},'slides':alignment})
        write(target/'teacher-pack.json',{'schemaVersion':1,'courseId':'rkis','contentVersion':course['contentVersion'],'notes':{s['id']:notes[s['id']] for s in c['slides']}})
    for semester in [5,6,7]:
        plan=[f'# {semester} семестр\n']
        for l in lessons:
            if l['semester']!=semester:continue
            plan.extend([f'## {l["title"]}\n',f'**Результат:** {l["goal"]}\n','**Вопросы:** '+ '; '.join(l['questions'])+'\n',l['explain']+'\n','**Ход разбора:**\n']+[f'{i}. {t}. {v}' for i,(t,v) in enumerate(l['steps'],1)]+['\n**Пример:**\n\n```\n'+l['code']+'\n```\n',l['codeCaption']+'\n',l['result']+'\n','**Самостоятельная попытка:** '+l['task']+'\n','**Разбор после попытки:** '+l['answer']+'\n','**Граница:** '+l['boundary']+'\n',f'[[Проекты/Разработка кода информационных систем/Тексты преподавателя/{l["id"]}/lecture.presenter|Сценарий по слайдам]]\n'])
        (folder/f'Сценарии — {semester} семестр.md').write_text('\n'.join(plan),encoding='utf-8')
print(json.dumps({'lectures':len(lessons),'slides':sum(len(l['slides']) for l in course['lectures']),'notes':len(notes)},ensure_ascii=False))
