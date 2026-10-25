"""Scenario-specific visual semantics; no arbitrary inference from answer strings."""

def refine(identity,q,model):
    key=(identity,q)
    branches={
      ('s05-01-dotnet',3):('no','yes'),
      ('s05-06-invariants',2):('yes','no'),
      ('s05-13-batch',3):('yes','no'),
      ('s06-06-administration',2):('yes','no'),
      ('s07-04-validation',4):('yes','no'),
    }
    actions={
      ('s05-01-dotnet',3):('Продолжить сборку','Сообщить об ошибке компиляции'),
      ('s05-06-invariants',1):('Создать допустимый объект','Отклонить создание'),
      ('s05-14-connections',4):('Перейти к операции чтения','Уточнить причину отказа'),
      ('s05-18-editing',1):('Проверить предметное ограничение','Указать ошибку формата'),
      ('s05-18-editing',2):('Применить значение','Сохранить прежнее значение'),
      ('s05-19-navigation',4):('Обновить выбранную запись','Отбросить устаревший ответ'),
      ('s06-01-passwords',3):('Продолжить проверки входа','Отклонить учётные данные'),
      ('s06-02-login',1):('Начать проверку учётных данных','Указать обязательные поля'),
      ('s06-03-roles',1):('Разрешить запрос операции','Отказать в операции'),
      ('s06-03-roles',2):('Выполнить общую операцию','Отказать до изменения'),
      ('s06-03-roles',3):('Применить к допустимому ресурсу','Отклонить доступ к ресурсу'),
      ('s06-04-lockout',2):('Сохранить ограничение входа','Продолжить проверку пароля'),
      ('s06-05-images',4):('Принять собранное поле','Продолжить сборку'),
      ('s06-06-administration',2):('Создать учётную запись','Вернуть причину отказа'),
      ('s07-01-files',4):('Заменить целевой файл','Сохранить прежний файл'),
      ('s07-02-json',3):('Принять документ целиком','Вернуть ошибки документа'),
      ('s07-03-http',2):('Проверить код статуса','Обработать транспортный отказ'),
      ('s07-03-http',3):('Прочитать и проверить DTO','Сообщить о нарушении контракта'),
      ('s07-03-http',4):('Обновить результаты','Игнорировать устаревший ответ'),
      ('s07-04-validation',1):('Продолжить проверку строки','Добавить предметную ошибку'),
      ('s07-04-validation',4):('Применить весь документ','Не применять документ'),
      ('s07-05-docx',2):('Заполнить область','Отклонить неподдерживаемый шаблон'),
    }
    if key in actions:model['yes'],model['no']=actions[key]
    if key==('s07-03-http',2):model['condition']='HTTP-ответ получен?'
    if key in [('s05-06-invariants',4),('s05-07-collections',4)]:model['mode']='table'
    if key in branches:
        for scenario,branch in zip(model['scenarios'],branches[key]):
            for frame in scenario['frames'][2:]:frame['branch']=branch
    # This question concerns compilation and a later runtime failure, not console output.
    if key==('s05-04-diagnostics',2):
        model['code']='// Компиляция отклонит несовместимые типы:\n// int count = "3";\n// После исправления исходников отказы БД\n// обрабатывают в слое доступа к данным.'
        for scenario in model['scenarios']:
            for frame in scenario['frames']:frame.pop('console',None)
    if key in [('s05-02-csharp',4),('s05-05-model',4)]:
        model['scenarios'][0]['frames'][-1]['console']=['376.50']
        if identity=='s05-05-model':model['scenarios'][1]['frames'][-1]['console']=['376.50']
    if key==('s05-10-money',1):
        for scenario,value in zip(model['scenarios'],['1800.00','900.00']):scenario['frames'][-1]['console']=[value]
    if key==('s05-10-money',2):
        for scenario,value in zip(model['scenarios'],['900.0','950.00']):scenario['frames'][-1]['console']=[value]
    if key==('s05-03-types',2):
        scenario=model['scenarios'][1]
        for index,frame in enumerate(scenario['frames']):
            frame['links']=[{'name':'orders','target':'List A'},{'name':'copy','target':'List B'}]
            frame['objects']=[{'id':'List A','fields':{'Count':'2','Элементы':'Order 7, Order 8'}},{'id':'List B','fields':{'Count':'2' if index<2 else '0','Элементы':'Order 7, Order 8' if index<2 else '—'}}]
    if key==('s05-05-model',1):
        model['mode']='objects'
        for scenario,product in zip(model['scenarios'],['7','8']):
            for index,frame in enumerate(scenario['frames']):
                frame['links']=[{'name':'selected','target':'Product '+product}]
                fields={'Id':product}
                if product=='7':fields['Name']='Блокнот' if index<2 else 'Альбом'
                else:fields['Строка таблицы']='2' if index<2 else '1'
                frame['objects']=[{'id':'Product '+product,'fields':fields}]
    if key==('s05-05-model',3):
        model['mode']='objects'
        for scenario,count in zip(model['scenarios'],[2,3]):
            for index,frame in enumerate(scenario['frames']):
                n=2 if index<2 else count
                frame['links']=[{'name':'order.Lines','target':'Позиции заказа'}]
                frame['objects']=[{'id':'Позиции заказа','fields':{'Count':str(n),'Товары':'7, 8' if n==2 else '7, 8, 9','Количество товара 7':'3','Количество товара 8':'2'}}]
    if identity=='s06-05-images' and q in [2,3,4]:
        model['mode']='tiles'
        before_after={2:[([1,0,2,3],[1,0,2,3]),([0,1,2,2],[0,1,2,2])],3:[([1,0,2,3],[0,1,2,3]),([2,1,0,3],[0,1,2,3])],4:[([0,1,2,3],[0,1,2,3]),([],[])]}
        for scenario,(before,after) in zip(model['scenarios'],before_after[q]):
            for index,frame in enumerate(scenario['frames']):frame['tiles']=before if index<2 else after
    return model
