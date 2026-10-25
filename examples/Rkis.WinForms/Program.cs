using System.ComponentModel;
using Rkis.Core;

ApplicationConfiguration.Initialize();
Application.Run(new ProductsForm());

sealed class ProductsForm : Form
{
    private readonly BindingList<Product> products = new([new Product(7, "Блокнот", 125.50m), new Product(8, "Ручка", 80m)]);
    private readonly BindingSource source = new();
    public ProductsForm()
    {
        Text = "Товары · Windows Forms"; Width = 820; Height = 500;
        var grid = new DataGridView { Dock = DockStyle.Fill, AutoGenerateColumns = true, AllowUserToAddRows = false };
        source.DataSource = products; grid.DataSource = source;
        grid.DataError += (_, e) => { e.ThrowException = false; MessageBox.Show(this, "Проверьте название и неотрицательную цену"); };
        var button = new Button { Text = "Изменить название первого товара", Dock = DockStyle.Bottom, Height = 48 };
        button.Click += (_, _) => products[0].Name = products[0].Name == "Блокнот" ? "Альбом" : "Блокнот";
        Controls.Add(grid); Controls.Add(button);
    }
    protected override void Dispose(bool disposing)
    {
        if (disposing) source.Dispose();
        base.Dispose(disposing);
    }
}
