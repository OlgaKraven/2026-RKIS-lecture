var builder = WebApplication.CreateBuilder(args);
builder.WebHost.UseUrls("http://127.0.0.1:5080");
var app = builder.Build();
app.MapGet("/products", () => Results.Json(new[] {
    new { Id = 7, Name = "Блокнот", Price = 125.50m },
    new { Id = 8, Name = "Ручка", Price = 80m }
}, new System.Text.Json.JsonSerializerOptions { PropertyNamingPolicy = null }));
app.MapGet("/unavailable", () => Results.StatusCode(503));
app.MapGet("/wrong-content", () => Results.Content("<p>Вход</p>", "text/html"));
app.Run();
