using System.ComponentModel;
using System.Runtime.CompilerServices;

namespace Rkis.Core;

public sealed class Product : INotifyPropertyChanged
{
    private string name;
    private decimal price;
    public int Id { get; }
    public int Version { get; }
    public string Name
    {
        get => name;
        set
        {
            if (string.IsNullOrWhiteSpace(value))
                throw new ArgumentException("Название обязательно");
            if (name == value) return;
            name = value;
            Changed();
        }
    }
    public decimal Price
    {
        get => price;
        set
        {
            if (value < 0m) throw new ArgumentOutOfRangeException(nameof(value), "Цена не может быть отрицательной");
            if (price == value) return;
            price = value;
            Changed();
        }
    }
    public Product(int id, string name, decimal price, int version = 1)
    {
        if (id <= 0) throw new ArgumentOutOfRangeException(nameof(id));
        if (string.IsNullOrWhiteSpace(name)) throw new ArgumentException("Название обязательно");
        if (price < 0m) throw new ArgumentOutOfRangeException(nameof(price));
        Id = id; this.name = name; this.price = price; Version = version;
    }
    public event PropertyChangedEventHandler? PropertyChanged;
    private void Changed([CallerMemberName] string? member = null)
        => PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(member));
}

public sealed record OrderLine
{
    public int ProductId { get; }
    public int Quantity { get; }
    public decimal UnitPrice { get; }
    public decimal Total => Quantity * UnitPrice;
    public OrderLine(int productId, int quantity, decimal unitPrice)
    {
        if (productId <= 0 || quantity <= 0 || unitPrice < 0)
            throw new ArgumentOutOfRangeException(nameof(quantity), "Проверьте товар, количество и цену");
        ProductId = productId; Quantity = quantity; UnitPrice = unitPrice;
    }
}

public enum OrderState { Draft, Confirmed, Cancelled }
public sealed class Order
{
    private readonly List<OrderLine> lines = [];
    public IReadOnlyList<OrderLine> Lines => lines.AsReadOnly();
    public OrderState State { get; private set; } = OrderState.Draft;
    public void AddLine(OrderLine line)
    {
        ArgumentNullException.ThrowIfNull(line);
        if (State != OrderState.Draft) throw new InvalidOperationException("Изменяется только черновик");
        lines.Add(line);
    }
    public decimal Calculate(decimal discountPercent)
    {
        if (discountPercent < 0 || discountPercent > 100) throw new ArgumentOutOfRangeException(nameof(discountPercent));
        return Math.Round(lines.Sum(x => x.Total) * (1m - discountPercent / 100m), 2, MidpointRounding.AwayFromZero);
    }
    public void Confirm()
    {
        if (State != OrderState.Draft || lines.Count == 0)
            throw new InvalidOperationException("Подтверждается только непустой черновик");
        State = OrderState.Confirmed;
    }
    public void Cancel()
    {
        if (State == OrderState.Cancelled) throw new InvalidOperationException("Заказ уже отменён");
        State = OrderState.Cancelled;
    }
}

public interface IProductRepository
{
    Task<IReadOnlyList<Product>> ReadAsync(CancellationToken ct);
    Task<bool> RenameAsync(int id, int expectedVersion, string name, CancellationToken ct);
}
