# Источники и перенос

Структура и часы — пользовательская программа МДК.05.02 от 25.10.2026, исходник сохранён в BrainM. Папка материалов: https://disk.yandex.ru/d/S7PWVBaKBr2ECg. При проверке 25.10.2026 открытый API вернул пустой каталог (total=0).

Все девять уникальных изданий из пользовательского списка сохранены в библиографии курса. Повтор Цехановского и Водяхо объединён. Некорректная по длине запись ISBN `978-5-93026-166-10` для пособия АГАСУ сохранена как замечание здесь и не воспроизводится как подтверждённый ISBN. Страницы и цитаты из закрытых полных текстов не приписываются: авторизация IPR отсутствует. Доступные карточки дают библиографию и аннотации. Издания по редуктору, инженерной графике и сетям доступа не используются как основания для синтаксиса C# и парольных алгоритмов. Котова/Скидан рассматривают C++, поэтому используются как контекст базовых алгоритмов, а не источник особенностей C#.

## Проверка технических уточнений

- Microsoft Desktop: https://learn.microsoft.com/en-us/dotnet/desktop/
- Типы значений C#: https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/value-types
- Привязка WPF: https://learn.microsoft.com/en-us/dotnet/desktop/wpf/data/data-binding-overview
- PasswordHasher: https://learn.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.identity.passwordhasher-1.verifyhashedpassword
- Npgsql: https://www.npgsql.org/doc/basic-usage.html
- MySqlConnector: https://mysqlconnector.net/ и https://mysqlconnector.net/api/mysqlconnector/mysqlcommandtype/
- XAMPP / MariaDB: https://www.apachefriends.org/faq_windows.html
- Open XML SDK: https://learn.microsoft.com/en-us/office/open-xml/word/structure-of-a-wordprocessingml-document

Это технические первичные справочники, а не замена заданного списка учебной литературы. Официальный действующий комплект критериев демонстрационного экзамена не предоставлен; точные баллы и лимиты не выдумываются.

## Дизайн и движок

Дизайн каталога и презентации — закреплённые ресурсы генератора BrainM, Raleway и фирменные логотипы. Новый маскот создан по эталонам lecture-rhino; подлинный логотип используется отдельно. Код движка перенесён из репозитория OlgaKraven/2026-lecture-shablone (MIT), локальная исходная редакция закреплена в `engine-origin.json`. Изменения курса: кодовые блоки, самостоятельные случаи с явным показом разбора, загрузка авторских заметок, оформление каталога и слайдов.

Проверка lock-файла BrainM обнаружила три поздних уточнения в правилах. Причина установлена по истории коммитов 8355739 и da61200: уточнялись проверки речи, самостоятельных задач и инфографики. Использованы актуальные проверенные инструкции без автоматической перезаписи lock. Точные отпечатки использованных инструкций находятся в `engine-origin.json`.

Дополнительная сверка: [HashSet.Add](https://learn.microsoft.com/dotnet/api/system.collections.generic.hashset-1.add), [якоря Regex](https://learn.microsoft.com/en-us/dotnet/standard/base-types/anchors-in-regular-expressions).

Актуальный источник каталога ОКФКС — e36d019; точные отпечатки и адаптация указаны в `catalog-origin.json`.
