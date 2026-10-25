"""Export the authored course to the explicitly selected teacher workspace."""
from pathlib import Path
import hashlib,json,sys

def export(root,workspace):
    course=json.loads((root/'public/course.json').read_text(encoding='utf-8'))
    notes=json.loads((root/'public/teacher-pack.json').read_text(encoding='utf-8'))['notes']
    folder=workspace/'BrainM/Проекты/Разработка кода информационных систем'
    sha=hashlib.sha256((root/'public/course.json').read_bytes()).hexdigest()
    models=json.loads((root/'public/workbenches.json').read_text(encoding='utf-8'))
    def write(path,value):path.write_bytes((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    for lecture in course['lectures']:
        target=folder/'Тексты преподавателя'/lecture['id'];target.mkdir(parents=True,exist_ok=True)
        metadata=f'---\ncourseId: rkis\nlectureId: {lecture["id"]}\ncontentVersion: {course["contentVersion"]}\nsourceKind: local\nsourceSha256: {sha}\n---\n\n# {lecture["title"]}\n'
        teacher=[metadata];presenter=[metadata];alignment=[]
        for number,slide in enumerate(lecture['slides'],1):
            sid=slide['id'];note=notes[sid]
            heading=f'<a id="{sid}"></a>\n\n## {number}. {slide["title"]}\n\n'
            teacher.append(heading+note['script']+'\n');presenter.append(heading+note['script']+'\n')
            if slide.get('notebook'):
                teacher.append('Запишите: '+slide['notebook']+'\n');presenter.append('Запишите: '+slide['notebook']+'\n')
            if slide.get('code'):
                for document in [teacher,presenter]:document.append('```'+slide['codeLanguage']+'\n'+slide['code']+'\n```\n')
            if slide.get('learning'):
                model=models[slide['learning']['id']]
                for document in [teacher,presenter]:
                    for scenario in model['scenarios']:
                        document.append('### '+scenario['title']+'\n\n'+scenario['given']+'\n\n'+ '\n\n'.join(f'{i}. {frame["label"]} Состояние: '+ '; '.join(f'{k}={v}' for k,v in frame['variables'].items()) for i,frame in enumerate(scenario['frames'],1))+'\n\n'+scenario['review']+'\n')
            if slide.get('task'):
                task=slide['task']
                for document in [teacher,presenter]:
                    document.append('Условие: '+task['prompt']+'\n')
                    if task.get('items'):
                        document.append('Понятия и категории для сопоставления:\n')
                        for item in task['items']:document.append('- '+item['text'])
                        document.append('\nВарианты соответствий:\n')
                    for option in task.get('options',[]):document.append('- '+option['text'])
                    document.append('')
            if note['answer']:
                for document in [teacher,presenter]:document.append('### Разбор после самостоятельной попытки\n\n'+note['answer']+'\n')
            alignment.append({'lectureId':lecture['id'],'slideId':sid,'displayNumber':number,'title':slide['title'],'anchors':{'teacher':sid,'presenter':sid}})
        for name,data in [('lecture.teacher.md',teacher),('lecture.presenter.md',presenter)]:
            (target/name).write_bytes(('\n'.join(data)+'\n').encode('utf-8'))
        write(target/'alignment.json',{'schemaVersion':1,'courseId':'rkis','contentVersion':course['contentVersion'],'sourceKind':'local','sourceSha256':sha,'lectureIds':[lecture['id']],'documents':{'teacher':'lecture.teacher.md','presenter':'lecture.presenter.md'},'slides':alignment})
        write(target/'teacher-pack.json',{'schemaVersion':1,'courseId':'rkis','contentVersion':course['contentVersion'],'notes':{s['id']:notes[s['id']] for s in lecture['slides']}})
    for semester in [5,6,7]:
        plan=[f'# {semester} семестр\n']
        for lecture in course['lectures']:
            if lecture['semester']!=semester:continue
            plan.extend(['## '+lecture['title']+'\n','Вопросы: '+lecture['question']+'\n','Начало: литература, материалы, вопросы, предметная задача и предварительный прогноз.\n','Каждый вопрос: определения, механизм, пошаговый разбор, исходный и изменённый случаи, антиошибка, вывод, практика и четыре формы самопроверки.\n',f'[[Проекты/Разработка кода информационных систем/Тексты преподавателя/{lecture["id"]}/lecture.presenter|Сценарий по слайдам]]\n'])
        (folder/f'Сценарии — {semester} семестр.md').write_bytes(('\n'.join(plan)+'\n').encode('utf-8'))

if __name__=='__main__':export(Path(__file__).resolve().parents[1],Path(sys.argv[1]).resolve())
