using Rkis.Core;
using System.Text.Json;
using System.Text.RegularExpressions;
using Rkis.Adapters;
using Microsoft.AspNetCore.Identity;

static void Equal<T>(T expected, T actual)
{
    if (!EqualityComparer<T>.Default.Equals(expected, actual))
        throw new Exception($"Ожидалось {expected}; получено {actual}");
}
static void Reject(Action action)
{
    try { action(); } catch (ArgumentException) { return; } catch (InvalidOperationException) { return; }
    throw new Exception("Ожидался отказ");
}
var order = new Order();
Reject(order.Confirm);
order.AddLine(new OrderLine(7, 3, 125.50m));
order.AddLine(new OrderLine(8, 2, 80m));
Equal(482.85m, order.Calculate(10m));
Equal(509.68m, order.Calculate(5m));
order.Confirm();
Reject(order.Confirm);
order.Cancel();
Reject(order.Confirm);
Equal(OrderState.Cancelled, order.State);
var product = new Product(7, "Блокнот", 125.50m);
Reject(() => product.Price = -1m);
Equal(125.50m, product.Price);
string? changed = null;
product.PropertyChanged += (_, e) => changed = e.PropertyName;
product.Name = "Альбом";
Equal("Name", changed);
var a = new List<int> { 10 }; var b = a; b.Add(20); Equal(2, a.Count);
var stock = new List<int> { 0, 2, 5 }; var query = stock.Where(x => x > 0).OrderBy(x => x);
stock.Add(3); Equal("2,3,5", string.Join(',', query));
int[] puzzle = [1, 0, 2, 3]; (puzzle[0], puzzle[1]) = (puzzle[1], puzzle[0]);
Equal(true, puzzle.Select((id, pos) => id == pos).All(x => x));
Equal(true, Regex.IsMatch("AB-0042", @"\A[A-Z]{2}-[0-9]{4}\z", RegexOptions.CultureInvariant, TimeSpan.FromMilliseconds(100)));
Equal(false, Regex.IsMatch("ab-0042", @"\A[A-Z]{2}-[0-9]{4}\z", RegexOptions.CultureInvariant, TimeSpan.FromMilliseconds(100)));
var json = JsonSerializer.Serialize(new[] { new { Id = 7, Name = "Блокнот", Price = 125.5m } });
using var document = JsonDocument.Parse(json);
Equal(125.5m, document.RootElement[0].GetProperty("Price").GetDecimal());
var user = new User(1, "learner");
string hash1 = Passwords.Create(user, "учебная-проверка-42");
string hash2 = Passwords.Create(user, "учебная-проверка-42");
Equal(false, hash1 == hash2);
Equal(true, Passwords.Verify(user, hash1, "учебная-проверка-42") != PasswordVerificationResult.Failed);
Equal(PasswordVerificationResult.Failed, Passwords.Verify(user, hash1, "ошибка"));
var until = new DateTimeOffset(2026, 10, 25, 10, 5, 0, TimeSpan.Zero);
Equal(true, Passwords.IsLocked(until.AddSeconds(-1), until));
Equal(false, Passwords.IsLocked(until, until));
Console.WriteLine("Проверены расчёты, переходы, инварианты, уведомления, LINQ, пазл, Regex, JSON, парольный хеш и граница блокировки.");
