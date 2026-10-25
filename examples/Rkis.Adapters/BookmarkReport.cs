using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Wordprocessing;

namespace Rkis.Adapters;

// Deliberately narrow template contract: a bookmark range is in one paragraph,
// its boundaries are direct children, and it contains no nested bookmarks.
public static class BookmarkReport
{
    public static void Fill(string template, string output, string bookmarkName, string value)
    {
        if (Path.GetFullPath(template) == Path.GetFullPath(output))
            throw new ArgumentException("Результат должен отличаться от шаблона");
        // Validate the source before creating or modifying an output document.
        using (var source = WordprocessingDocument.Open(template, false))
            _ = Range(source, bookmarkName);
        File.Copy(template, output, overwrite: false);
        using var doc = WordprocessingDocument.Open(output, true);
        var (start, end) = Range(doc, bookmarkName);
        var item = start.NextSibling();
        while (item is not null && item != end)
        {
            var next = item.NextSibling();
            item.Remove(); item = next;
        }
        start.InsertAfterSelf(new Run(new Text(value) { Space = SpaceProcessingModeValues.Preserve }));
        (doc.MainDocumentPart?.Document ?? throw new InvalidDataException("Нет основной части документа")).Save();
    }

    private static (BookmarkStart, BookmarkEnd) Range(WordprocessingDocument doc, string name)
    {
        var body = doc.MainDocumentPart?.Document?.Body ?? throw new InvalidDataException("Нет тела документа");
        var starts = body.Descendants<BookmarkStart>().Where(x => x.Name?.Value == name).ToArray();
        if (starts.Length != 1) throw new InvalidDataException($"Ожидалась одна закладка {name}");
        var start = starts[0];
        var ends = body.Descendants<BookmarkEnd>().Where(x => x.Id?.Value == start.Id?.Value).ToArray();
        if (ends.Length != 1 || start.Parent is not Paragraph || ends[0].Parent != start.Parent)
            throw new InvalidDataException("Диапазон закладки должен лежать в одном абзаце");
        var siblings = start.Parent.ChildElements.ToArray();
        int first = Array.IndexOf(siblings, start), last = Array.IndexOf(siblings, ends[0]);
        if (last <= first || siblings.Skip(first + 1).Take(last - first - 1).Any(x => x is BookmarkStart or BookmarkEnd || x.Descendants<BookmarkStart>().Any() || x.Descendants<BookmarkEnd>().Any()))
            throw new InvalidDataException("Неверный или вложенный диапазон закладки");
        return (start, ends[0]);
    }
}
