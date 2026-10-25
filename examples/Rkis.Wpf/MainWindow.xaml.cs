using System.Collections.ObjectModel;
using System.Windows;
using Rkis.Core;
namespace Rkis.Wpf;
public partial class MainWindow : Window
{
    public ObservableCollection<Product> Products { get; } = [new Product(7,"Блокнот",125.50m),new Product(8,"Ручка",80m)];
    public MainWindow() { InitializeComponent(); DataContext = this; }
    private void Rename(object sender, RoutedEventArgs e)
        => Products[0].Name = Products[0].Name == "Блокнот" ? "Альбом" : "Блокнот";
}
